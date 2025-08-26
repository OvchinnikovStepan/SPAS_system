import pandas as pd
import httpx
import streamlit as st
from typing import Optional
from datetime import datetime, date, time
from dashboard.utils.validate_data import validate_dataframe_structure
from dashboard.utils.validate_datetime_index import validate_datetime_index


def _normalize_source(source: Optional[str]) -> str:
    return (source or "").strip().lower()

def _clean_measurement_tag(tag: Optional[str]) -> str:
    # Тег измерения чувствителен к регистру, поэтому только обрезаем пробелы
    return (tag or "").strip()

def _get_data_url_for_source(source: str) -> str:
    """
    Возвращает полный URL для эндпоинта /data в зависимости от выбранного источника.
    Источники: 'msk' -> API_DATA_MSK_URL, 'oms' -> API_DATA_OMS_URL.
    """
    s = _normalize_source(source)
    if s == "msk":
        base = st.secrets.get("API_DATA_MSK_URL")
        secret_key = "API_DATA_MSK_URL"
    elif s == "oms":
        base = st.secrets.get("API_DATA_OMS_URL")
        secret_key = "API_DATA_OMS_URL"
    else:
        raise ValueError("Поддерживаемые источники: 'msk' или 'oms'.")

    if not base:
        raise RuntimeError(f"Не найден секрет {secret_key}. Проверьте .streamlit/secrets.toml")

    return f"{base.rstrip('/')}/data"


@st.dialog("Параметры запроса данных", width="large")
def api_params_dialog():
    source = st.selectbox("Источник данных", options=["msk", "oms"], index=0, key="api_source_select")
    tag_name = st.text_input("Название тэга")

    use_start = st.checkbox("Указать начало периода", value=False)
    start_date = st.date_input("Начало периода — дата", value=date.today(), disabled=not use_start)
    start_time = st.time_input("Начало периода — время", value=time(0, 0, 0), disabled=not use_start, key="start_time")

    use_end = st.checkbox("Указать конец периода", value=False)
    end_date = st.date_input("Конец периода — дата", value=date.today(), disabled=not use_end)
    end_time = st.time_input("Конец периода — время", value=time(23, 59, 59), disabled=not use_end, key="end_time")

    def assemble_dt(use_flag: bool, d: date, t: time) -> Optional[datetime]:
        return datetime.combine(d, t) if use_flag else None

    def to_iso_or_none(dt: Optional[datetime]) -> Optional[str]:
        return dt.isoformat() if dt else None

    start_dt = assemble_dt(use_start, start_date, start_time)
    end_dt = assemble_dt(use_end, end_date, end_time)

    if st.button("Отправить"):
        st.session_state.api_params = {
            "source": _normalize_source(source),
            "measurement_tag": _clean_measurement_tag(tag_name),
            "dateStart": to_iso_or_none(start_dt),
            "dateEnd": to_iso_or_none(end_dt),
        }
        st.session_state.api_dialog_closed = True
        st.rerun()


def _df_from_api_array(records) -> pd.DataFrame:
    """
    Ожидает массив объектов [{"d": "...", "v": ...}, ...].
    Делает 'd' datetime-индексом (UTC, если есть 'Z'), валидирует.
    """
    if not isinstance(records, list):
        raise ValueError("Ожидался массив JSON-объектов от API.")

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df

    if "d" not in df.columns:
        raise ValueError("В ответе API нет колонки 'd' с датой/временем.")

    df["d"] = pd.to_datetime(df["d"], utc=True, errors="coerce")

    bad_rows = df["d"].isna().sum()
    if bad_rows > 0:
        df = df.dropna(subset=["d"])

    if df.empty:
        return df

    df = df.set_index("d").sort_index()

    validate_dataframe_structure(df, raise_error=True)
    validate_datetime_index(df)

    return df


def upload_data() -> Optional[pd.DataFrame]:
    df = None

    # 1) Локальная загрузка
    uploaded_file = st.file_uploader("Загрузите файл Excel или CSV", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
            else:
                df = pd.read_excel(uploaded_file, index_col=0, parse_dates=True)
            validate_dataframe_structure(df, raise_error=True)
            validate_datetime_index(df)
            st.success("Данные успешно загружены и валидированы!")
            return df
        except Exception as e:
            st.error(f"Ошибка при загрузке данных: {e}")
            return None

    # 2) Запрос к API
    if st.button("Запросить данные с сервера"):
        st.session_state.api_dialog_closed = False
        api_params_dialog()

    if st.session_state.get("api_dialog_closed", False):
        params = st.session_state.get("api_params")
        if params:
            try:
                source = _normalize_source(params.get("source"))
                if source not in {"msk", "oms"}:
                    st.error("Выберите источник ('msk' или 'oms') перед запросом.")
                    return None

                measurement_tag = _clean_measurement_tag(params.get("measurement_tag"))
                if not measurement_tag:
                    st.error("Укажите тэг измерения.")
                    return None

                payload = {"tag": measurement_tag}
                if params.get("dateStart"):
                    payload["dateStart"] = params["dateStart"]
                if params.get("dateEnd"):
                    payload["dateEnd"] = params["dateEnd"]

                data_url = _get_data_url_for_source(source)

                with httpx.Client(timeout=30.0, verify=False) as client:
                    resp = client.get(
                        data_url,
                        params=payload,
                        headers={"Content-Type": "application/json", "accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data_json = resp.json()

                df = _df_from_api_array(data_json)
                st.success("Данные получены с сервера и валидированы!")
                return df

            except httpx.HTTPStatusError as e:
                st.error(f"Ошибка API ({e.response.status_code}): {e.response.text}")
            except httpx.RequestError as e:
                st.error(f"Сетевой сбой при обращении к API: {e}")
            except (ValueError, RuntimeError) as e:
                st.error(f"Ошибка конфигурации/данных: {e}")
            except Exception as e:
                st.error(f"Непредвиденная ошибка при обработке данных: {e}")

    return df

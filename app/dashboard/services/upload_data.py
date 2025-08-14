import pandas as pd
import json
from dashboard.json_df.tag_msk_core import data
import streamlit as st
from typing import Optional
from datetime import date
from dashboard.utils.validate_data import validate_dataframe_structure
from dashboard.utils.validate_datetime_index import validate_datetime_index


@st.dialog("Параметры запроса данных", width="large")
def api_params_dialog():
    tag_name = st.text_input("Название тэга")
    start_date = st.date_input("Начало периода", value=date.today())
    end_date = st.date_input("Конец периода", value=date.today())
    if st.button("Отправить"):
        st.session_state.api_params = {
            "tag": tag_name, "start": start_date, "end": end_date
        }
        st.session_state.api_dialog_closed = True
        st.rerun()

def upload_data() -> Optional[pd.DataFrame]:
    df = None

    # Загрузка из файла
    uploaded_file = st.file_uploader("Загрузите файл Excel или CSV", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
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

    # Кнопка для открытия диалога
    if st.button("Запросить данные с сервера"):
        st.session_state.api_dialog_closed = False
        api_params_dialog()

    # После закрытия диалога — применяем фильтр
    if st.session_state.get("api_dialog_closed", False):
        params = st.session_state.get("api_params")
        if params:
            try:
                # Пока фильтр по датам как заглушка, который задается заранее чем загружается датасет, ведь мы загружаем датасет не по фильтру
                df = pd.DataFrame(data)
                df['d'] = pd.to_datetime(df['d'], format='ISO8601')
                df = df.set_index('d')
                validate_dataframe_structure(df, raise_error=True)
                validate_datetime_index(df)

                mask = (
                    (df.index >= pd.to_datetime(params["start"])) &
                    (df.index <= pd.to_datetime(params["end"]))
                )
                df = df.loc[mask]

                st.success("Данные загружены и отфильтрованы!")
                return df
            except Exception as e:
                st.error(f"Ошибка при обработке данных: {e}")
    return df
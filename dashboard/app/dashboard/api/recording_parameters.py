import streamlit as st
from typing import Dict, Any
from .request_parameters import request_parameters

def _initialize_default_overrides_once() -> None:
    defaults_flag_key = "detector_defaults_initialized"
    if st.session_state.get(defaults_flag_key):
        return
    existing_overrides = st.session_state.get("detector_param_overrides")
    if not isinstance(existing_overrides, dict):
        existing_overrides = {}
    default_overrides: Dict[str, Dict[str, Any]] = {
        "freezing": {"freezing_count": 5, "rel_tol": 1e-9},
        "avalanche": {
            "hi_percent": 0.95,
            "low_percent": 0.05,
            "bound_coef": 5.0,
            "statistic_len": 30,
            "statistic_len_for_mean": 5,
        },
        "outlier": {
            "hi_percent": 0.95,
            "low_percent": 0.05,
            "bound_coef": 3.0,
            "statistic_len": 144,
            "statistic_len_for_mean": 12,
        },
    }
    for detector_name, params in default_overrides.items():
        if detector_name not in existing_overrides or not isinstance(existing_overrides.get(detector_name), dict):
            existing_overrides.setdefault(detector_name, {})
        for param_name, param_value in params.items():
            existing_overrides[detector_name].setdefault(param_name, param_value)
    st.session_state.detector_param_overrides = existing_overrides
    st.session_state[defaults_flag_key] = True

def _get_overridden_params_from_session() -> Dict[str, Dict[str, Any]]:
    overrides = st.session_state.get("detector_param_overrides")
    if isinstance(overrides, dict):
        return overrides
    return {}

_ALLOWED_PARAMS = {
    "freezing": {"freezing_count", "rel_tol"},
    "avalanche": {"hi_percent", "low_percent", "bound_coef", "statistic_len", "statistic_len_for_mean"},
    "outlier": {"hi_percent", "low_percent", "bound_coef", "statistic_len", "statistic_len_for_mean"},
}

def get_detector_parameters() -> Dict[str, Dict[str, Any]]:
    try:
        result = request_parameters()
        if "error" in result:
            st.error(f"Ошибка получения параметров: {result['error']}")
            return {}
        _initialize_default_overrides_once()
        overridden = _get_overridden_params_from_session()
        for detector_name, params in result.items():
            allowed = _ALLOWED_PARAMS.get(detector_name, set())
            if detector_name in overridden:
                for p_name, p_val in overridden[detector_name].items():
                    if p_name in allowed:
                        params[p_name] = p_val
        return result
    except Exception as e:
        st.error(f"Неожиданная ошибка: {e}")
        return {}

def get_detector_parameters_for_api() -> Dict[str, Dict[str, Any]]:
    params = get_detector_parameters()
    def _to_int(value: Any, default: int) -> int:
        try:
            if isinstance(value, bool):
                return int(value)
            if value is None:
                return default
            return int(float(value))
        except (TypeError, ValueError):
            return default
    def _to_float(value: Any, default: float, round_to_1_dec: bool = False) -> float:
        try:
            if isinstance(value, bool):
                val = float(int(value))
            elif value is None:
                val = default
            else:
                val = float(value)
            return round(val, 1) if round_to_1_dec else val
        except (TypeError, ValueError):
            return default
    freezing = params.get("freezing", {})
    avalanche = params.get("avalanche", {})
    outlier = params.get("outlier", {})
    return {
        "freezing": {
            "freezing_count": _to_int(freezing.get("freezing_count"), default=5),
            "rel_tol": _to_float(freezing.get("rel_tol"), default=1e-9, round_to_1_dec=False),
        },
        "avalanche": {
            "hi_percent": _to_float(avalanche.get("hi_percent"), default=0.95, round_to_1_dec=True),
            "low_percent": _to_float(avalanche.get("low_percent"), default=0.05, round_to_1_dec=True),
            "bound_coef": _to_float(avalanche.get("bound_coef"), default=5.0, round_to_1_dec=True),
            "statistic_len": _to_int(avalanche.get("statistic_len"), default=30),
            "statistic_len_for_mean": _to_int(avalanche.get("statistic_len_for_mean"), default=5),
        },
        "outlier": {
            "hi_percent": _to_float(outlier.get("hi_percent"), default=0.95, round_to_1_dec=True),
            "low_percent": _to_float(outlier.get("low_percent"), default=0.05, round_to_1_dec=True),
            "bound_coef": _to_float(outlier.get("bound_coef"), default=3.0, round_to_1_dec=True),
            "statistic_len": _to_int(outlier.get("statistic_len"), default=144),
            "statistic_len_for_mean": _to_int(outlier.get("statistic_len_for_mean"), default=12),
        },
    }

def _save_overrides(detector_name: str, edited_params: Dict[str, Any]) -> None:
    if "detector_param_overrides" not in st.session_state or not isinstance(st.session_state.get("detector_param_overrides"), dict):
        st.session_state.detector_param_overrides = {}
    if detector_name not in st.session_state.detector_param_overrides:
        st.session_state.detector_param_overrides[detector_name] = {}
    st.session_state.detector_param_overrides[detector_name].update(edited_params)

def _render_freezing_popover(params: Dict[str, Any]) -> None:
    with st.popover("⚙️ Настроить параметры", use_container_width=True):
        st.write("Детектор замерзания")
        col1, col2 = st.columns(2)
        with col1:
            freezing_count = st.number_input(
                "freezing_count (int)",
                value=int(params.get("freezing_count", 5)),
                min_value=0, step=1, key="freezing_freezing_count"
            )
        with col2:
            rel_tol = st.number_input(
                "rel_tol (float)",
                value=float(params.get("rel_tol", 1e-9)),
                min_value=0.0, step=1e-9, format="%.9f", key="freezing_rel_tol"
            )
        if st.button("💾 Сохранить", use_container_width=True, key="save_freezing"):
            _save_overrides("freezing", {
                "freezing_count": int(freezing_count),
                "rel_tol": float(rel_tol),
            })
            st.success("Параметры сохранены для текущего сеанса!")
            st.rerun()

def _render_avalanche_popover(params: Dict[str, Any]) -> None:
    with st.popover("⚙️ Настроить параметры", use_container_width=True):
        st.write("Детектор лавинной скорости")
        col1, col2 = st.columns(2)
        with col1:
            hi_percent = st.number_input(
                "hi_percent (0..1, шаг 0.1)",
                value=float(params.get("hi_percent", 0.95)),
                min_value=0.0, max_value=1.0,
                step=0.1, format="%.1f",
                key="avalanche_hi_percent"
            )
            statistic_len = st.number_input(
                "statistic_len (int)",
                value=int(params.get("statistic_len", 30)),
                min_value=1, step=1,
                key="avalanche_stat_len"
            )
        with col2:
            low_percent = st.number_input(
                "low_percent (0..1, шаг 0.1)",
                value=float(params.get("low_percent", 0.05)),
                min_value=0.0, max_value=1.0,
                step=0.1, format="%.1f",
                key="avalanche_low_percent"
            )
            statistic_len_for_mean = st.number_input(
                "statistic_len_for_mean (int)",
                value=int(params.get("statistic_len_for_mean", 5)),
                min_value=1, step=1,
                key="avalanche_stat_len_mean"
            )
        bound_coef = st.number_input(
            "bound_coef (шаг 0.1)",
            value=float(params.get("bound_coef", 5.0)),
            min_value=0.0, step=0.1, format="%.1f",
            key="avalanche_bound_coef"
        )
        if st.button("💾 Сохранить", use_container_width=True, key="save_avalanche"):
            _save_overrides("avalanche", {
                "hi_percent": round(float(hi_percent), 1),
                "low_percent": round(float(low_percent), 1),
                "bound_coef": round(float(bound_coef), 1),
                "statistic_len": int(statistic_len),
                "statistic_len_for_mean": int(statistic_len_for_mean),
            })
            st.success("Параметры сохранены для текущего сеанса!")
            st.rerun()

def _render_outlier_popover(params: Dict[str, Any]) -> None:
    with st.popover("⚙️ Настроить параметры", use_container_width=True):
        st.write("Детектор аномалий")
        col1, col2 = st.columns(2)
        with col1:
            hi_percent = st.number_input(
                "hi_percent (0..1, шаг 0.1)",
                value=float(params.get("hi_percent", 0.95)),
                min_value=0.0, max_value=1.0,
                step=0.1, format="%.1f",
                key="outlier_hi_percent"
            )
            statistic_len = st.number_input(
                "statistic_len (int)",
                value=int(params.get("statistic_len", 144)),
                min_value=1, step=1,
                key="outlier_stat_len"
            )
        with col2:
            low_percent = st.number_input(
                "low_percent (0..1, шаг 0.1)",
                value=float(params.get("low_percent", 0.05)),
                min_value=0.0, max_value=1.0,
                step=0.1, format="%.1f",
                key="outlier_low_percent"
            )
            statistic_len_for_mean = st.number_input(
                "statistic_len_for_mean (int)",
                value=int(params.get("statistic_len_for_mean", 12)),
                min_value=1, step=1,
                key="outlier_stat_len_mean"
            )
        bound_coef = st.number_input(
            "bound_coef (шаг 0.1)",
            value=float(params.get("bound_coef", 3.0)),
            min_value=0.0, step=0.1, format="%.1f",
            key="outlier_bound_coef"
        )
        if st.button("💾 Сохранить", use_container_width=True, key="save_outlier"):
            _save_overrides("outlier", {
                "hi_percent": round(float(hi_percent), 1),
                "low_percent": round(float(low_percent), 1),
                "bound_coef": round(float(bound_coef), 1),
                "statistic_len": int(statistic_len),
                "statistic_len_for_mean": int(statistic_len_for_mean),
            })
            st.success("Параметры сохранены для текущего сеанса!")
            st.rerun()

def display_detector_parameters():
    st.header("Параметры детекторов")
    detector_params = get_detector_parameters()
    if not detector_params:
        st.warning("Не удалось загрузить параметры детекторов")
        return
    series_data = st.session_state.get("current_dataset")
    if series_data is not None:
        st.info(f"Датасет загружен: {len(series_data)} точек данных")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Детектор замерзания")
        params = detector_params.get("freezing", {})
        if "freezing_count" in params:
            try:
                display_value = int(params["freezing_count"]) if not isinstance(params["freezing_count"], (int, float)) else int(params["freezing_count"])
            except (TypeError, ValueError):
                display_value = 0
            st.metric("Количество замерзаний", f"{display_value}")
        else:
            st.warning("Параметр freezing_count не найден")
        _render_freezing_popover(params)
    with col2:
        st.subheader("Детектор лавинной скорости")
        params = detector_params.get("avalanche", {})
        if "bound_coef" in params:
            try:
                display_value = float(params["bound_coef"]) if not isinstance(params["bound_coef"], (int, float)) else float(params["bound_coef"])
            except (TypeError, ValueError):
                display_value = 0.0
            st.metric("Коэффициент границы", f"{display_value:.1f}")
        else:
            st.warning("Параметр bound_coef не найден")
        _render_avalanche_popover(params)
    with col3:
        st.subheader("Детектор аномалий")
        params = detector_params.get("outlier", {})
        if "bound_coef" in params:
            try:
                display_value = float(params["bound_coef"]) if not isinstance(params["bound_coef"], (int, float)) else float(params["bound_coef"])
            except (TypeError, ValueError):
                display_value = 3.0
            st.metric("Коэффициент границы", f"{display_value:.1f}")
        else:
            st.warning("Параметр bound_coef не найден")
        _render_outlier_popover(params)

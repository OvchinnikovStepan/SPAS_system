import streamlit as st
from typing import Dict, Any
from .request_parameters import request_parameters

def _initialize_default_overrides_once() -> None:
    """
    Инициализирует стандартные значения параметров детекторов только один раз
    за сессию пользователя. Не перезаписывает уже заданные пользователем
    переопределения.
    """
    defaults_flag_key = "detector_defaults_initialized"
    if st.session_state.get(defaults_flag_key):
        return

    # Текущие переопределения пользователя (если уже есть)
    existing_overrides = st.session_state.get("detector_param_overrides")
    if not isinstance(existing_overrides, dict):
        existing_overrides = {}

    # Базовые дефолты на первый запуск
    default_overrides: Dict[str, Dict[str, Any]] = {
        "freezing": {"freezing_count": 3},
        "avalanche": {"bound_coef": 1.0},
        "outlier": {"bound_coef": 1.0},
    }

    # Объединяем, не перезаписывая уже существующие значения пользователя
    for detector_name, params in default_overrides.items():
        if detector_name not in existing_overrides or not isinstance(existing_overrides.get(detector_name), dict):
            existing_overrides.setdefault(detector_name, {})
        for param_name, param_value in params.items():
            existing_overrides[detector_name].setdefault(param_name, param_value)

    st.session_state.detector_param_overrides = existing_overrides
    st.session_state[defaults_flag_key] = True

def _get_overridden_params_from_session() -> Dict[str, Dict[str, Any]]:
    """Возвращает переопределенные пользователем параметры из session_state."""
    overrides = st.session_state.get("detector_param_overrides")
    if isinstance(overrides, dict):
        return overrides
    return {}

def get_detector_parameters() -> Dict[str, Dict[str, Any]]:
    """
    Получает параметры всех детекторов из функции request_parameters.
    
    Returns:
        Dict[str, Dict[str, Any]]: Словарь с параметрами детекторов
        Ключи: 'avalanche', 'freezing', 'outlier'
        Значения: словари с параметрами соответствующих детекторов
    """
    try:
        result = request_parameters()

        if "error" in result:
            st.error(f"Ошибка получения параметров: {result['error']}")
            return {}

        # Гарантируем дефолты один раз на первую загрузку сессии
        _initialize_default_overrides_once()

        # Переопределения параметров из сессии (пер-пользовательский сеанс)
        overridden = _get_overridden_params_from_session()

        for detector_name, params in result.items():
            if detector_name in overridden:
                # Обновляем только разрешенные для изменения параметры
                if detector_name == "freezing" and "freezing_count" in overridden[detector_name]:
                    params["freezing_count"] = overridden[detector_name]["freezing_count"]
                elif detector_name in ["avalanche", "outlier"] and "bound_coef" in overridden[detector_name]:
                    params["bound_coef"] = overridden[detector_name]["bound_coef"]

        return result
    except Exception as e:
        st.error(f"Неожиданная ошибка: {e}")
        return {}

def get_detector_parameters_for_api() -> Dict[str, Dict[str, Any]]:
    """
    Возвращает словарь параметров детекторов, приведённый к корректным типам
    для отправки в API.

    Структура возврата:
    {
        "freezing": {"freezing_count": int},
        "avalanche": {"bound_coef": float},
        "outlier": {"bound_coef": float}
    }
    """
    params = get_detector_parameters()

    def _to_int(value: Any, default: int) -> int:
        try:
            if isinstance(value, bool):
                return int(value)
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _to_float(value: Any, default: float) -> float:
        try:
            if isinstance(value, bool):
                return float(int(value))
            return float(value)
        except (TypeError, ValueError):
            return default

    freezing_count = _to_int(params.get("freezing", {}).get("freezing_count"), default=3)
    avalanche_bound = _to_float(params.get("avalanche", {}).get("bound_coef"), default=1.0)
    outlier_bound = _to_float(params.get("outlier", {}).get("bound_coef"), default=1.0)

    return {
        "freezing": {"freezing_count": freezing_count, "rel_tol": 1e-4},
        "avalanche": {"bound_coef": avalanche_bound, "statistic_len": 144, "statistic_len_for_mean": 12},
        "outlier": {"bound_coef": outlier_bound, "statistic_len": 144, "statistic_len_for_mean": 12},
    }

def display_detector_parameters():
    """
    Отображает параметры детекторов в трех колонках на основном экране.
    """
    st.header("Параметры детекторов")
    
    # Получаем параметры детекторов
    detector_params = get_detector_parameters()
    
    if not detector_params:
        st.warning("Не удалось загрузить параметры детекторов")
        return
    
    # Отображаем информацию о датасете из session_state, если он есть
    series_data = st.session_state.get("current_dataset")
    if series_data is not None:
        st.info(f"Датасет загружен: {len(series_data)} точек данных")
    
    # Создаем три колонки для детекторов
    col1, col2, col3 = st.columns(3)
    
    # Колонка 1: Детектор замерзания
    with col1:
        st.subheader("Детектор замерзания")
        
        if "freezing" in detector_params:
            params = detector_params["freezing"]
            
            # Отображаем только freezing_count
            if "freezing_count" in params:
                raw_value = params["freezing_count"]
                try:
                    display_value = int(raw_value) if not isinstance(raw_value, (int, float)) else int(raw_value)
                except (TypeError, ValueError):
                    display_value = 0
                st.metric("Количество замерзаний", f"{display_value}")
            else:
                st.warning("Параметр freezing_count не найден")
            
            # Кнопка для настройки параметров
            if st.button("⚙️ Настроить параметры", key="freezing_config", use_container_width=True):
                st.session_state.configuring_detector = "freezing"
                st.session_state.detector_params = params
                st.rerun()
        else:
            st.warning("Параметры не найдены")
    
    # Колонка 2: Детектор лавинной скорости
    with col2:
        st.subheader("Детектор лавинной скорости")
        
        if "avalanche" in detector_params:
            params = detector_params["avalanche"]
            
            # Отображаем только bound_coef
            if "bound_coef" in params:
                raw_value = params["bound_coef"]
                try:
                    display_value = float(raw_value) if not isinstance(raw_value, (int, float)) else float(raw_value)
                except (TypeError, ValueError):
                    display_value = 0.0
                st.metric("Коэффициент границы", f"{display_value:.3f}")
            else:
                st.warning("Параметр bound_coef не найден")
            
            # Кнопка для настройки параметров
            if st.button("⚙️ Настроить параметры", key="avalanche_config", use_container_width=True):
                st.session_state.configuring_detector = "avalanche"
                st.session_state.detector_params = params
                st.rerun()
        else:
            st.warning("Параметры не найдены")
    
    # Колонка 3: Детектор аномалий
    with col3:
        st.subheader("Детектор аномалий")
        
        if "outlier" in detector_params:
            params = detector_params["outlier"]
            
            # Отображаем только bound_coef
            if "bound_coef" in params:
                raw_value = params["bound_coef"]
                try:
                    display_value = float(raw_value) if not isinstance(raw_value, (int, float)) else float(raw_value)
                except (TypeError, ValueError):
                    display_value = 0.0
                st.metric("Коэффициент границы", f"{display_value:.3f}")
            else:
                st.warning("Параметр bound_coef не найден")
            
            # Кнопка для настройки параметров
            if st.button("⚙️ Настроить параметры", key="outlier_config", use_container_width=True):
                st.session_state.configuring_detector = "outlier"
                st.session_state.detector_params = params
                st.rerun()
        else:
            st.warning("Параметры не найдены")
    
    # Если выбран детектор для настройки, показываем форму редактирования
    if hasattr(st.session_state, 'configuring_detector') and st.session_state.configuring_detector:
        st.divider()
        st.subheader(f"⚙️ Настройка параметров: {st.session_state.configuring_detector}")
        
        if hasattr(st.session_state, 'detector_params') and st.session_state.detector_params:
            # Создаем форму для редактирования параметров
            with st.form(key=f"config_form_{st.session_state.configuring_detector}"):
                edited_params = {}
                
                # Показываем только нужные параметры для каждого детектора
                if st.session_state.configuring_detector == "freezing":
                    # Для детектора замерзания только freezing_count
                    if "freezing_count" in st.session_state.detector_params:
                        freezing_count = st.session_state.detector_params["freezing_count"]
                        edited_params["freezing_count"] = st.number_input(
                            "Количество замерзаний:",
                            value=int(freezing_count) if isinstance(freezing_count, (int, float)) else 3,
                            min_value=0,
                            step=1,
                            key="config_freezing_count"
                        )
                
                elif st.session_state.configuring_detector == "avalanche":
                    # Для детектора лавин только bound_coef
                    if "bound_coef" in st.session_state.detector_params:
                        bound_coef = st.session_state.detector_params["bound_coef"]
                        edited_params["bound_coef"] = st.number_input(
                            "Коэффициент границы:",
                            value=float(bound_coef) if isinstance(bound_coef, (int, float)) else 1.0,
                            min_value=0.0,
                            step=0.1,
                            key="config_avalanche_bound_coef"
                        )
                
                elif st.session_state.configuring_detector == "outlier":
                    # Для детектора аномалий только bound_coef
                    if "bound_coef" in st.session_state.detector_params:
                        bound_coef = st.session_state.detector_params["bound_coef"]
                        edited_params["bound_coef"] = st.number_input(
                            "Коэффициент границы:",
                            value=float(bound_coef) if isinstance(bound_coef, (int, float)) else 1.0,
                            min_value=0.0,
                            step=0.1,
                            key="config_outlier_bound_coef"
                        )
                
                # Кнопки для сохранения и отмены
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.form_submit_button("💾 Сохранить", use_container_width=True):
                        # Сохраняем параметры в файл
                        detector_name = st.session_state.configuring_detector
                        if detector_name not in detector_params:
                            detector_params[detector_name] = {}
                        
                        # Обновляем параметры в основном словаре
                        detector_params[detector_name].update(edited_params)
                        
                        # Обновляем переопределения параметров в session_state
                        if "detector_param_overrides" not in st.session_state or not isinstance(st.session_state.get("detector_param_overrides"), dict):
                            st.session_state.detector_param_overrides = {}
                        if detector_name not in st.session_state.detector_param_overrides:
                            st.session_state.detector_param_overrides[detector_name] = {}
                        st.session_state.detector_param_overrides[detector_name].update(edited_params)
                        
                        st.success("Параметры успешно сохранены для текущего сеанса пользователя!")
                        st.session_state.detector_params = edited_params
                        
                        # Сбрасываем состояние настройки
                        if 'configuring_detector' in st.session_state:
                            del st.session_state.configuring_detector
                        if 'detector_params' in st.session_state:
                            del st.session_state.detector_params
                        st.rerun()
                
                with col_cancel:
                    if st.form_submit_button("❌ Отмена", use_container_width=True):
                        # Сбрасываем состояние настройки
                        if 'configuring_detector' in st.session_state:
                            del st.session_state.configuring_detector
                        if 'detector_params' in st.session_state:
                            del st.session_state.detector_params
                        st.rerun()
        
        # Кнопка для закрытия формы настройки
        if st.button("🔙 Вернуться", key="back_to_overview"):
            if 'configuring_detector' in st.session_state:
                del st.session_state.configuring_detector
            if 'detector_params' in st.session_state:
                del st.session_state.detector_params
            st.rerun()

import streamlit as st
from dashboard.services.upload_data import upload_data
from dashboard.components.timeseries_plot import show_timeseries_plot
from dashboard.utils.validate_data import validate_data
from dashboard.components.recording_parameters import display_detector_parameters
from dashboard.components.request_detectors_output import send_detectors_request

def main_page():
    st.title("SPAS System")
    
    # Загружаем данные
    df = upload_data()
    
    if validate_data(df):
        # Сохраняем датасет в session_state
        st.session_state.current_dataset = df
        
        # Если результаты детекторов еще не загружены, инициализируем пустым значением
        if 'detectors_results' not in st.session_state:
            st.session_state.detectors_results = None
        
        # Отображаем график (первоначальный или обновленный)
        feature = show_timeseries_plot(
            df, 
            st.session_state.detectors_results,
            key="main_timeseries_plot"  # Добавляем уникальный ключ
        )
        st.session_state.feature = feature

        # Отображаем параметры детекторов
        display_detector_parameters()

        # Кнопка пересчета
        recalc_clicked = st.button(
            "Выполнить пересчет", 
            use_container_width=True,
            key="recalc_button"
        )

        # При нажатии кнопки выполняем запрос и обновляем график
        if recalc_clicked:
            with st.spinner("Запрашиваем значения детекторов..."):
                try:
                    # Получаем результаты детекторов
                    detectors_results = send_detectors_request(df, feature)
                    
                    # Сохраняем результаты в session_state
                    st.session_state.detectors_results = detectors_results
                    
                    # Показываем сообщение об успехе
                    st.success("Пересчет выполнен")
                    
                    # Принудительно обновляем страницу для отображения новых данных
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Ошибка при получении значений детекторов: {e}")
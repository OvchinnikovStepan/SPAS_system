import streamlit as st
from dashboard.services.upload_data import upload_data
from dashboard.components.timeseries_plot import show_timeseries_plot
from dashboard.utils.validate_data import validate_data

def main_page():
    df = upload_data()

    if validate_data(df):
        selected_area = show_timeseries_plot(df)
        st.session_state['selected_area'] = selected_area

    if 'selected_area' in st.session_state and st.session_state['selected_area'] is not None:
        if st.button('Отобразить данные в выделенной области'):
            @st.dialog("Выделенная область")
            def display_selected_area():
                st.dataframe(st.session_state['selected_area'])
            display_selected_area()
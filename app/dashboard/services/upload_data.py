import pandas as pd
import streamlit as st
from typing import Optional
from dashboard.utils.validate_data import validate_dataframe_structure
from dashboard.utils.validate_datetime_index import validate_datetime_index


def upload_data() -> Optional[pd.DataFrame]:
    """Загрузка данных из Excel или CSV через streamlit, с валидацией и проверкой формата дат в индексе."""
    uploaded_file = st.file_uploader("Загрузите файл Excel или CSV", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, index_col=0, parse_dates=True)
            else:
                st.error("Поддерживаются только файлы .csv и .xlsx")
                return None
            validate_dataframe_structure(df, raise_error=True)
            validate_datetime_index(df)
            st.success("Данные успешно загружены и валидированы!")
            return df
        except Exception as e:
            st.error(f"Ошибка при загрузке данных: {e}")
    return None

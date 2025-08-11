import streamlit as st
from dashboard.services.upload_data import upload_data
from dashboard.components.timeseries_plot import show_timeseries_plot
from dashboard.utils.validate_data import validate_data

def main_page():
    df = upload_data()

    if validate_data(df):
        show_timeseries_plot(df)
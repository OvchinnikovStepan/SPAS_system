import streamlit as st
from dashboard.services.upload_data import upload_data


df = upload_data()

st.write(df)
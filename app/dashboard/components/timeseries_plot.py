from ast import Pass
from pandas._config import display
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


def show_timeseries_plot(df: pd.DataFrame):
    """
    Отображает интерактивный график временного ряда с выбором признака и возможностью выделять и сохранять область.
    
    Параметры: 
        pandas DataFrame с временным индексом и признаками

    Возвращает:
        DataFrame с точками в выделенной области или None
    """
    feature = st.selectbox("Выберите признак для отображения:", df.columns)

    if 'last_feature' not in st.session_state:
        st.session_state['last_feature'] = feature
    if st.session_state['last_feature'] != feature:
        st.session_state['selected_points_df'] = None
        st.session_state['last_points'] = None
    st.session_state['last_feature'] = feature

    data = df[[feature]].copy()
    data = data.reset_index().rename(columns={data.index.name or 'index': 'Время'})

    col_use, col_clear = st.columns(2)
    with col_use:
        use_btn = st.button("Использовать выделенную область", key="use_selection")
    with col_clear:
        clear_btn = st.button("Очистить выделение", key="clear_selection")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Время'],
        y=data[feature],
        mode='lines+markers',
        name="Основной ряд",
        line=dict(color="#1976d2", width=2),
        marker=dict(size=6, color="#1976d2", line=dict(width=0)),
        opacity=0.9,
        showlegend=True
    ))
    if st.session_state.get('selected_points_df') is not None and not st.session_state['selected_points_df'] is None and not st.session_state['selected_points_df'].empty:
        selected_df = st.session_state['selected_points_df']
        fig.add_trace(go.Scatter(
            x=selected_df['Время'],
            y=selected_df[feature],
            mode='lines+markers',
            name="Выделенные точки",
            line=dict(color="#43a047", width=2),
            marker=dict(size=10, color="#43a047", symbol="diamond"),
            opacity=1.0,
            showlegend=True
        ))
    fig.update_layout(
        dragmode='select',
        selectdirection='h',
        margin=dict(l=40, r=20, t=50, b=40),
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        font=dict(family="Montserrat, Arial", size=14),
        title=dict(x=0.5, font=dict(size=20)),
        xaxis=dict(
            title="Дата",
            tickangle=0,
            tickformat="%d.%m.%Y",
            showgrid=True,
            gridcolor="#e0e0e0",
            ticklabelmode="period",
            automargin=True,
            tickfont=dict(size=12),
            titlefont=dict(size=16)
        ),
        yaxis=dict(
            title=feature,
            showgrid=True,
            gridcolor="#e0e0e0",
            tickfont=dict(size=12),
            titlefont=dict(size=16),
            automargin=True
        ),
        hovermode="x unified"
    )
    fig.update_xaxes(nticks=min(10, len(data)))

    selected_points = plotly_events(fig, select_event=True, override_height=500, override_width='100%')

    if 'selected_points_df' not in st.session_state:
        st.session_state['selected_points_df'] = None
    if 'last_points' not in st.session_state:
        st.session_state['last_points'] = None

    if selected_points:
        indices = [pt['pointIndex'] for pt in selected_points]
        selected_df = data.iloc[indices].sort_values('Время')
        st.session_state['last_points'] = selected_df

    if use_btn and st.session_state['last_points'] is not None:
        st.session_state['selected_points_df'] = st.session_state['last_points']
        st.rerun()
    if clear_btn:
        st.session_state['selected_points_df'] = None
        st.session_state['last_points'] = None
        st.rerun()

    # Возвращаем DataFrame с точками в выделенной области или None
    return st.session_state['selected_points_df']
        
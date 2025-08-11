import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def show_timeseries_plot(df: pd.DataFrame) -> None:
    """
    Отображает простой график временного ряда с выбором признака.
    Легенда включена. Оси и легенда оформлены в контрастном стиле.

    Параметры:
        df: pandas DataFrame с временным индексом и признаками
    """

    feature = st.selectbox("Выберите признак для отображения:", df.columns)

    data = df[[feature]].copy()
    data = data.reset_index().rename(columns={data.index.name or 'index': 'Время'})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data['Время'],
            y=data[feature],
            mode='lines+markers',
            name=feature,
            line=dict(color="#1565c0", width=2.5),
            marker=dict(size=6, color="#1565c0"),
            opacity=0.95,
            showlegend=True,
        )
    )

    fig.update_layout(
        margin=dict(l=50, r=30, t=40, b=50),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Montserrat, Arial", size=14, color="#111111"),
        hovermode="x unified",
        legend=dict(
            bgcolor="#ffffff",
            bordercolor="#111111",
            borderwidth=1,
            font=dict(color="#111111"),
            orientation='h',
            x=0,
            y=1.1,
        ),
        xaxis=dict(
            title="Дата",
            tickangle=0,
            tickformat="%d.%m.%Y",
            showgrid=True,
            gridcolor="#d0d0d0",
            zeroline=False,
            ticks="outside",
            tickcolor="#111111",
            ticklen=6,
            linecolor="#111111",
            linewidth=2,
            mirror=True,
            automargin=True,
            ticklabelmode="period",
            titlefont=dict(size=16, color="#111111"),
            tickfont=dict(size=12, color="#111111"),
        ),
        yaxis=dict(
            title=feature,
            showgrid=True,
            gridcolor="#d0d0d0",
            zeroline=False,
            ticks="outside",
            tickcolor="#111111",
            ticklen=6,
            linecolor="#111111",
            linewidth=2,
            mirror=True,
            automargin=True,
            titlefont=dict(size=16, color="#111111"),
            tickfont=dict(size=12, color="#111111"),
        ),
    )

    fig.update_xaxes(nticks=min(12, max(4, len(data) // 7)))

    st.plotly_chart(fig, use_container_width=True)
        
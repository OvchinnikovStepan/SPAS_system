import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Dict, Optional


def show_timeseries_plot(df: pd.DataFrame, detectors_results: Optional[Dict[str, Any]] = None, key: Optional[str] = None) -> str:
    """
    Отображает график временного ряда с выбором признака и вертикальными линиями
    через точки, где срабатывали детекторы (avalanche / freezing / outlier).
    """

    feature = st.selectbox(
        "Выберите признак для отображения:", 
        df.columns,
        key=f"feature_select_{key}" if key else "feature_select"
    )

    # Основные данные ряда
    values = df[[feature]].copy()
    data_for_plot = values.reset_index().rename(columns={values.index.name or 'index': 'Время'})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data_for_plot['Время'],
            y=data_for_plot[feature],
            mode='lines+markers',
            name=feature,
            line=dict(color="#1565c0", width=2.5),
            marker=dict(size=6, color="#1565c0"),
            opacity=0.95,
            showlegend=True,
        )
    )

    # Наложение маркеров детекторов + ВЕРТИКАЛЬНЫЕ ЛИНИИ
    vertical_shapes = []

    if detectors_results and isinstance(detectors_results, dict):
        results_dict = detectors_results.get("results", {})
        if isinstance(results_dict, dict) and len(results_dict) > 0:
            detectors_df = pd.DataFrame.from_dict(results_dict, orient='index')
            try:
                detectors_df.index = pd.to_datetime(detectors_df.index)
            except Exception:
                pass

            aligned_flags = detectors_df.reindex(values.index)

            detector_styles = {
                "avalanche": {"color": "#ff0400", "symbol": "x", "name": "avalanche"},
                "freezing": {"color": "#B8FF06", "symbol": "diamond", "name": "freezing"},
                "outlier": {"color": "#fe00a9", "symbol": "triangle-up", "name": "outlier"},
            }

            for detector_name, style in detector_styles.items():
                if detector_name in aligned_flags.columns:
                    true_mask = aligned_flags[detector_name] == True
                    if true_mask.any():
                        x_points = values.index[true_mask]
                        y_points = values.loc[true_mask, feature]

                        fig.add_trace(
                            go.Scatter(
                                x=x_points,
                                y=y_points,
                                mode='markers',
                                name=style["name"],
                                marker=dict(
                                    size=10,
                                    color=style["color"],
                                    symbol=style["symbol"],
                                    line=dict(width=1, color="#111111")
                                ),
                                opacity=0.95,
                                showlegend=True,
                            )
                        )

                        # Вертикальные линии через каждую точку
                        for x in x_points:
                            vertical_shapes.append(dict(
                                type="line",
                                xref="x", x0=x, x1=x,
                                yref="paper", y0=0, y1=1,
                                layer="below",
                                line=dict(color=style["color"], width=1),
                                opacity=0.8
                            ))

    # Добавляем накопленные линии в layout
    if vertical_shapes:
        existing = list(fig.layout.shapes) if fig.layout.shapes else []
        fig.update_layout(shapes=existing + vertical_shapes)

    fig.update_layout(
        margin=dict(l=50, r=30, t=40, b=50),
        meta={"streamlit_key": "timeseries_plot"},
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
            title=dict(text="Дата", font=dict(size=16, color="#111111")),
            tickangle=0,
            tickformat="%d.%m.%Y",
            showgrid=True,
            gridcolor="rgba(208,208,208,0.7)",
            zeroline=False,
            ticks="outside",
            tickcolor="#111111",
            ticklen=6,
            linecolor="#111111",
            linewidth=2,
            mirror=True,
            automargin=True,
            ticklabelmode="period",
            tickfont=dict(size=12, color="#111111"),
        ),
        yaxis=dict(
            title=dict(text=feature, font=dict(size=16, color="#111111")),
            showgrid=True,
            gridcolor="rgba(208,208,208,0.7)",
            zeroline=False,
            ticks="outside",
            tickcolor="#111111",
            ticklen=6,
            linecolor="#111111",
            linewidth=2,
            mirror=True,
            automargin=True,
            tickfont=dict(size=12, color="#111111"),
        ),
    )

    fig.update_xaxes(nticks=min(12, max(4, len(data_for_plot) // 7)))
    st.plotly_chart(fig, use_container_width=True, key="main_plot")
    return feature

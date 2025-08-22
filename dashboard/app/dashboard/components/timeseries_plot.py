import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Dict, Optional


# Стили детекторов (можно править централизованно)
DETECTOR_STYLES: Dict[str, Dict[str, str]] = {
    "avalanche": {"symbol": "x",           "name": "avalanche", "color": "#ff0000"},
    "freezing":  {"symbol": "diamond",     "name": "freezing",  "color": "#00cc44"},
    "outlier":   {"symbol": "triangle-up", "name": "outlier",   "color": "#ff00cc"},
}

MARKER_SIZE = 12
MARKER_BORDER_WIDTH = 2
MAIN_LINE_WIDTH = 2.2


def show_timeseries_plot(
    df: pd.DataFrame,
    detectors_results: Optional[Dict[str, Any]] = None,
    key: Optional[str] = None
) -> str:
    """
    Отображает график временного ряда:
    - основной ряд одной линией (Scattergl, без маркеров);
    - для каждого детектора два трейса с общим legendgroup:
        1) маркеры (видимы в легенде),
        2) «стебли» как один Scattergl с разрывами (скрыт в легенде).
      Благодаря legendgroup скрытие детектора в легенде скрывает и маркеры, и стебли.
    """

    # Выбор признака
    feature = st.selectbox(
        "Выберите признак для отображения:",
        df.columns,
        key=f"feature_select_{key}" if key else "feature_select",
    )

    # Данные ряда
    values = df[[feature]].copy()
    data_for_plot = values.reset_index().rename(columns={values.index.name or 'index': 'Время'})

    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=data_for_plot['Время'],
            y=data_for_plot[feature],
            mode='lines',
            name=feature,
            line=dict(width=MAIN_LINE_WIDTH, color="#1565c0"),
            opacity=0.95,
            showlegend=True,
        )
    )

    # ДЕТЕКТОРЫ: маркеры + «стебли», связанные через legendgroup
    if detectors_results and isinstance(detectors_results, dict):
        results_dict = detectors_results.get("results", {})
        if isinstance(results_dict, dict) and len(results_dict) > 0:
            detectors_df = pd.DataFrame.from_dict(results_dict, orient='index')
            try:
                detectors_df.index = pd.to_datetime(detectors_df.index, utc=True)
            except Exception:
                # если не удаётся привести индекс — оставляем как есть
                pass

            # Выравниваем по текущему индексу values (если индексы совместимы)
            aligned_flags = detectors_df.reindex(values.index)

            # Границы Y для «стеблей» (по текущему видимому ряду)
            y_min = float(values[feature].min())
            y_max = float(values[feature].max())
            pad = (y_max - y_min) * 0.03 if y_max > y_min else 1.0
            y0, y1 = y_min - pad, y_max + pad

            for det, style in DETECTOR_STYLES.items():
                if det not in aligned_flags.columns:
                    continue

                mask = aligned_flags[det] == True
                if not mask.any():
                    continue

                x_pts = values.index[mask]
                y_pts = values.loc[mask, feature]

                group = f"det_{det}"  # единая группа для маркеров и стеблей

                # 1) Маркеры (показываются в легенде)
                fig.add_trace(
                    go.Scattergl(
                        x=x_pts,
                        y=y_pts,
                        mode="markers",
                        name=style["name"],
                        legendgroup=group,
                        marker=dict(
                            size=MARKER_SIZE,
                            color=style["color"],
                            symbol=style["symbol"],
                            line=dict(width=MARKER_BORDER_WIDTH, color="#111111"),
                        ),
                        hovertemplate=(
                            f"<b>%{{text}}</b><br>"
                            "Время: %{x}<br>"
                            f"{feature}: %{{y:.4g}}<extra></extra>"
                        ),
                        text=[style["name"]] * len(x_pts),
                        showlegend=True,  # этот трейс отображается в легенде
                    )
                )

                # 2) «Стебли» как единый Scattergl c разрывами (не показывать в легенде)
                # Формируем последовательности вида [x1,x1,None, x2,x2,None, ...] и [y0,y1,None, ...]
                xs: list = []
                ys: list = []
                for x in x_pts:
                    xs.extend([x, x, None])
                    ys.extend([y0, y1, None])

                fig.add_trace(
                    go.Scattergl(
                        x=xs,
                        y=ys,
                        mode="lines",
                        name=style["name"] + " (lines)",
                        legendgroup=group,
                        opacity=0.05,
                        line=dict(width=1.2, color=style["color"]),
                        hoverinfo="skip",     # чтобы стебли не перехватывали ховер
                        showlegend=False,     # не дублировать пункт в легенде
                    )
                )

    # Оформление графика
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
            groupclick="togglegroup",  # клик по пункту скрывает/показывает всю группу
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
            showspikes=True,         # вертикальный курсор
            spikemode="across",
            spikesnap="cursor",
            spikethickness=1.5,
            spikedash="dot",
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

    # Умеренное число тиков по X (без тяжёлых расчётов)
    fig.update_xaxes(nticks=min(12, max(4, len(data_for_plot) // 7)))

    st.plotly_chart(fig, use_container_width=True, key="main_plot")
    return feature

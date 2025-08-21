import numpy as np
import pandas as pd


def avalanche_detector(
        series: pd.Series,
        statistic: pd.Series = None,
        last_point: pd.Timestamp = None,
        sensity: str = 'medium',
        hi_percent: float = 0.95,
        low_percent: float = 0.05,
        bound_coef: int = 5,
        statistic_len: int = 30,
        statistic_len_for_mean: int = 5,
):

    if bound_coef is None:
        bound_coef = {'low': 10, 'medium': 7, 'high': 5}.get(sensity, 7)

    # Убираем NaN/inf
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    series = series.groupby(series.index).last()

    if statistic is not None:
        statistic = statistic.replace([np.inf, -np.inf], np.nan).dropna()

    if statistic is None or statistic.empty:
        statistic = series.iloc[:-1]
        last_point = series.index[-2]

    def detection_step(series, statistic, last_point):
        statistics_diff = (statistic - statistic.shift(1)).dropna().abs()

        if statistics_diff.empty:
            return pd.Series(dtype=float), statistic, last_point

        q_hi = statistics_diff.quantile(hi_percent)
        q_lo = statistics_diff.quantile(low_percent)
        diff_std = statistics_diff[(statistics_diff <= q_hi) & (statistics_diff >= q_lo)].std()

        # Маска времени (избегаем деления на 0)
        time_deltas = (statistic.index[1:] - statistic.index[:-1]).seconds / 60
        time_deltas = np.where(time_deltas == 0, np.nan, time_deltas)

        statistics_diff_scaled = statistics_diff / time_deltas
        statistics_diff_scaled = statistics_diff_scaled[(statistics_diff <= q_hi) & (statistics_diff >= q_lo)]
        diff_std_scaled = statistics_diff_scaled.std()

        clear_statistics = statistic[(statistic <= statistic.quantile(hi_percent)) &
                                     (statistic >= statistic.quantile(low_percent))]
        mean = np.mean(clear_statistics.iloc[-statistic_len_for_mean:]) if not clear_statistics.empty else 0

        points_to_check = series.loc[last_point:].iloc[1:]
        diff = (series - series.shift(1)).dropna()
        delta = (series.index[1:] - series.index[:-1]).seconds / 60
        delta = np.where(delta == 0, np.nan, delta)
        diff = diff / delta

        prev_diff = diff.shift(1).dropna()

        index_to_check = points_to_check.index.intersection(diff.index).intersection(prev_diff.index)
        diff = diff[index_to_check]
        prev_diff = prev_diff[index_to_check]
        points_to_check = points_to_check[index_to_check]

        cond_1 = prev_diff.abs() > bound_coef * diff_std_scaled
        cond_2 = True
        cond_3 = ((points_to_check - mean).abs() > bound_coef * diff_std) | (diff.abs() > bound_coef * diff_std_scaled)

        checked_points = points_to_check[cond_1 & cond_2 & cond_3]

        if statistic is not None and not statistic.empty:
            new_points = points_to_check.copy().drop_duplicates()
            if not new_points.empty:
                try:
                    if statistic.iloc[-1] == new_points.iloc[0]:
                        new_points.drop(new_points.index[0], inplace=True)
                except IndexError:
                    pass
                if not new_points.empty:
                    statistic = pd.concat([statistic, new_points])
                    statistic = statistic.iloc[-statistic_len:]

        last_point = series.index[-1]
        statistic = statistic.groupby(statistic.index).last()

        return checked_points, statistic, last_point

    checked_points = pd.Series(dtype=float)

    while len(series) > 100:
        checked_points_on_step, statistic, last_point = detection_step(
            series=series[:100], statistic=statistic, last_point=last_point
        )
        if not checked_points_on_step.empty:
            checked_points = pd.concat([checked_points, checked_points_on_step]) if not checked_points.empty else checked_points_on_step
        series = series[99:]
    else:
        checked_points_on_step, _, _ = detection_step(series=series, statistic=statistic, last_point=last_point)
        if not checked_points_on_step.empty:
            checked_points = pd.concat([checked_points, checked_points_on_step]) if not checked_points.empty else checked_points_on_step

    return checked_points

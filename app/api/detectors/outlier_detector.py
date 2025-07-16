import numpy as np
import pandas as pd

def outlier_detector(
    series: pd.Series,
    statistic: pd.Series = None,
    last_point: pd.Timestamp = None,
    sensity: str = 'medium',
    hi_percent: float = 0.95,
    low_percent: float = 0.05,
    bound_coef: int = None,
    statistic_len: int = 144,
    statistic_len_for_mean: int = 12
):
        """
        Аргументы функции обнаружения выбросов.

        Аргументы:
        series: Анализируемая часть данных
        statistic: Статистика
        last_point: Последняя точка статистики
        outlier_sensity (str): параметр чувствительности;
        bound_coef (int): коэффициент для порога;
        hi_percent (float): высший порог перцентиля;
        low_percent (float): низший порог перцентиля;
        statistic_len (int): длина записи статистики (из идеи 1 расчет в 10 минут);
        statistic_len_for_mean (int): длина статистики для расчета среднего значения.
        """
        if bound_coef is None:
            if sensity == 'low':
                bound_coef = 10
            elif sensity == 'medium':
                bound_coef = 7
            elif sensity == 'high':
                bound_coef = 5
            else:
                bound_coef = 7

        series = series.groupby(series.index).last()
        
        if statistic is None or statistic.empty:
            statistic = series.iloc[:-1]
            last_point = series.index[-2]

        def detection_step(series, statistic, last_point):
            normalized_series = statistic[
                (statistic <= statistic.quantile(hi_percent))
                & (statistic >= statistic.quantile(low_percent))]
        
            if len(normalized_series) < 2:
                normalized_series = statistic
                statistic_std = normalized_series.std()
                mean = np.mean(normalized_series.iloc[-statistic_len_for_mean:])

            hi_bound = mean + bound_coef * statistic_std
            low_bound = mean - bound_coef * statistic_std

            points_to_check = series.loc[last_point:].iloc[:-1]
            prev_diff = (points_to_check - series.shift(1)).dropna()
            next_diff = (series.shift(-1) - points_to_check).dropna()

            checked_points = points_to_check[
                prev_diff[
                    ((prev_diff).abs() > bound_coef * statistic_std)
                    & ((prev_diff) * (next_diff) < 0)
                    & (
                        (points_to_check >= hi_bound)
                        | (points_to_check <= low_bound)
                    )
                ].index
            ]
            
            if not (statistic is None or statistic.empty):
                new_points = points_to_check.copy()
                new_points.drop_duplicates(inplace=True)
                try:
                    if statistic.iloc[-1] == new_points.iloc[0]:
                        new_points = new_points.iloc[1:]
                except IndexError:
                    pass
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
            checked_points = pd.concat([checked_points, checked_points_on_step])
            series = series[99:]
        else:
            checked_points_on_step, _, _ = detection_step(
                series=series, statistic=statistic, last_point=last_point
            )
            checked_points = pd.concat([checked_points, checked_points_on_step])

        return checked_points
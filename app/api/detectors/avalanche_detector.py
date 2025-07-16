import numpy as np
import pandas as pd


def avalanch_detector(
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
        """
        Аргументы функции обнаружения выбросов.

        Аргументы:
        series: Анализируемая часть данных
        statistic: Статистика
        last_point: Последняя точка статистики
        sensity (str): параметр чувствительности;
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

            statistics_diff = (statistic - statistic.shift(1)).dropna().abs()
            # отсекаем разности по квантилям и считаем std
            diff_std = statistics_diff[(statistics_diff <= statistics_diff.quantile(hi_percent)) * (statistics_diff >= statistics_diff.quantile(low_percent))].std()
            
            # std разностей с учетом временных интервалов
            # делим разности в статистике на временные интервалы
            statistics_diff_scaled = statistics_diff / ((statistic.index[1:] - statistic.index[:-1]).seconds / 60)
            # отсекаем разности по кванитлям (без учета временных интервалов)
            statistics_diff_scaled = statistics_diff_scaled[(statistics_diff <= statistics_diff.quantile(hi_percent)) * (statistics_diff >= statistics_diff.quantile(low_percent))]
            # считаем std
            diff_std_scaled = statistics_diff_scaled.std()
            
            clear_statistics = statistic[(statistic <= statistic.quantile(hi_percent)) * (statistic >= statistic.quantile(low_percent))]
            mean = np.mean(clear_statistics.iloc[-statistic_len_for_mean:])

            new_points = series.loc[last_point:].iloc[1:]

            points_to_check = series.loc[last_point:].iloc[1:]
            diff = (series - series.shift(1)).dropna() / ((series.index[1:] - series.index[:-1]).seconds / 60)
            prev_diff = diff.shift(1).dropna()

            # пересечение для всех трех: diff, prev_diff, points_to_check
            index_to_check = points_to_check.index.intersection(diff.index).intersection(prev_diff.index)
            diff = diff[index_to_check]
            prev_diff = prev_diff[index_to_check]
            points_to_check = points_to_check[index_to_check]

            cond_1 = (prev_diff).abs() > bound_coef * diff_std_scaled
            cond_2 = True#(prev_diff) * (diff) > 0
            cond_3 = ((points_to_check - mean).abs() > bound_coef * diff_std) + (diff.abs() > bound_coef * diff_std_scaled)
            
            checked_points = points_to_check[cond_1 & cond_2 & cond_3]

            if not (statistic is None or statistic.empty):
                new_points = points_to_check.copy()
                new_points.drop_duplicates(inplace=True)
                try:
                    if statistic.iloc[-1] == new_points[0]:
                        new_points.drop(new_points.index[0], inplace=True)
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
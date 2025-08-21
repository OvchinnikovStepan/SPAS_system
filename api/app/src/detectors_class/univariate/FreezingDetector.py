import numpy as np
import pandas as pd
from math import isclose
from api.app.src.detectors_class.base import UnivariateModels


class FreezingDetector(UnivariateModels):
    """
    Класс для обнаружения замораживания (залипания) одномерных аномалий.
    """

    MODEL_TYPE = 'UNIVARIATE_ANOMALY'

    def __init__(self, freezing_count: int = 5, rel_tol: float = 1e-9, *args, **kwargs):
        """
        Метод с инициализацией количества последних изменений, которые должны быть одинаковыми для определения замораживания (залипания).

        Аргументы:
        freezing_count (int): число замораживания (залипания);
        *args, **kwargs: дополнительные аргументы.
        """
        self.freezing_count = 5 if freezing_count is None else freezing_count
        self.rel_tol = rel_tol

    def predict(self, series: pd.Series):

        if len(series) < self.freezing_count:
            return pd.Series(dtype=float)

        series = series.sort_index().copy()
        frozen_mask = pd.Series(False, index=series.index)

        i = 0
        n = len(series)

        while i <= n - self.freezing_count:
            window = series.iloc[i:i + self.freezing_count]
            mean_val = window.mean()

            # Проверяем, является ли текущее окно замороженным
            if all(isclose(x, mean_val, rel_tol=self.rel_tol) for x in window):
                end = i + self.freezing_count - 1

                # Расширяем вправо
                while end < n - 1 and isclose(series.iloc[end + 1], mean_val, rel_tol=self.rel_tol):
                    end += 1

                frozen_mask.iloc[i:end + 1] = True
                i = end + 1  # Перескакиваем за пределы найденного участка
            else:
                i += 1

        return series[frozen_mask]

    def fit(self):
        pass

    def fit_predict(self):
        pass

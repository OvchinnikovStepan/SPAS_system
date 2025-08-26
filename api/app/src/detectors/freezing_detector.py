import numpy as np
import pandas as pd
from math import isclose

def freezing_detector(
    series: pd.Series,
    freezing_count: int = 5,
    rel_tol: float = 1e-9,
) -> pd.Series:
    """
    Обнаруживает все точки в участках "заморозки" значений.
    
    Параметры:
        series: Входной временной ряд
        freezing_count: Минимальное количество подряд идущих близких значений
        rel_tol: Относительный допуск для сравнения значений
        min_consecutive: Минимальная длина участка для включения в результат (если None, равен freezing_count)
    
    Возвращает:
        pd.Series с ВСЕМИ точками в обнаруженных участках заморозки
    """
    if len(series) < freezing_count:
        return pd.Series(dtype=float)
    
    series = series.sort_index().copy()
    frozen_mask = pd.Series(False, index=series.index)
    
    i = 0
    n = len(series)
    
    while i <= n - freezing_count:
        window = series.iloc[i:i+freezing_count]
        mean_val = window.mean()
        
        # Проверяем, является ли текущее окно замороженным
        if all(isclose(x, mean_val, rel_tol=rel_tol) for x in window):
            end = i + freezing_count - 1
            
            # Расширяем вправо
            while end < n - 1 and isclose(series.iloc[end+1], mean_val, rel_tol=rel_tol):
                end += 1
                
            frozen_mask.iloc[i:end+1] = True
            i = end + 1  # Перескакиваем за пределы найденного участка
        else:
            i += 1
    
    return series[frozen_mask]
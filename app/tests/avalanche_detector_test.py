import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from app.src.detectors.avalanche_detector import avalanch_detector
def test_avalanch_detector():
    # 1. Создаем тестовые данные
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=10000, freq='10min')
    base_values = np.cumsum(np.random.normal(0, 0.1, len(dates)))
    
    # Добавляем "лавины" - резкие изменения тренда
    avalanches = {
        5000: 5.0,   # Резкий рост
        6000: -4.5, # Резкое падение
        7000: 3.8,  # Рост
        8000: -6.2, # Падение
        9000: 4.0   # Рост
    }
    
    values = base_values.copy()
    for pos, val in avalanches.items():
        values[pos:] += val
    
    series = pd.Series(values, index=dates)
    
    # 2. Запускаем детектор
    print("Запуск детектора лавин...")
    detected = avalanch_detector(
        series=series,
        sensity='medium',
        bound_coef=8,
        statistic_len=144,
        statistic_len_for_mean=12
    )
    
    # 3. Анализ результатов
    print("\nРезультаты детекции:")
    print(f"Всего точек: {len(series)}")
    print(f"Обнаружено лавин: {len(detected)}")
    
    # 4. Визуализация
    plt.figure(figsize=(15, 7))
    
    # Исходный ряд
    plt.plot(series.index, series.values, 'b-', alpha=0.7, label='Исходный ряд')
    
    # Обнаруженные лавины
    if not detected.empty:
        plt.scatter(detected.index, detected.values, 
                   color='red', s=100, label='Обнаруженные лавины')
    
    # Реальные лавины (для проверки)
    real_avalanches = series.shift(-1).iloc[list(avalanches.keys())]
    plt.scatter(real_avalanches.index, real_avalanches.values,
               color='green', marker='x', s=200, linewidth=2, 
               label='Реальные лавины (тест)')
    
    plt.title('Детекция лавин во временном ряде')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # 5. Оценка точности
    #print("\nОценка точности:")
    #true_positives = len(set(detected.index) & set(real_avalanches.index))
    #false_positives = len(detected) - true_positives
    #false_negatives = len(avalanches) - true_positives
    #
    #print(f"Правильно обнаружено: {true_positives}/{len(avalanches)}")
    #print(f"Ложные срабатывания: {false_positives}")
    #print(f"Пропущенные лавины: {false_negatives}")

if __name__ == "__main__":
    test_avalanch_detector()
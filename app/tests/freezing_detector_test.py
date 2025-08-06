def test_freezing_detector_visual():
    """Тест с визуализацией для проверки работы алгоритма"""
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from app.src.detectors.freezing_detector import freezing_detector
    # Создаем тестовые данные
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=300, freq="5min")
    values = np.random.normal(0, 0.5, 300)
    
    # Добавляем участки заморозки разной длины
    values[50:70] = 2.0       # Длинный участок (20 точек)
    values[100:105] = -1.0    # Короткий участок (5 точек) - должен быть обнаружен
    values[120:125] = 1.5     # Еще один короткий
    values[150:180] = 0.0     # Очень длинный участок
    values[200:210] = -2.0    # Средний участок (10 точек)
    
    # Добавляем "почти замороженные" участки
    values[230:240] = 3.0
    values[235] = 3.0001      # Небольшое отклонение
    
    series = pd.Series(values, index=dates)
    
    # Запускаем детектор
    frozen = freezing_detector(series, freezing_count=5, rel_tol=1e-4)
    
    # Визуализация
    plt.figure(figsize=(15, 6))
    plt.plot(series.index, series.values, 'b-', label='Исходный ряд', alpha=0.7)
    plt.scatter(frozen.index, frozen.values, color='red', s=30, 
               label='Обнаруженная заморозка')
    
    # Разметка реальных участков заморозки
    real_frozen_ranges = [(50,70), (100,105), (120,125), (150,180), (200,210)]
    for start, end in real_frozen_ranges:
        plt.axvspan(series.index[start], series.index[end-1], 
                   color='green', alpha=0.1, label='Реальные участки' if start==50 else "")
    
    plt.title('Детекция заморозки значений (все точки)')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Проверка результатов
    print("Результаты проверки:")
    print(frozen.dtype)
    for start, end in real_frozen_ranges:
        detected = sum(series.index[i] in frozen.index for i in range(start, end))
        print(f"Участок [{start}-{end}]: обнаружено {detected}/{end-start} точек")
    
    # Проверка почти замороженного участка
    almost_frozen = series[230:240]
    detected_in_almost = sum(idx in frozen.index for idx in almost_frozen.index)
    print(f"\nПочти замороженный участок [230-240]: обнаружено {detected_in_almost} точек")

if __name__ == "__main__":
    test_freezing_detector_visual()
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from outlier_detector import outlier_detector  # Импортируем вашу функцию

# 1. Создаем тестовые данные с выбросами
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=1000, freq="H")
values = np.random.normal(0, 2, 1000)

# Добавляем явные выбросы
values[300] = 8.5    # Выброс вверх
values[455] = -7.2   # Выброс вниз
values[600] = 9.1   # Еще один выброс вверх
values[800] = 6.3   # Не такой явный выброс

series = pd.Series(values, index=dates)

# 2. Запускаем детектор выбросов
print("Запуск детектора выбросов...")
outliers = outlier_detector(
    series=series,
    outlier_sensity='None',  # Можно менять на 'low'/'high'
    bound_coef=3,
    statistic_len=144,
    statistic_len_for_mean=12
)

# 3. Выводим результаты
print("\nНайденные выбросы:")
print(outliers)

print(f"\nВсего обнаружено выбросов: {len(outliers)}")
print(f"Процент выбросов: {len(outliers)/len(series):.1%}")

# 4. Визуализация
plt.figure(figsize=(12, 6))
plt.plot(series.index, series.values, 'b-', label='Исходный ряд')

# Отмечаем выбросы красными точками
if not outliers.empty:
    plt.scatter(outliers.index, outliers.values, color='red', 
                label=f'Выбросы ({len(outliers)} шт.)')

# Добавляем легенду и заголовок
plt.title('Детекция выбросов в временном ряде')
plt.xlabel('Время')
plt.ylabel('Значение')
plt.legend()
plt.grid(True)

# Автоматически подбираем масштаб для лучшего обзора выбросов
plt.ylim(min(series.min(), -10), max(series.max(), 10))

plt.show()
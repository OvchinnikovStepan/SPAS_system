import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def test_api_avalanche_detector(url):
    """Тест детектора лавин через API"""

    # 1. Создаем тестовые данные
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=10000, freq='10min')
    base_values = np.cumsum(np.random.normal(0, 0.1, len(dates)))

    # Добавляем "лавины" - резкие изменения тренда
    avalanches = {
        5000: 5.0,  # Резкий рост
        6000: -4.5,  # Резкое падение
        7000: 3.8,  # Рост
        8000: -6.2,  # Падение
        9000: 4.0  # Рост
    }

    values = base_values.copy()
    for pos, val in avalanches.items():
        values[pos:] += val

    series = pd.Series(values, index=dates)

    # 2. Подготавливаем данные для API
    series_dict = {str(idx): float(val) for idx, val in series.items()}

    # Формируем запрос
    request_data = {
        "series": series_dict,
        "models": {
            "avalanche": {
                "sensity": "medium",
                "bound_coef": 8,
                "statistic_len": 144,
                "statistic_len_for_mean": 12
            }
        }
    }

    # 3. Отправляем запрос к API


    try:
        print("📡 Отправка данных в API...")
        response = requests.post(url, json=request_data)

        if response.status_code == 200:
            api_response = response.json()
            print("✅ Запрос к API выполнен успешно")

            # Преобразуем ответ в Series с обнаруженными лавинами
            results_data = api_response["results"]

            # Создаем Series с результатами для детектора лавин
            avalanche_results = {}
            for timestamp, detectors in results_data.items():
                if "avalanche" in detectors and detectors["avalanche"] == True:
                    avalanche_results[timestamp] = series[pd.Timestamp(timestamp)]

            detected = pd.Series(avalanche_results)
            if not detected.empty:
                detected.index = pd.to_datetime(detected.index)

            # 4. Анализ результатов
            print("\n📊 Результаты детекции:")
            print(f"Всего точек: {len(series)}")
            print(f"Обнаружено лавин: {len(detected)}")

            # 5. Визуализация
            plt.figure(figsize=(15, 7))

            # Исходный ряд
            plt.plot(series.index, series.values, 'b-', alpha=0.7, label='Исходный ряд')

            # Обнаруженные лавины
            if not detected.empty:
                plt.scatter(detected.index, detected.values,
                            color='red', s=100, label='Обнаруженные лавины')

            # Реальные лавины (для проверки)
            real_avalanche_indices = list(avalanches.keys())
            real_avalanche_points = series.iloc[real_avalanche_indices]
            plt.scatter(real_avalanche_points.index, real_avalanche_points.values,
                        color='green', marker='x', s=200, linewidth=2,
                        label='Реальные лавины (тест)')

            plt.title('Детекция лавин во временном ряде (через API)')
            plt.xlabel('Время')
            plt.ylabel('Значение')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()


        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API. Убедитесь, что сервер запущен.")
    except Exception as e:
        print(f"❌ Ошибка при выполнении теста: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🔍 Тестирование детектора лавин через API...")
    test_api_avalanche_detector()

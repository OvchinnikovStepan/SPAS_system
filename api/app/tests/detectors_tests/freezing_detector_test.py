import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def test_api_freezing_detector(url):
    """Тест детектора заморозки через API"""

    # Создаем тестовые данные
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=300, freq="5min")
    values = np.random.normal(0, 0.5, 300)

    # Добавляем участки заморозки разной длины
    values[50:70] = 2.0  # Длинный участок (20 точек)
    values[100:105] = -1.0  # Короткий участок (5 точек) - должен быть обнаружен
    values[120:125] = 1.5  # Еще один короткий
    values[150:180] = 0.0  # Очень длинный участок
    values[200:210] = -2.0  # Средний участок (10 точек)

    # Добавляем "почти замороженные" участки
    values[230:240] = 3.0
    values[235] = 3.0001  # Небольшое отклонение

    series = pd.Series(values, index=dates)

    # Подготавливаем данные для API
    series_dict = {str(idx): float(val) for idx, val in series.items()}

    # Формируем запрос
    request_data = {
        "series": series_dict,
        "models": {
            "freezing": {
                "freezing_count": 5,
                "rel_tol": 1e-4
            }
        }
    }

    # Отправляем запрос к API

    try:
        response = requests.post(url, json=request_data)

        if response.status_code == 200:
            api_response = response.json()
            print("✅ Запрос к API выполнен успешно")

            # Преобразуем ответ в DataFrame для удобства работы
            results_data = api_response["results"]

            # Создаем Series с результатами для детектора заморозки
            freezing_results = {}
            for timestamp, detectors in results_data.items():
                if "freezing" in detectors:
                    freezing_results[timestamp] = detectors["freezing"]

            freezing_series = pd.Series(freezing_results)
            freezing_series.index = pd.to_datetime(freezing_series.index)

            # Визуализация
            plt.figure(figsize=(15, 6))

            # Исходный ряд
            plt.plot(series.index, series.values, 'b-', label='Исходный ряд', alpha=0.7)

            # Обнаруженные замороженные точки
            frozen_points = series[freezing_series[freezing_series == True].index]
            if not frozen_points.empty:
                plt.scatter(frozen_points.index, frozen_points.values,
                            color='red', s=30, label='Обнаруженная заморозка', zorder=5)

            # Разметка реальных участков заморозки
            real_frozen_ranges = [(50, 70), (100, 105), (120, 125), (150, 180), (200, 210)]
            for start, end in real_frozen_ranges:
                plt.axvspan(series.index[start], series.index[end - 1],
                            color='green', alpha=0.1, label='Реальные участки' if start == 50 else "")

            plt.title('Детекция заморозки значений через API')
            plt.xlabel('Время')
            plt.ylabel('Значение')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            # Анализ результатов
            print("\n📊 Результаты проверки:")
            total_detected = len(frozen_points)
            print(f"Всего обнаружено замороженных точек: {total_detected}")

            for start, end in real_frozen_ranges:
                range_points = series.index[start:end]
                detected_in_range = sum(idx in frozen_points.index for idx in range_points)
                total_in_range = len(range_points)
                print(f"Участок [{start}-{end}]: обнаружено {detected_in_range}/{total_in_range} точек")

            # Проверка почти замороженного участка
            almost_frozen = series[230:240]
            detected_in_almost = sum(idx in frozen_points.index for idx in almost_frozen.index)
            print(f"\nПочти замороженный участок [230-240]: обнаружено {detected_in_almost} точек")

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
    print("🔍 Тестирование детектора заморозки через API...")
    test_api_freezing_detector()

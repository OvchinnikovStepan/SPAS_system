import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def test_api_outlier_detector(url):
    """Тест детектора выбросов через API"""

    # 1. Создаем тестовые данные с выбросами
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=1000, freq="h")
    values = np.random.normal(0, 2, 1000)

    # Добавляем явные выбросы
    values[300] = 8.5  # Выброс вверх
    values[455] = -7.2  # Выброс вниз
    values[600] = 9.1  # Еще один выброс вверх
    values[800] = 6.3  # Не такой явный выброс

    series = pd.Series(values, index=dates)

    print(series)

    # 2. Подготавливаем данные для API
    series_dict = {str(idx): float(val) for idx, val in series.items()}

    # Формируем запрос
    request_data = {
        "series": series_dict,
        "models": {
            "outlier": {
                "sensity": "None",  # Можно менять на 'low'/'high'
                "bound_coef": 3,
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

            # Преобразуем ответ в Series с обнаруженными выбросами
            results_data = api_response["results"]

            # Создаем Series с результатами для детектора выбросов
            outlier_results = {}
            for timestamp, detectors in results_data.items():
                if "outlier" in detectors and detectors["outlier"] == True:
                    outlier_results[timestamp] = series[pd.Timestamp(timestamp)]

            outliers = pd.Series(outlier_results)
            if not outliers.empty:
                outliers.index = pd.to_datetime(outliers.index)

            # 4. Выводим результаты
            print("\n📊 Найденные выбросы:")
            if not outliers.empty:
                print(outliers.head(10))  # Показываем первые 10
            else:
                print("Выбросы не найдены")

            print(f"\n📈 Всего обнаружено выбросов: {len(outliers)}")
            print(f"Процент выбросов: {len(outliers) / len(series):.1%}")

            # 5. Визуализация
            plt.figure(figsize=(15, 7))

            # Исходный ряд
            plt.plot(series.index, series.values, 'b-', alpha=0.7, label='Исходный ряд')

            # Отмечаем выбросы красными точками
            if not outliers.empty:
                plt.scatter(outliers.index, outliers.values,
                            color='red', s=50, label=f'Выбросы ({len(outliers)} шт.)', zorder=5)

            # Отмечаем настоящие выбросы зелеными крестами
            real_outliers_idx = [300, 455, 600, 800]
            real_outliers = series.iloc[real_outliers_idx]
            plt.scatter(real_outliers.index, real_outliers.values,
                        color='green', marker='x', s=200, linewidth=3,
                        label='Реальные выбросы', zorder=5)

            # Добавляем легенду и заголовок
            plt.title('Детекция выбросов в временном ряде (через API)')
            plt.xlabel('Время')
            plt.ylabel('Значение')
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Автоматически подбираем масштаб для лучшего обзора выбросов
            y_min = min(series.min(), outliers.min() if not outliers.empty else series.min(), -10)
            y_max = max(series.max(), outliers.max() if not outliers.empty else series.max(), 10)
            plt.ylim(y_min - 1, y_max + 1)

            plt.tight_layout()
            plt.show()

            # 6. Анализ точности
            print("\n🔍 Анализ точности:")
            if not outliers.empty:
                detected_indices = set(outliers.index)
                real_indices = set(real_outliers.index)

                true_positives = len(detected_indices & real_indices)
                false_positives = len(detected_indices - real_indices)
                false_negatives = len(real_indices - detected_indices)

                print(f"Правильно обнаружено: {true_positives}/4")
                print(f"Ложные срабатывания: {false_positives}")
                print(f"Пропущенные выбросы: {false_negatives}")

                if len(real_outliers) > 0:
                    recall = true_positives / len(real_outliers)
                    print(f"Полнота (Recall): {recall:.1%}")

                if len(outliers) > 0:
                    precision = true_positives / len(outliers)
                    print(f"Точность (Precision): {precision:.1%}")

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
    print("🔍 Тестирование детектора выбросов через API...")
    test_api_outlier_detector()

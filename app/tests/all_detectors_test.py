from app.tests.outlier_detector_test import test_api_outlier_detector
from app.tests.avalanche_detector_test import test_api_avalanche_detector
from app.tests.freezing_detector_test import test_api_freezing_detector


url = "http://127.0.0.1:8000/api/detectors"

if __name__ == "__main__":
    print("🔍 Тестирование детектора лавин через API...")
    test_api_avalanche_detector(url)
    print("🔍 Тестирование детектора заморозки через API...")
    test_api_freezing_detector(url)
    print("🔍 Тестирование детектора выбросов через API...")
    test_api_outlier_detector(url)
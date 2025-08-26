import importlib
import logging

logger = logging.getLogger(__name__)


def validate_basic_functionality():
    """Проверка базовой функциональности детекторов"""
    import pandas as pd
    import numpy as np

    # Создаем тестовые данные
    test_series = pd.Series(
        np.random.normal(0, 1, 100),
        index=pd.date_range(start="2023-01-01", periods=100, freq="1h")
    )

    from api.app.config import DETECTORS

    for detector_name in DETECTORS.keys():
        module_path = DETECTORS[detector_name]["path"]

        try:
            # Импортируем и запускаем тест
            if '.' in module_path:
                module_name, func_name = module_path.rsplit('.', 1)
            else:
                module_name = module_path
                func_name = "detector"

            module = importlib.import_module(module_name)
            func = getattr(module, func_name)

            # Минимальный тест с параметрами по умолчанию
            test_params = get_default_params(detector_name)
            result = func(test_series, **test_params)

            # Проверяем результат
            if result is None:
                raise ValueError(f"Детектор '{detector_name}' вернул None")

            logger.info(f"✅ Базовый тест детектора '{detector_name}' пройден")

        except Exception as e:
            logger.warning(f"⚠️  Базовый тест детектора '{detector_name}' не пройден: {e}")
            # Не прерываем запуск, но логируем предупреждение

    return True


def get_default_params(detector_name):
    """Возвращает параметры по умолчанию для детектора"""
    defaults = {
        "avalanche": {"sensity": "medium", "bound_coef": 8},
        "freezing": {"freezing_count": 5, "rel_tol": 1e-4},
        "outlier": {"sensity": "None", "bound_coef": 3}
    }
    return defaults.get(detector_name, {})
import os
import importlib
import logging

logger = logging.getLogger(__name__)


def validate_detector_functions():
    """Проверка наличия необходимых функций в модулях детекторов"""
    from app.config import DETECTORS

    required_function = "detector"  # или другое имя функции

    for detector_name in DETECTORS.keys():
        try:
            module_path = DETECTORS[detector_name]["path"]
            if '.' in module_path:
                module_name, func_name = module_path.rsplit('.', 1)
            else:
                module_name = module_path
                func_name = required_function

            # Импортируем модуль
            module = importlib.import_module(module_name)

            # Проверяем наличие функции
            if not hasattr(module, func_name):
                raise AttributeError(f"Функция '{func_name}' не найдена в модуле '{module_name}'")

            # Проверяем, что это callable
            func = getattr(module, func_name)
            if not callable(func):
                raise TypeError(f"'{func_name}' в модуле '{module_name}' не является функцией")

            logger.info(f"✅ Функция '{func_name}' доступна в детекторе '{detector_name}'")

        except Exception as e:
            raise ValueError(f"❌ Ошибка проверки функции детектора '{detector_name}': {e}")

    logger.info("✅ Все функции детекторов доступны")
    return True

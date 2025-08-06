import os
import importlib
import logging

logger = logging.getLogger(__name__)


def validate_detector_modules():
    """Проверка наличия и доступности модулей детекторов"""
    from app.config import DETECTORS

    for detector_name in DETECTORS.keys():
        module_path = DETECTORS[detector_name]["path"]
        try:
            # Разделяем путь на модуль и функцию
            if '.' in module_path:
                module_name, func_name = module_path.rsplit('.', 1)
            else:
                raise ValueError(f"Некорректный формат пути: {module_path}")

            # Попытка импорта модуля
            importlib.import_module(module_name)
            logger.info(f"✅ Модуль детектора '{detector_name}' доступен: {module_name}")

        except ImportError as e:
            raise ImportError(f"❌ Модуль детектора '{detector_name}' не найден: {module_path}. Ошибка: {e}")
        except Exception as e:
            raise ValueError(f"❌ Ошибка проверки детектора '{detector_name}': {e}")

    logger.info("✅ Все модули детекторов доступны")
    return True

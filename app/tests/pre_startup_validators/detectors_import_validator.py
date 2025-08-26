import os
import importlib
import logging

logger = logging.getLogger(__name__)


def validate_detector_imports():
    try:
        # Попытка импорта
        from app.config import DETECTORS

        # Проверка типов
        if not isinstance(DETECTORS, dict):
            logger.error(f"❌ DETECTORS должен быть dict, получено {type(DETECTORS)}")
            raise TypeError("Некорректный тип DETECTORS - должен быть словарем")

        # Проверка на пустоту
        if len(DETECTORS) == 0:
            logger.warning("⚠️ Словарь DETECTORS пуст")
            raise ValueError("Словарь доступных детекторов пуст")

        logger.info(f"📊 Найдено {len(DETECTORS)} детекторов:")
        for name in DETECTORS.keys():
            logger.info(f"  • {name}: {DETECTORS[name]['path']}")
            logger.info(f"      Описание: {DETECTORS[name]['description']}")

        logger.info("✅ Конфигурация детекторов проверена успешно")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта конфигурации: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка конфигурации детекторов: {e}")
        raise






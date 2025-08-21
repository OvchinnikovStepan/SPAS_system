import os
import importlib
import logging

logger = logging.getLogger(__name__)


def validate_dependencies():
    """Проверка необходимых зависимостей"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pandas",
        "numpy",
        "pydantic"
    ]

    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"✅ Пакет '{package}' доступен")

            return True
        except ImportError:
            raise ImportError(f"❌ Требуемый пакет '{package}' не установлен")
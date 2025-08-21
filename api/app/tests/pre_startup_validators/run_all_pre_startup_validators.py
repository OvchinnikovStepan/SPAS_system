import logging
from api.app.tests.pre_startup_validators.basic_functionality_validator import validate_basic_functionality
from api.app.tests.pre_startup_validators.dependencies_validator import validate_dependencies
from api.app.tests.pre_startup_validators.detectors_functions_validator import validate_detector_functions
from api.app.tests.pre_startup_validators.detectors_import_validator import validate_detector_imports
from api.app.tests.pre_startup_validators.detectors_modules_validator import validate_detector_modules

logger = logging.getLogger(__name__)


def run_pre_startup_validations():
    """Запуск всех предстартовых проверок"""
    try:
        logger.info("🚀 Начало предстартовых проверок...")

        # Проверки в порядке важности
        if validate_dependencies() and \
                validate_detector_imports() and \
                validate_detector_modules() and \
                validate_detector_functions() and \
                validate_basic_functionality():
            logger.info("✅ Все предстартовые проверки пройдены успешно")
            return True
        else:
            raise

    except Exception as e:
        logger.critical(f"❌ Предстартовые проверки не пройдены: {e}")
        raise SystemExit(1)


# Вызов при запуске приложения
if __name__ == "__main__":
    run_pre_startup_validations()
    # Запуск FastAPI приложения

from fastapi import FastAPI
import logging
from app.src.middleware import add_middlewares
from app.src.api.detectors_router import router as detectors_router
from app.tests.pre_startup_validators.run_all_pre_startup_validators import run_pre_startup_validations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SPAS System API")


# Запуск проверок перед стартом
@app.on_event("startup")
async def startup_event():
    """Выполняется при запуске приложения"""
    try:
        run_pre_startup_validations()
        logger.info("🚀 Приложение готово к работе")
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка при запуске: {e}")
        raise


app.include_router(router=detectors_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "SPAS timeseries analyzer"}

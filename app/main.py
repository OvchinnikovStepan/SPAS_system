from fastapi import FastAPI
import logging
import coloredlogs
import uvicorn
from contextlib import asynccontextmanager
from app.src.middleware import add_middlewares
from app.settings import settings
from app.src.api.detectors_router import router as detectors_router
from app.tests.pre_startup_validators.run_all_pre_startup_validators import run_pre_startup_validations

coloredlogs.install(
    level='INFO',
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    field_styles={
        'asctime': {'color': 'green'},
        'name': {'color': 'blue'},
        'levelname': {'color': 'yellow', 'bold': True}
    },
    level_styles={
        'debug': {'color': 'white'},
        'info': {'color': 'blue'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'red', 'bold': True}
    }
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, который выполняется ПЕРЕД запуском приложения (startup)
    try:
        run_pre_startup_validations()
        logger.info("🚀 Приложение готово к работе")
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка при запуске: {e}")
        raise

    yield  # Здесь работает приложение

    # Код, который выполняется ПОСЛЕ остановки приложения (shutdown)
    logger.info("🛑 Приложение остановлено")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug,
)
add_middlewares(app)

app.include_router(router=detectors_router, prefix="/api")


@app.get("/",
         summary="Проверка запуска",
         status_code=200,
         description="Проверка получения ответа от API",
         response_description="Строка с текстом для проверки запуска API",
         tags=['Root']
         )
async def root():
    return {"message": "SPAS timeseries analyzer"}


@app.get("/health",
         summary="Основная информация об API",
         status_code=200,
         description="Получение основной информации о развернутой версии программы",
         response_description="Название программы, версия, режим работы и порт в строковом формате",
         tags=['Root']
         )
def health_check():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "port": settings.port
    }

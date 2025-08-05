from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pandas as pd
import logging
from app.src.schemas.response_schema import SResponse
from app.src.schemas.request_schema import SRequest
from app.src.services.routing_func import routing_func

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/detectors', tags=['Детекторы'])

def check_detectors_config() -> Dict[str, Any]:
    """Проверяет конфигурацию и возвращает её при успехе"""

    try:
        # Попытка импорта
        from app.config import DETECTORS, DETECTORS_DESCRIPTION
        logger.info("✅ Файлы конфигурации успешно импортированы")

    except ImportError as e:
        logger.error(f"❌ Не удалось импортировать конфигурацию: {e}")
        raise ImportError("Файл конфигурации не найден или ошибка импорта")

    # Проверка типов
    if not isinstance(DETECTORS, dict):
        logger.error(f"❌ DETECTORS должен быть dict, получено {type(DETECTORS)}")
        raise TypeError("Некорректный тип DETECTORS - должен быть словарем")

    if not isinstance(DETECTORS_DESCRIPTION, dict):
        logger.error(f"❌ DETECTORS_DESCRIPTION должен быть dict, получено {type(DETECTORS_DESCRIPTION)}")
        raise TypeError("Некорректный тип DETECTORS_DESCRIPTION - должен быть словарем")

    # Проверка на пустоту
    if len(DETECTORS) == 0:
        logger.warning("⚠️ Словарь DETECTORS пуст")
        raise ValueError("Словарь доступных детекторов пуст")

    if len(DETECTORS_DESCRIPTION) == 0:
        logger.warning("⚠️ Словарь DETECTORS_DESCRIPTION пуст")
        raise ValueError("Словарь описаний детекторов пуст")

    # Проверка соответствия ключей
    detectors_keys = set(DETECTORS.keys())
    descriptions_keys = set(DETECTORS_DESCRIPTION.keys())

    if detectors_keys != descriptions_keys:
        missing_in_descriptions = detectors_keys - descriptions_keys
        missing_in_detectors = descriptions_keys - detectors_keys

        error_msg = "Несоответствие ключей между DETECTORS и DETECTORS_DESCRIPTION: "
        if missing_in_descriptions:
            error_msg += f"Отсутствуют описания для: {list(missing_in_descriptions)}. "
        if missing_in_detectors:
            error_msg += f"Отсутствуют детекторы для: {list(missing_in_detectors)}."

        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    # Проверка содержимого DETECTORS
    for name, config in DETECTORS.items():
        if not isinstance(config, str) or not config.strip():
            logger.error(f"❌ Некорректная конфигурация для детектора '{name}': {config}")
            raise ValueError(f"Некорректная конфигурация детектора '{name}' - должен быть непустой строкой")

    # Проверка содержимого DETECTORS_DESCRIPTION
    for name, description in DETECTORS_DESCRIPTION.items():
        if not isinstance(description, str) or not description.strip():
            logger.error(f"❌ Некорректное описание для детектора '{name}': {description}")
            raise ValueError(f"Некорректное описание детектора '{name}' - должно быть непустой строкой")

    logger.info(f"📊 Найдено {len(DETECTORS)} детекторов:")
    for name, config in DETECTORS.items():
        logger.info(f"  • {name}: {config}")
        logger.info(f"      Описание: {DETECTORS_DESCRIPTION[name]}")

    return DETECTORS_DESCRIPTION


@router.get("",
            summary="Все детекторы",
            status_code=200,
            description="Получение списка всех детекторов",
            response_description="Список всех детекторов с их описанием",
            responses={
                200: {"description": "Список детекторов успешно получен"},
                500: {"description": "Не удалось получить список детекторов"}
            }
)
async def get_detectors() -> Dict[str, str]:
    """
        Возвращает список названий всех доступных детекторов.
    """
    try:
        detectors = check_detectors_config()
        return detectors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка конфигурации: {str(e)}")


@router.post("",
             summary="Провести проверку по детекторам",
             response_model=SResponse,
             description="Принимает временной ряд и запускает указанные детекторы аномалий",
             response_description="DataFrame с результатами анализа по каждому детектору",
             status_code=200
)
def run_detectors(request: SRequest) -> SResponse:
    try:
        # Преобразуем входной словарь в Series
        series = pd.Series(request.series)
        series.index = pd.to_datetime(series.index)

        # Запускаем детекторы
        detector_results = routing_func(series=series, models=request.models)

        # Создаём общий DataFrame с результатами
        if detector_results:
            df_result = pd.DataFrame(index=series.index)
            for detector_name, result in detector_results.items():
                df_result[detector_name] = result

            # Преобразуем в ответ
            return SResponse(
                index=[str(idx) for idx in df_result.index],
                columns=list(df_result.columns),
                data=df_result.values.tolist()
            )
        else:
            # Если нет результатов, возвращаем пустую структуру
            return SResponse(
                index=[str(idx) for idx in series.index],
                columns=[],
                data=[[] for _ in series.index]
            )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при анализе временного ряда: {str(e)}"
        )
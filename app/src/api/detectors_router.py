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
        from app.config import DETECTORS
        logger.info("✅ Файл конфигурации успешно импортирован")

    except ImportError as e:
        logger.error(f"❌ Не удалось импортировать конфигурацию: {e}")
        raise ImportError("Файл конфигурации не найден или ошибка импорта")

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
        logger.info(f"  • {name}: {DETECTORS[name]["path"]}")
        logger.info(f"      Описание: {DETECTORS[name]["description"]}")

    return DETECTORS


@router.get("",
            summary="Все детекторы",
            status_code=200,
            description="Получение списка всех детекторов",
            response_description="Список всех детекторов с их описанием",
            )
async def get_detectors() -> Dict[str, Any]:
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
async def run_detectors(request: SRequest) -> SResponse:
    try:
        # Преобразуем входной словарь в Series
        series = pd.Series(request.series)
        series.index = pd.to_datetime(series.index)

        # Запускаем детекторы
        detector_results = routing_func(series=series, models=request.models)

        if detector_results:
            # Создаём DataFrame с False для всех точек по умолчанию
            df_result = pd.DataFrame(False, index=series.index, columns=detector_results.keys(), dtype=bool)

            # Заполняем True для выделенных точек
            for detector_name, result in detector_results.items():
                if isinstance(result, pd.Series):
                    # Если результат - Series с индексами выделенных точек
                    df_result.loc[result.index, detector_name] = True
                elif isinstance(result, (list, pd.Index)):
                    # Если результат - список индексов
                    df_result.loc[result, detector_name] = True

            # Преобразуем в формат {timestamp: {detector: result}}
            results_dict = {}
            for idx in df_result.index:
                results_dict[str(idx)] = df_result.loc[idx].to_dict()

            return SResponse(results=results_dict)
        else:
            # Если нет результатов, возвращаем False для всех детекторов
            results_dict = {}
            detector_names = list(request.models.keys())  # Используем запрошенные детекторы

            for idx in series.index:
                results_dict[str(idx)] = {detector: False for detector in detector_names}

            return SResponse(results=results_dict)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при анализе временного ряда: {str(e)}"
        )

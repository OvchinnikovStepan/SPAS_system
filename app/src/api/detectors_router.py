from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pandas as pd
import logging
from app.src.schemas.detector_response_schema import SDetectorResponse
from app.src.schemas.detector_request_schema import SDetectorRequest
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
        filtered_response = {}
        for detector_name, detector_config in detectors.items():
            # Исключаем ключ "path"
            filtered_config = {k: v for k, v in detector_config.items() if k != "path"}
            filtered_response[detector_name] = filtered_config

        return filtered_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка конфигурации: {str(e)}")


@router.post("",
             summary="Провести проверку по детекторам",
             response_model=SDetectorResponse,
             description="Принимает временной ряд и запускает указанные детекторы аномалий",
             response_description="DataFrame с результатами анализа по каждому детектору",
             status_code=200
             )
async def run_detectors(request: SDetectorRequest) -> SDetectorResponse:
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

            return SDetectorResponse(results=results_dict)
        else:
            # Если нет результатов, возвращаем False для всех детекторов
            results_dict = {}
            detector_names = list(request.models.keys())  # Используем запрошенные детекторы

            for idx in series.index:
                results_dict[str(idx)] = {detector: False for detector in detector_names}

            return SDetectorResponse(results=results_dict)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при анализе временного ряда: {str(e)}"
        )

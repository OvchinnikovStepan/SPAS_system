from fastapi import APIRouter, HTTPException
from typing import List
import logging
from api.app.src.schemas.data_file_schema import SFileInfo
from api.app.src.schemas.data_request_schema import SDataRequest
from api.app.src.schemas.data_point_schema import SDataPoint
from api.app.src.services.data_service.data_service import get_available_files, get_data_slice

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/data', tags=['Данные'])


@router.get("",
            summary="Все теги",
            status_code=200,
            description="Получение списка всех доступных тегов",
            response_description="Список всех доступных тегов",
            )
async def get_tags() -> List[SFileInfo]:
    """
        Возвращает список всех доступных тегов.
    """
    try:
        files = get_available_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка конфигурации: {str(e)}")


@router.post("",
             summary="Провести проверку по детекторам",
             description="Принимает временной ряд и запускает указанные детекторы аномалий",
             response_description="DataFrame с результатами анализа по каждому детектору",
             status_code=200
             )
async def run_detectors(request: SDataRequest) -> List[SDataPoint]:
    try:
        return get_data_slice(request)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при получении временного отрезка: {str(e)}"
        )

from typing import Dict, Any, Union
from importlib import import_module
import logging
import pandas as pd
from app.config import DETECTORS

logger = logging.getLogger(__name__)


def routing_func(
        series: pd.Series,
        models: Dict[str, Dict[str, Any]]
) -> Dict[str, Union[pd.Series, pd.DataFrame]]:
    """
    Маршрутизирует вызовы к различным детекторам аномалий.
    
    Args:
        series: Фрейм с данными для анализа
        models: Словарь с конфигурацией детекторов в формате:
               {
                   "detector_type1": {"param1": value1, ...},
                   "detector_type2": {"param2": value2, ...}
               }
               
    Returns:
        Словарь с результатами работы детекторов в формате:
        {
            "detector_type1": result1,
            "detector_type2": result2
        }
        
    Raises:
        ValueError: Если указан неизвестный тип детектора
        RuntimeError: Если при выполнении детектора возникла ошибка
    """
    results = {}

    for detector_type, params in models.items():
        try:
            if detector_type not in DETECTORS:
                raise ValueError(f"Unknown detector type: {detector_type}. Available: {list(DETECTORS.keys())}")

            module_path, func_name = DETECTORS[detector_type]["path"].rsplit('.', 1)
            detector_module = import_module(module_path)
            detector_func = getattr(detector_module, func_name)

            logger.info(f"Executing {detector_type} detector with params: {params}")
            results[detector_type] = detector_func(series=series, **params)

        except Exception as e:
            logger.error(f"Error in {detector_type} detector: {str(e)}")
            raise RuntimeError(f"Detector {detector_type} execution failed") from e

    return results

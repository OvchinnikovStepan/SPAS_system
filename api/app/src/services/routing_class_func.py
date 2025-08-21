from typing import Dict, Any, Union
import logging
import pandas as pd
import inspect
from api.app.config import DETECTORS_CLASS, DETECTORS_PATH

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
            if detector_type not in DETECTORS_CLASS:
                raise ValueError(f"Unknown detector type: {detector_type}. Available: {list(DETECTORS_CLASS.keys())}")

            module_path, class_name = DETECTORS_PATH + "." + DETECTORS_CLASS[detector_type]["name"], DETECTORS_CLASS[detector_type]["name"]
            detector_module = __import__(module_path, fromlist=[class_name])
            DetectorClass = getattr(detector_module, class_name)

            detector_instance = DetectorClass(**params)

            # Получаем сигнатуру метода predict
            predict_signature = inspect.signature(detector_instance.predict)
            required_params = list(predict_signature.parameters.keys())

            # Подготавливаем аргументы для вызова
            predict_kwargs = {'series': series}

            # Добавляем дополнительные параметры, если они требуются
            if 'statistic' in required_params:
                predict_kwargs['statistic'] = params.get('statistic', None)
            if 'last_point' in required_params:
                predict_kwargs['last_point'] = params.get('last_point', None)

            # Выполняем предсказание
            logger.info(f"Executing {detector_type} detector with params: {params}")
            result = detector_instance.predict(**predict_kwargs)

            # Обработка результатов
            if isinstance(result, tuple):
                # Берем только первый элемент (статус аномалии)
                results[detector_type] = result[0]
            else:
                results[detector_type] = result

        except Exception as e:
            logger.error(f"Error in {detector_type} detector: {str(e)}")
            raise RuntimeError(f"Detector {detector_type} execution failed") from e

    return results

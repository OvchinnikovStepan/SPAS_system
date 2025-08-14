import os
from typing import Any, Dict, Mapping, Optional, Union
import pandas as pd
import requests
from .recording_parameters import get_detector_parameters_for_api


DETECTORS_URL = os.getenv("DETECTORS_URL", "http://172.20.10.3:8000/api/detectors")


def _series_to_payload_dict(
    df: "pd.DataFrame",
    value_column: Optional[str] = None,
  ) -> Dict[str, float]:
    """Преобразует DataFrame с DatetimeIndex в словарь
    """
    series = df[value_column]
    return {ts.isoformat(): float(val) for ts, val in series.items()}


def send_detectors_request(
    df: "pd.DataFrame",
    value_column: Optional[str] = None,
    timeout_sec: int = 15,
  ) -> Dict[str, Any]:
    """Формирует payload и отправляет POST-запрос в API детекторов.

    Параметры:
      - df: DataFrame с DatetimeIndex; значения датчика в числовом столбце
      - value_column: имя столбца (если не указан — берется первый числовой)
      - timeout_sec: таймаут запроса в секундах

    Возвращает:
      - JSON-ответ сервера как dict
    """
    try:
        models = get_detector_parameters_for_api()
    except Exception as e:
        print(e, "get_detector_parameters_for_api")
    try:
        series_payload = _series_to_payload_dict(df, value_column=value_column)
    except Exception as e:
        print(e, "_series_to_payload_dict")
        

    payload: Dict[str, Any] = {
        "models": models,
        "series": series_payload,
    }
    print(payload)
    resp = requests.post(
        DETECTORS_URL,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout_sec,
    )
    resp.raise_for_status()
    return resp.json()



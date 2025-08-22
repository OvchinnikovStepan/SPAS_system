import os
from typing import Any, Dict, Mapping, Optional, Union
import pandas as pd
import requests
import streamlit as st
from .recording_parameters import get_detector_parameters_for_api

API_BASE = st.secrets['API_URL'].rstrip('/')
DETECTORS_URL = f"{API_BASE}/detectors"


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
    models = get_detector_parameters_for_api()
    series_payload = _series_to_payload_dict(df, value_column=value_column)

    payload: Dict[str, Any] = {
        "models": models,
        "series": series_payload,
    }
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



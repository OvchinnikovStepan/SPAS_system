import os
from typing import Any, Dict, Union
import requests
import streamlit as st


API_BASE = st.secrets['API_URL'].rstrip('/')
DETECTORS_URL = f"{API_BASE}/detectors"

class ParametersRequestError(Exception):
    """Исключение для ошибок при запросе параметров."""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

def parse_request() -> Dict[str, Any]:
    """Выполняет запрос к бэкенду и возвращает JSON как словарь."""
    try:
        resp = requests.get(
            DETECTORS_URL,
            headers={'accept': 'application/json'},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise ParametersRequestError("Превышено время ожидания запроса к серверу")
    except requests.exceptions.ConnectionError:
        raise ParametersRequestError("Ошибка подключения к серверу")
    except requests.exceptions.HTTPError as e:
        raise ParametersRequestError(f"HTTP ошибка: {e}")
    except requests.exceptions.RequestException as e:
        raise ParametersRequestError(f"Ошибка запроса: {e}")
    except Exception as e:
        raise ParametersRequestError(f"Неожиданная ошибка при запросе: {e}")

def avalanche_parameters(response: Dict[str, Any]) -> Dict[str, Any]:
    """Извлекает параметры для детектора лавин."""
    try:
        if "avalanche" not in response:
            raise ParametersRequestError("В ответе отсутствуют параметры для детектора лавин")
        if "params" not in response["avalanche"]:
            raise ParametersRequestError("В ответе детектора лавин отсутствуют параметры")
        return response["avalanche"]["params"]
    except KeyError as e:
        raise ParametersRequestError(f"Ошибка структуры данных для детектора лавин: {e}")

def freezing_parameters(response: Dict[str, Any]) -> Dict[str, Any]:
    """Извлекает параметры для детектора замерзания."""
    try:
        if "freezing" not in response:
            raise ParametersRequestError("В ответе отсутствуют параметры для детектора замерзания")
        if "params" not in response["freezing"]:
            raise ParametersRequestError("В ответе детектора замерзания отсутствуют параметры")
        return response["freezing"]["params"]
    except KeyError as e:
        raise ParametersRequestError(f"Ошибка структуры данных для детектора замерзания: {e}")

def outlier_parameters(response: Dict[str, Any]) -> Dict[str, Any]:
    """Извлекает параметры для детектора выбросов."""
    try:
        if "outlier" not in response:
            raise ParametersRequestError("В ответе отсутствуют параметры для детектора выбросов")
        if "params" not in response["outlier"]:
            raise ParametersRequestError("В ответе детектора выбросов отсутствуют параметры")
        return response["outlier"]["params"]
    except KeyError as e:
        raise ParametersRequestError(f"Ошибка структуры данных для детектора выбросов: {e}")

def request_parameters() -> Union[Dict[str, Dict[str, Any]], Dict[str, str]]:
    """Возвращает словарь параметров по всем детекторам или информацию об ошибке.

    Возвращает:
        - При успехе: словарь с параметрами детекторов
        - При ошибке: словарь с информацией об ошибке {"error": "описание ошибки"}

    Пример структуры возврата при успехе:
    {
        "avalanche": {...},
        "freezing": {...},
        "outlier": {...}
    }

    Пример структуры возврата при ошибке:
    {
        "error": "описание ошибки"
    }
    """
    try:
        response = parse_request()
        
        # Проверяем, что ответ содержит все необходимые детекторы
        required_detectors = ["avalanche", "freezing", "outlier"]
        for detector in required_detectors:
            if detector not in response:
                return {"error": f"В ответе отсутствуют данные для детектора {detector}"}
        
        return {
            "avalanche": avalanche_parameters(response),
            "freezing": freezing_parameters(response),
            "outlier": outlier_parameters(response),
        }
    except ParametersRequestError as e:
        return {"Ошибка1 error": e.message}
    except Exception as e:
        return {"Ошибка2 error": f"Неожиданная ошибка: {e}"}

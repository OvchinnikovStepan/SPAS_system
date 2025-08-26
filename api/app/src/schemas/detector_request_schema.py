from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Union
import pandas as pd


class SDetectorRequest(BaseModel):
    series: Dict[str, float] = Field(..., description="Фрейм с данными для анализа")
    models: Dict[str, Dict[str, Any]] = Field(..., description="модели и соответствующие им параметры")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "series": {
                    "2023-01-01T00:00:00": 10.5,
                    "2023-01-01T00:10:00": 12.3,
                    "2023-01-01T00:20:00": 100.0
                },
                "models": {
                    "avalanche": {
                        "sensity": "medium",
                        "bound_coef": 8,
                        "statistic_len": 144,
                        "statistic_len_for_mean": 12
                    },
                    "outlier": {
                        "sensity": "None",  # Можно менять на 'low'/'high'
                        "bound_coef": 3,
                        "statistic_len": 144,
                        "statistic_len_for_mean": 12
                    },
                    "freezing": {
                        "freezing_count": 5,
                        "rel_tol": 1e-4
                    }
                }
            }
        }
    )

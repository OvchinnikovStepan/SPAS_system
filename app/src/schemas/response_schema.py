from pydantic import BaseModel, Field
from typing import Dict, Any, Union

class SResponse(BaseModel):
    results: Dict[str, Dict[str, Union[float, int, bool, None]]] \
        = Field(..., description="Результаты прогона детекторов")

    class Config:
        json_schema_extra = {
            "example": {
                "results": {
                    "2023-01-01T00:00:00": {
                        "isolation_forest": False,
                        "z_score": False,
                        "avalanche_detector": False
                    },
                    "2023-01-01T00:10:00": {
                        "isolation_forest": False,
                        "z_score": True,
                        "avalanche_detector": False
                    }
                }
            }
        }
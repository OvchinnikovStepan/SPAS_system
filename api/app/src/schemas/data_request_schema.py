from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from api.app.src.schemas.isodate_query import ISODateTime


class SDataRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag": "spb",
                "dateStart": "2025-03-09T08:49:00",
                "dateEnd": "2025-03-10T10:27:00"
            }
        }
    )

    tag: str = Field(..., description="Тег датчика для запроса данных")
    dateStart: Optional[ISODateTime] = Field(None, title="Время начала отрезка", description="ISO 8601 without timezone")
    dateEnd: Optional[ISODateTime] = Field(None, title="Время конца отрезка", description="ISO 8601 without timezone")

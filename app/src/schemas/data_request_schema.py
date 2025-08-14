from pydantic import BaseModel, Field
from typing import Optional, Annotated
from app.src.schemas.isodate_query import ISODateTime


class SDataRequest(BaseModel):
    tag: str = Field(..., description="Тег датчика для запроса данных")
    dateStart: Optional[ISODateTime] = Field(None, description="Время начала отрезка")
    dateEnd: Optional[ISODateTime] = Field(None, description="Время конца отрезка")

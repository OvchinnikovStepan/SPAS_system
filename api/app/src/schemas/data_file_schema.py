from pydantic import BaseModel, Field
from typing import Optional
from api.app.src.schemas.isodate_query import ISODateTime


class SFileInfo(BaseModel):
    filename: str = Field(..., description="Тег", alias="tag")
    start: Optional[ISODateTime] = Field(None, title="Начальная дата")
    end: Optional[ISODateTime] = Field(None, title="Конечная дата")
    count: int = 0

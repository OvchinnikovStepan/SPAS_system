from pydantic import BaseModel, Field
from api.app.src.schemas.isodate_query import ISODateTime


class SDataPoint(BaseModel):
    d: ISODateTime  # ISO 8601 timestamp
    v: float = Field(..., description="Значение")

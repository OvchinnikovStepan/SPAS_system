from fastapi import Query
from typing import Annotated

ISODateTime = Annotated[
    str,
    Query(
        description="Дата и время в формате ISO 8601 (например: 2025-03-10T08:49:05 или 2025-07-02T05:58:31.016006)",
        example="2025-03-10T08:49:05",
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}:\d{2}|Z)?$"
    )
]
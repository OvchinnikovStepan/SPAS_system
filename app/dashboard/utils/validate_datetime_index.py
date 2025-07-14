from .get_date_formats import get_date_formats
import pandas as pd


def validate_datetime_index(df: pd.DataFrame) -> None:
    """Проверяет, что индекс датафрейма — это даты, и что они соответствуют одному из поддерживаемых форматов."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Индекс датафрейма должен быть DatetimeIndex (датой)")
    # Проверяем, что все даты в индексе соответствуют одному из форматов
    date_formats = get_date_formats()
    for fmt in date_formats:
        try:
            pd.to_datetime(df.index.strftime(fmt), format=fmt)
            return  # хотя бы один формат подошёл
        except Exception:
            continue
    raise ValueError(f"Индекс не соответствует поддерживаемым форматам дат: {date_formats}")
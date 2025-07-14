from typing import List


def get_date_formats() -> List[str]:
    """Возвращает список поддерживаемых форматов дат"""
    return [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%Y/%m/%d',
        '%m/%d/%Y'
    ]
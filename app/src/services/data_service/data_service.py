from pathlib import Path
from app.settings import settings
from datetime import datetime
from typing import List
from fastapi import HTTPException
import json
from app.src.schemas.data_file_schema import SFileInfo
from app.src.schemas.data_point_schema import SDataPoint
from app.src.schemas.data_request_schema import SDataRequest
import logging
import re

logger = logging.getLogger(__name__)

DATA_DIR = Path(settings.data_dir)


def parse_datetime(dt_str: str) -> datetime:
    """Парсинг ISO формата даты"""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception as e:
        raise ValueError(f"Неверный формат даты: {dt_str}, {e}")


def load_json_file(filepath: Path) -> List[SDataPoint]:
    """Загружает файл в формате JSON массива"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if isinstance(json_data, list):
                for item in json_data:
                    if 'd' in item and 'v' in item:
                        data.append(SDataPoint(
                            d=item["d"],
                            v=item["v"]
                        ))
            else:
                raise ValueError("Файл должен содержать JSON-массив")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Ошибка парсинга JSON в файле {filepath}: {e}")
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения файла {filepath}: {e}")
    return data


def extract_tag_from_filename(filename: str) -> str:
    """Извлекает тег из имени файла"""
    if filename.endswith('.json'):
        filename = filename[:-5]

    pattern = r'^tag_(.+)_core$'
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    return filename


def get_file_metadata(filepath: Path) -> SFileInfo:
    """Получает метаданные файла: начало, конец, количество записей"""
    data = load_json_file(filepath)

    if not data:
        tag = extract_tag_from_filename(filepath.name)
        return SFileInfo(
            filename=filepath.name,
            tag=tag
        )

    try:
        # Используем точечную нотацию для доступа к полям Pydantic модели
        sorted_data = sorted(data, key=lambda x: x.d)
        start = sorted_data[0].d
        end = sorted_data[-1].d
        count = len(data)

        tag = extract_tag_from_filename(filepath.name)

        return SFileInfo(
            filename=filepath.name,
            tag=tag,
            start=start,
            end=end,
            count=count
        )

    except Exception as e:
        # Даже в случае ошибки возвращаем базовую информацию
        tag = extract_tag_from_filename(filepath.name)
        logger.error(f"Не удалось обработать временные данные файла {filepath.name}: {e}")
        return SFileInfo(
            filename=filepath.name,
            tag=tag
        )


def get_available_files():
    """
    Возвращает список всех доступных JSON-файлов и их временные диапазоны.
    """
    files_info = []

    for file_path in DATA_DIR.glob("*.json"):
        try:
            file_info = get_file_metadata(file_path)
            files_info.append(file_info)
        except Exception as e:
            logger.error(f"❌ Ошибка обработки файла {file_path}: {e}")
            continue

    return files_info


def get_data_slice(request: SDataRequest) -> List[SDataPoint]:
    """
    Возвращает отрезок данных из указанного JSON-файла.
    """
    filename = f"tag_{request.tag}_core.json"
    start = request.dateStart
    end = request.dateEnd

    file_path = DATA_DIR / filename

    # Проверяем существование файла
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Файл {filename} не найден")

    # Загружаем данные
    data = load_json_file(file_path)

    if not data:
        return []

    # Фильтрация по временному диапазону
    filtered_data = []

    try:
        start_dt = parse_datetime(start) if start else None
        end_dt = parse_datetime(end) if end else None

        for item in data:
            try:
                # Используем точечную нотацию для доступа к полям
                item_dt = parse_datetime(item.d)

                # Проверяем попадание в диапазон
                if start_dt and item_dt < start_dt:
                    continue
                if end_dt and item_dt > end_dt:
                    continue

                filtered_data.append(item)
            except ValueError:
                # Пропускаем записи с некорректной датой
                continue
    except Exception as e:
        logger.error(f"❌ Ошибка при составлении отрезка: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке данных: {e}")

    return filtered_data
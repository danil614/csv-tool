"""
Вспомогательные функции, не связанные напрямую с фильтрами или агрегаторами.
"""

import csv
from pathlib import Path
from typing import Dict, List


def read_csv(path: Path) -> List[Dict[str, str]]:
    """
    Читаем CSV в список словарей (строка - значение).
    Отдельный модуль, чтобы было проще заменить на pandas при желании.
    """
    with path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        return list(reader)

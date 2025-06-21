"""
Модуль, содержащий логику фильтрации строк CSV-файла.
"""

from typing import Any, Dict

from .exceptions import ParseConditionError


class FilterCondition:
    """
    Класс инкапсулирует условие фильтрации вида "price>100", "brand=xiaomi".
    Поддерживаемые операторы: = < >
    """

    SUPPORTED_OPS = {"=", ">", "<"}

    def __init__(self, column: str, op: str, raw_value: str) -> None:
        if op not in self.SUPPORTED_OPS:
            raise ParseConditionError(f"Unsupported operator '{op}'")
        self.column = column.strip()
        self.op = op
        self.raw_value = raw_value.strip()

    @classmethod
    def parse(cls, raw: str) -> "FilterCondition":
        """Разбираем строку --where и возвращаем объект FilterCondition."""
        for op in cls.SUPPORTED_OPS:
            if op in raw:
                column, value = raw.split(op, maxsplit=1)
                if not column.strip():
                    raise ParseConditionError("Column name is required in --where")
                return cls(column, op, value)
        raise ParseConditionError("Unable to parse --where condition")

    @staticmethod
    def _maybe_cast(value: str) -> Any:
        """
        Пытаемся привести строку к float.
        Если не получилось — остаётся строкой.
        """
        try:
            return float(value)
        except ValueError:
            return value

    def match(self, row: Dict[str, str]) -> bool:
        if self.column not in row:
            raise ParseConditionError(f"Column '{self.column}' absent in CSV")

        left_raw = row[self.column]
        left = self._maybe_cast(left_raw)
        right = self._maybe_cast(self.raw_value)

        # Сравнения
        if self.op == "=":
            return left == right
        if self.op == ">":
            if not all(isinstance(x, (int, float)) for x in (left, right)):
                raise ParseConditionError("Operator '>' works on numeric values only")
            return left > right
        if self.op == "<":
            if not all(isinstance(x, (int, float)) for x in (left, right)):
                raise ParseConditionError("Operator '<' works on numeric values only")
            return left < right

        # Недостижимый участок
        raise ParseConditionError(f"Unsupported operator '{self.op}'")

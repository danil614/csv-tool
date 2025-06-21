"""
Модуль, отвечающий за агрегирующие функции.
Расширяемость: чтобы добавить, например, медиану — достаточно создать MedianAggregator и зарегистрировать его.
"""

from typing import Dict, List, Type

from .exceptions import AggregationError, ParseConditionError


# ------------------------------------------------------------------ #
#                         Базовый класс                              #
# ------------------------------------------------------------------ #
class BaseAggregator:
    name: str = "base"  # уникальный идентификатор в регистре

    def __init__(self, column: str) -> None:
        self.column = column

    def __call__(self, values: List[float]) -> float:
        raise NotImplementedError


# ------------------------------------------------------------------ #
#                        Конкретные реализации                       #
# ------------------------------------------------------------------ #
class MinAggregator(BaseAggregator):
    name = "min"

    def __call__(self, values: List[float]) -> float:
        return min(values)


class MaxAggregator(BaseAggregator):
    name = "max"

    def __call__(self, values: List[float]) -> float:
        return max(values)


class AvgAggregator(BaseAggregator):
    name = "avg"

    def __call__(self, values: List[float]) -> float:
        return sum(values) / len(values)


# ------------------------------------------------------------------ #
#                          Реестр функций                            #
# ------------------------------------------------------------------ #
_AGGREGATORS: Dict[str, Type[BaseAggregator]] = {
    cls.name: cls for cls in (MinAggregator, MaxAggregator, AvgAggregator)
}


def build_aggregator(raw: str) -> BaseAggregator:
    """
    Строка вида  rating=min -> объект MinAggregator(column="rating")
    """
    if "=" not in raw:
        raise ParseConditionError("--aggregate must be 'column=func'")
    column, func_name = (part.strip() for part in raw.split("=", maxsplit=1))
    func_name = func_name.lower()

    if func_name not in _AGGREGATORS:
        names = ", ".join(_AGGREGATORS)
        raise ParseConditionError(
            f"Unknown aggregator '{func_name}'. Supported: {names}"
        )
    return _AGGREGATORS[func_name](column)


# ------------------------------------------------------------------ #
#                 Вспомогательная проверка числовых данных           #
# ------------------------------------------------------------------ #
def cast_to_float(values: List[str], column: str) -> List[float]:
    """
    Приводим каждую строку к float. Если не получается - бросаем ошибку.
    """
    result: List[float] = []
    for raw in values:
        try:
            result.append(float(raw))
        except ValueError as exc:
            raise AggregationError(
                f"Non-numeric value '{raw}' in column '{column}'"
            ) from exc
    return result

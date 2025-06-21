"""
Модуль с исключениями, чтобы ими могли пользоваться другие части проекта.
"""


class CSVToolError(Exception):
    """Base error for CSV-tool."""


class ParseConditionError(CSVToolError):
    """Raised when --where/--aggregate string cannot be parsed."""


class AggregationError(CSVToolError):
    """Raised on aggregation failures (e.g. non-numeric values)."""

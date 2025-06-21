"""
Модуль, отвечающий за взаимодействие с командной строкой.
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List

from tabulate import tabulate

from .aggregation import build_aggregator, cast_to_float
from .exceptions import CSVToolError
from .filter import FilterCondition
from .utils import read_csv


def _print_table(rows: List[Dict[str, Any]]) -> None:
    """Красивый вывод результатов в консоль."""
    if not rows:
        print("No data")
        return

    headers = list(rows[0].keys())
    print(tabulate([row.values() for row in rows], headers=headers, tablefmt="pretty"))


def _apply_filter(rows: List[Dict[str, str]], flt: FilterCondition | None) -> List[Dict[str, str]]:
    """Возвращаем все строки или только те, что удовлетворяют условию."""
    if flt is None:
        return rows
    return [row for row in rows if flt.match(row)]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple CSV analyser.")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    parser.add_argument(
        "--where",
        help='Filter condition, e.g. --where "price>100" or "brand=xiaomi"',
    )
    parser.add_argument(
        "--aggregate",
        help='Aggregate, e.g. --aggregate "rating=min"',
    )
    return parser


def run(argv: List[str] | None = None) -> None:  # точка входа для main.py и тестов
    parser = _build_parser()
    ns = parser.parse_args(argv)

    path = Path(ns.file)
    if not path.exists():
        parser.error(f"File '{path}' not found")

    try:
        rows = read_csv(path)

        # Фильтрация
        flt = FilterCondition.parse(ns.where) if ns.where else None
        selected = _apply_filter(rows, flt)

        # Агрегация
        if ns.aggregate:
            aggregator = build_aggregator(ns.aggregate)
            values_raw = [row[aggregator.column] for row in selected]
            values_num = cast_to_float(values_raw, aggregator.column)
            result_value = aggregator(values_num)
            _print_table([{aggregator.column: result_value}])
        else:
            _print_table(selected)

    except CSVToolError as exc:
        parser.error(str(exc))

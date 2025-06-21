"""
Набор тестов для проверки фильтрации, агрегации и ошибок.
"""

from pathlib import Path
from typing import List

import pytest

from src import run


@pytest.fixture(scope="session")
def sample_csv(tmp_path_factory) -> Path:
    tmp = tmp_path_factory.mktemp("data") / "products.csv"
    tmp.write_text(
        "name,brand,price,rating\n"
        "iphone 15 pro,apple,999,4.9\n"
        "galaxy s23 ultra,samsung,1199,4.8\n"
        "redmi note 12,xiaomi,199,4.6\n"
        "poco x5 pro,xiaomi,299,4.4\n",
        encoding="utf-8",
    )
    return tmp


def _cli(extra: List[str], sample_csv: Path, capsys):
    """Запускаем cli.run и возвращаем stdout."""
    run(["--file", str(sample_csv), *extra])
    return capsys.readouterr().out.strip()


# -------------------------- фильтрация ------------------------------ #
def test_filter_eq(sample_csv, capsys):
    out = _cli(["--where", "brand=xiaomi"], sample_csv, capsys)
    assert "redmi note 12" in out
    assert "poco x5 pro" in out
    assert "iphone 15 pro" not in out


def test_filter_gt(sample_csv, capsys):
    out = _cli(["--where", "price>1000"], sample_csv, capsys)
    assert "galaxy s23 ultra" in out
    assert "iphone 15 pro" not in out


# -------------------------- агрегация ------------------------------- #
@pytest.mark.parametrize(
    "func,expected",
    [("min", "4.4"), ("max", "4.9"), ("avg", "4.675")],
)
def test_aggregation(sample_csv, func, expected, capsys):
    out = _cli(["--aggregate", f"rating={func}"], sample_csv, capsys)
    assert expected in out


def test_aggregation_with_filter(sample_csv, capsys):
    out = _cli(["--where", "brand=xiaomi", "--aggregate", "rating=min"], sample_csv, capsys)
    assert "4.4" in out
    assert "4.9" not in out


# --------------------------- ошибки -------------------------------- #
def test_unknown_aggregator(sample_csv):
    with pytest.raises(SystemExit):
        run(["--file", str(sample_csv), "--aggregate", "price=median"])


def test_unknown_operator(sample_csv):
    with pytest.raises(SystemExit):
        run(["--file", str(sample_csv), "--where", "price>=100"])

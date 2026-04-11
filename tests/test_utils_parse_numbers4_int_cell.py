"""tools.utils の数値セルパース（CSV 取り込みで使用）。"""
from tools.utils import parse_numbers4_int_cell


def test_parse_empty_returns_none() -> None:
    assert parse_numbers4_int_cell(None) is None
    assert parse_numbers4_int_cell("") is None
    assert parse_numbers4_int_cell("   ") is None


def test_parse_comma_yen_strips() -> None:
    assert parse_numbers4_int_cell('1,234') == 1234
    assert parse_numbers4_int_cell('"5,678"円') == 5678


def test_parse_invalid_returns_none() -> None:
    assert parse_numbers4_int_cell("abc") is None

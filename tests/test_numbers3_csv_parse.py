"""numbers3 CSV 行パース・マージ（Supabase / Postgres 投入ロジック）。"""
from tools.load_numbers3_csv_to_postgres import (
    merge_rows_by_draw_number,
    parse_csv_row,
    row_to_rest_payload,
)


def test_parse_csv_row_minimal() -> None:
    row = ["第1234回", "2026/04/10", "123"]
    out = parse_csv_row(row)
    assert out is not None
    draw_number, draw_date, numbers, *tiers = out
    assert draw_number == 1234
    assert draw_date == "2026/04/10"
    assert numbers == "123"
    assert all(t is None for t in tiers)


def test_parse_csv_row_invalid_numbers() -> None:
    assert parse_csv_row(["第1回", "2026/04/10", "12"]) is None
    assert parse_csv_row(["第1回", "2026/04/10", "1234"]) is None


def test_parse_csv_row_kai_variants() -> None:
    assert parse_csv_row(["1234", "2026/04/10", "456"]) is not None
    assert parse_csv_row(["回のみ", "2026/04/10", "456"]) is None


def test_merge_rows_later_list_wins() -> None:
    a = (1, "2020/01/01", "111", None, None, None, None, None, None, None, None)
    b = (1, "2020/01/02", "222", None, None, None, None, None, None, None, None)
    merged = merge_rows_by_draw_number([a], [b])
    assert merged == [b]


def test_row_to_rest_payload_keys() -> None:
    row = (99, "2026/01/02", "987", 1, 2, 3, 4, 5, 6, 7, 8)
    payload = row_to_rest_payload(row)
    assert set(payload.keys()) == {
        "draw_number",
        "draw_date",
        "numbers",
        "tier1_winners",
        "tier1_payout_yen",
        "tier2_winners",
        "tier2_payout_yen",
        "tier3_winners",
        "tier3_payout_yen",
        "tier4_winners",
        "tier4_payout_yen",
    }
    assert payload["draw_number"] == 99
    assert payload["numbers"] == "987"

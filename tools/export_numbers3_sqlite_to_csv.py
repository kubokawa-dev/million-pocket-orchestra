"""
lottery.db の numbers3_draws を numbers3/draws_export.csv に書き出す（Git 用）。

*.db は .gitignore のため、リポジトリ経由で CI に履歴を載せたいときに使う。
書式は load_numbers3_csv_to_postgres.py が読める「第N回,日付,3桁」のみ（等級列は将来拡張可）。
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.utils import DB_PATH


def main() -> None:
    p = argparse.ArgumentParser(description="numbers3_draws を CSV にエクスポート")
    p.add_argument(
        "-o",
        "--output",
        default=os.path.join(ROOT, "numbers3", "draws_export.csv"),
        help="出力パス",
    )
    p.add_argument("--db", default=DB_PATH, help="SQLite パス")
    args = p.parse_args()

    import sqlite3

    if not os.path.isfile(args.db):
        print(f"❌ DB が見つかりません: {args.db}")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    conn = sqlite3.connect(args.db)
    try:
        cur = conn.execute(
            "SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number ASC"
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for draw_number, draw_date, numbers in rows:
            w.writerow([f"第{draw_number}回", draw_date, numbers])

    print(f"✅ {len(rows)} 行を書き出しました: {args.output}")


if __name__ == "__main__":
    main()

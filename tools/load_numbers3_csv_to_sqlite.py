"""
numbers3/*.csv を lottery.db の numbers3_draws に読み込む（GitHub Actions 用）。

ナンバーズ4の tools/load_csv_to_db.py と同じく、予測パイプラインが参照する SQLite を
リポジトリの月次 CSV から毎回再構築する。
"""
from __future__ import annotations

import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.load_numbers3_csv_to_postgres import load_all_csv_files
from tools.utils import DB_PATH, ensure_numbers3_draws_columns, get_db_connection

INSERT_SQL = """
INSERT OR REPLACE INTO numbers3_draws (
    draw_number, draw_date, numbers,
    tier1_winners, tier1_payout_yen,
    tier2_winners, tier2_payout_yen,
    tier3_winners, tier3_payout_yen,
    tier4_winners, tier4_payout_yen
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def ensure_table(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS numbers3_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL,
            tier1_winners INTEGER,
            tier1_payout_yen INTEGER,
            tier2_winners INTEGER,
            tier2_payout_yen INTEGER,
            tier3_winners INTEGER,
            tier3_payout_yen INTEGER,
            tier4_winners INTEGER,
            tier4_payout_yen INTEGER
        )
        """
    )
    conn.commit()
    ensure_numbers3_draws_columns(conn)


def load_numbers3_csv_to_sqlite() -> int:
    print("=" * 60)
    print("📂 numbers3/*.csv → SQLite numbers3_draws")
    print("=" * 60)

    rows = load_all_csv_files()
    print(f"📊 CSVから {len(rows)} 件を読み込みました")

    if not rows:
        print("⚠️  CSV に有効行がありません")
        return 0

    conn = get_db_connection()
    try:
        ensure_table(conn)
        cur = conn.cursor()
        for row in rows:
            cur.execute(INSERT_SQL, row)
        conn.commit()

        cur.execute("SELECT COUNT(*), MIN(draw_number), MAX(draw_number) FROM numbers3_draws")
        total, lo, hi = cur.fetchone()
        print(f"✅ SQLite に反映: {len(rows)} 行（テーブル計 {total} 件、第{lo}〜第{hi}回）")
        return len(rows)
    finally:
        conn.close()


if __name__ == "__main__":
    load_numbers3_csv_to_sqlite()

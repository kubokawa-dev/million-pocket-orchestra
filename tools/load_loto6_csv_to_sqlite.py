"""
loto6/*.csv → lottery.db の loto6_draws（4列。GitHub Actions で予測・分析と整合させる）。

フルCSVの等級列は SQLite スキーマに無いため、当せん本数字・ボーナスのみ投入する。
"""
from __future__ import annotations

import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.load_loto6_csv_to_postgres import load_all_csv_files
from tools.utils import get_db_connection

INSERT_SQL = """
INSERT OR REPLACE INTO loto6_draws (
    draw_number, draw_date, numbers, bonus_number
) VALUES (?, ?, ?, ?)
"""


def ensure_table(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loto6_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL,
            bonus_number INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def load_loto6_csv_to_sqlite() -> int:
    print("=" * 60)
    print("📂 loto6/*.csv → SQLite loto6_draws")
    print("=" * 60)

    rows = load_all_csv_files()
    slim = [(r[0], r[1], r[2], r[3]) for r in rows]
    print(f"📊 CSVから {len(slim)} 件を読み込みました")

    if not slim:
        print("⚠️  CSV に有効行がありません")
        return 0

    conn = get_db_connection()
    try:
        ensure_table(conn)
        cur = conn.cursor()
        for row in slim:
            cur.execute(INSERT_SQL, row)
        conn.commit()

        cur.execute("SELECT COUNT(*), MIN(draw_number), MAX(draw_number) FROM loto6_draws")
        total, lo, hi = cur.fetchone()
        print(f"✅ SQLite に反映: {len(slim)} 行（計 {total} 件、第{lo}〜第{hi}回）")
        return len(slim)
    finally:
        conn.close()


if __name__ == "__main__":
    load_loto6_csv_to_sqlite()

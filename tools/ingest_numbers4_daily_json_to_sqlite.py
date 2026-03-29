"""
predictions/daily 配下の JSON を numbers4_daily_prediction_documents に取り込む（SQLite）。

  python tools/ingest_numbers4_daily_json_to_sqlite.py
  python tools/ingest_numbers4_daily_json_to_sqlite.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.daily_predictions_json_common import DAILY, collect_daily_prediction_records
from tools.utils import get_db_connection

UPSERT_SQL = """
INSERT INTO numbers4_daily_prediction_documents (
    target_draw_number, doc_kind, method_slug, relative_path,
    payload, payload_sha256, file_mtime, ingested_at
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
ON CONFLICT(target_draw_number, doc_kind, method_slug) DO UPDATE SET
    relative_path = excluded.relative_path,
    payload = excluded.payload,
    payload_sha256 = excluded.payload_sha256,
    file_mtime = excluded.file_mtime,
    ingested_at = excluded.ingested_at
"""


def ensure_table(conn) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS numbers4_daily_prediction_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_draw_number INTEGER NOT NULL,
            doc_kind TEXT NOT NULL CHECK (doc_kind IN ('ensemble', 'method', 'budget_plan')),
            method_slug TEXT NOT NULL DEFAULT '',
            relative_path TEXT NOT NULL,
            payload TEXT NOT NULL,
            payload_sha256 TEXT,
            file_mtime TEXT,
            ingested_at TEXT DEFAULT (datetime('now')),
            CHECK (
                (doc_kind = 'method' AND method_slug != '')
                OR (doc_kind IN ('ensemble', 'budget_plan') AND method_slug = '')
            ),
            UNIQUE (target_draw_number, doc_kind, method_slug)
        )
        """
    )
    conn.commit()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not DAILY.is_dir():
        print(f"⚠️  {DAILY} がありません")
        return

    records, skipped = collect_daily_prediction_records()
    print(f"📂 対象 {len(records)} 件（パターン外スキップ {skipped}）")

    if args.dry_run:
        return

    conn = get_db_connection()
    ensure_table(conn)
    cur = conn.cursor()
    for r in records:
        payload_text = json.dumps(r.payload, ensure_ascii=False, separators=(",", ":"))
        cur.execute(
            UPSERT_SQL,
            (
                r.target_draw_number,
                r.doc_kind,
                r.method_slug,
                r.relative_path,
                payload_text,
                r.payload_sha256,
                r.file_mtime,
            ),
        )
    conn.commit()
    conn.close()
    print(f"✅ lottery.db に反映しました（{len(records)} 件）")


if __name__ == "__main__":
    main()

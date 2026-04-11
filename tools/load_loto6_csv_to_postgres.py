"""
loto6/*.csv を PostgreSQL（ローカル / Supabase）の loto6_draws に UPSERT。

想定CSV（20列・ヘッダなし）:
  第n回,日付,本数字×6,(ボーナス),1等口,1等金,…,5等口,5等金,キャリーオーバー

前提:
  apps/web/supabase/migrations/20260412120000_loto6_draws.sql 相当のテーブル

PostgREST 一括時は全行で JSON キー一致（PGRST102 回避のため NULL も明示）。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import quote_plus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("❌ psycopg2-binary が必要です: pip install psycopg2-binary")
    sys.exit(1)

from dotenv import load_dotenv

from tools.load_numbers3_csv_to_postgres import (
    _is_localhost_dsn,
    _service_role_for_rest,
    _supabase_rest_base,
    inject_service_role_from_supabase_cli,
    resolve_postgres_url,
    resolve_supabase_project_ref,
    try_inject_service_role_from_cli,
)
from tools.utils import DB_PATH, parse_numbers4_int_cell

load_dotenv(os.path.join(ROOT, ".env"))
load_dotenv(os.path.join(ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(ROOT, "apps", "web", ".env.local"), override=True)

CSV_DIR = os.path.join(ROOT, "loto6")

REST_COLUMNS = [
    "draw_number",
    "draw_date",
    "numbers",
    "bonus_number",
    "tier1_winners",
    "tier1_payout_yen",
    "tier2_winners",
    "tier2_payout_yen",
    "tier3_winners",
    "tier3_payout_yen",
    "tier4_winners",
    "tier4_payout_yen",
    "tier5_winners",
    "tier5_payout_yen",
    "carryover_yen",
]

UPSERT_SQL = """
INSERT INTO loto6_draws (
    draw_number, draw_date, numbers, bonus_number,
    tier1_winners, tier1_payout_yen,
    tier2_winners, tier2_payout_yen,
    tier3_winners, tier3_payout_yen,
    tier4_winners, tier4_payout_yen,
    tier5_winners, tier5_payout_yen,
    carryover_yen
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (draw_number) DO UPDATE SET
    draw_date = EXCLUDED.draw_date,
    numbers = EXCLUDED.numbers,
    bonus_number = EXCLUDED.bonus_number,
    tier1_winners = EXCLUDED.tier1_winners,
    tier1_payout_yen = EXCLUDED.tier1_payout_yen,
    tier2_winners = EXCLUDED.tier2_winners,
    tier2_payout_yen = EXCLUDED.tier2_payout_yen,
    tier3_winners = EXCLUDED.tier3_winners,
    tier3_payout_yen = EXCLUDED.tier3_payout_yen,
    tier4_winners = EXCLUDED.tier4_winners,
    tier4_payout_yen = EXCLUDED.tier4_payout_yen,
    tier5_winners = EXCLUDED.tier5_winners,
    tier5_payout_yen = EXCLUDED.tier5_payout_yen,
    carryover_yen = EXCLUDED.carryover_yen
"""


def _strip_q(s: str) -> str:
    return s.strip().strip('"')


def parse_winner_cell(raw: str | None) -> int | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().strip('"')
    if "該当" in s:
        return None
    s = s.replace("口", "").replace(",", "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def parse_csv_row(row: list[str]) -> tuple | None:
    if len(row) < 20:
        return None
    kai_m = re.search(r"(\d+)", row[0] or "")
    if not kai_m:
        return None
    draw_number = int(kai_m.group(1))
    draw_date = row[1].strip()
    try:
        nums = [int(row[i]) for i in range(2, 8)]
    except ValueError:
        return None
    for n in nums:
        if not (1 <= n <= 43):
            return None
    numbers = ",".join(str(x) for x in nums)
    bonus_m = re.search(r"\((\d+)\)", (row[8] or "").strip())
    if not bonus_m:
        return None
    bonus_number = int(bonus_m.group(1))
    if not (1 <= bonus_number <= 43):
        return None

    t1w = parse_winner_cell(row[9])
    t1y = parse_numbers4_int_cell(row[10])
    t2w = parse_winner_cell(row[11])
    t2y = parse_numbers4_int_cell(row[12])
    t3w = parse_winner_cell(row[13])
    t3y = parse_numbers4_int_cell(row[14])
    t4w = parse_winner_cell(row[15])
    t4y = parse_numbers4_int_cell(row[16])
    t5w = parse_winner_cell(row[17])
    t5y = parse_numbers4_int_cell(row[18])
    carry = parse_numbers4_int_cell(row[19])

    return (
        draw_number,
        draw_date,
        numbers,
        bonus_number,
        t1w,
        t1y,
        t2w,
        t2y,
        t3w,
        t3y,
        t4w,
        t4y,
        t5w,
        t5y,
        carry,
    )


def load_all_csv_files() -> list[tuple]:
    rows: list[tuple] = []
    for csv_path in sorted(glob.glob(os.path.join(CSV_DIR, "*.csv"))):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if not row:
                        continue
                    parsed = parse_csv_row(row)
                    if parsed:
                        rows.append(parsed)
        except Exception as e:
            print(f"[warn] Error reading {csv_path}: {e}")
    by_draw: dict[int, tuple] = {}
    for r in rows:
        by_draw[r[0]] = r
    return sorted(by_draw.values(), key=lambda x: x[0])


def load_rows_from_sqlite(db_path: str) -> list[tuple]:
    import sqlite3

    if not os.path.isfile(db_path):
        print(f"❌ SQLite が見つかりません: {db_path}")
        return []
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='loto6_draws'"
        )
        if cur.fetchone() is None:
            print("⚠️ loto6_draws テーブルがありません")
            return []
        cur = conn.execute(
            "SELECT draw_number, draw_date, numbers, bonus_number FROM loto6_draws ORDER BY draw_number ASC"
        )
        raw = cur.fetchall()
    finally:
        conn.close()

    out: list[tuple] = []
    for draw_number, draw_date, numbers, bonus in raw:
        num = str(numbers or "").strip()
        if not num:
            continue
        out.append(
            (
                int(draw_number),
                str(draw_date or "").strip(),
                num,
                int(bonus) if bonus is not None else 0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )
        )
    return out


def merge_rows_by_draw_number(*row_lists: list[tuple]) -> list[tuple]:
    by_draw: dict[int, tuple] = {}
    for rows in row_lists:
        for r in rows:
            by_draw[r[0]] = r
    return sorted(by_draw.values(), key=lambda x: x[0])


def load_rows_for_source(source: str, sqlite_path: str | None) -> tuple[list[tuple], str]:
    path = sqlite_path or DB_PATH
    if source == "csv":
        return load_all_csv_files(), "loto6/*.csv"
    if source == "sqlite":
        return load_rows_from_sqlite(path), path
    s_rows = load_rows_from_sqlite(path)
    c_rows = load_all_csv_files()
    return merge_rows_by_draw_number(s_rows, c_rows), f"{path} + loto6/*.csv（同一回は CSV 優先）"


def row_to_rest_payload(row: tuple) -> dict:
    d = dict(zip(REST_COLUMNS, row))
    return {k: d[k] for k in REST_COLUMNS}


def upsert_via_supabase_rest(rows: list[tuple], *, chunk_size: int = 500) -> None:
    base = _supabase_rest_base()
    key = _service_role_for_rest()
    if not base or not key:
        raise ValueError("PostgREST 用の URL / service_role が不足しています")

    endpoint = f"{base}/rest/v1/loto6_draws?on_conflict=draw_number"
    payload_rows = [row_to_rest_payload(r) for r in rows]
    total = 0
    for i in range(0, len(payload_rows), chunk_size):
        chunk = payload_rows[i : i + chunk_size]
        body = json.dumps(chunk, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(endpoint, data=body, method="POST")
        req.add_header("apikey", key)
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "resolution=merge-duplicates,return=minimal")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:2000]
            raise RuntimeError(f"PostgREST HTTP {e.code}: {err_body}") from e
        total += len(chunk)
        print(f"   … {total} / {len(rows)} 件送信")
    print(f"✅ Supabase PostgREST に {len(rows)} 件を UPSERT しました")


def _should_try_cli_service_role(args: argparse.Namespace) -> bool:
    if args.no_rest or args.use_cli_login or _service_role_for_rest():
        return False
    if not _supabase_rest_base():
        return False
    import shutil

    if not shutil.which("supabase"):
        return False
    db_url = resolve_postgres_url()
    rest_flag = os.getenv("SUPABASE_USE_REST", "").lower() in ("1", "true", "yes")
    return bool(rest_flag or not db_url or _is_localhost_dsn(db_url))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="loto6 CSV / SQLite → PostgreSQL UPSERT")
    p.add_argument(
        "--source",
        choices=("csv", "sqlite", "both"),
        default="csv",
        help="csv=loto6/*.csv のみ, sqlite=lottery.db, both=マージ（同一回は CSV 優先）",
    )
    p.add_argument("--sqlite-path", default=None)
    p.add_argument("--no-rest", action="store_true")
    p.add_argument("--use-cli-login", action="store_true")
    p.add_argument("--skip-if-unconfigured", action="store_true")
    p.add_argument("--project-ref", default=None)
    p.add_argument(
        "--draw-number",
        type=int,
        default=None,
        action="append",
        dest="draw_numbers",
        metavar="N",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.use_cli_login:
        ref = resolve_supabase_project_ref(args.project_ref)
        inject_service_role_from_supabase_cli(ref)
        print("🔑 Supabase CLI で service_role を取得しました（メモリ内のみ）")
    elif _should_try_cli_service_role(args):
        if try_inject_service_role_from_cli(args.project_ref):
            print("🔑 supabase login 済み CLI から service_role を取得しました（メモリ内のみ）")

    if args.skip_if_unconfigured and not args.use_cli_login:
        db_url = resolve_postgres_url()
        has_rest = bool(_service_role_for_rest() and _supabase_rest_base())
        can_direct_remote = bool(db_url and not _is_localhost_dsn(db_url))
        if not has_rest and not can_direct_remote:
            print(
                "⚠️ Supabase REST 用の認証も、リモート Postgres URI も無いため "
                "loto6_draws UPSERT をスキップします（--skip-if-unconfigured）。"
            )
            return

    rows, label = load_rows_for_source(args.source, args.sqlite_path)
    print(f"📊 ロト6 抽選データ（{label}）から {len(rows)} 行を読み込み")
    if not rows:
        print("⚠️ 投入する行がありません")
        return

    if args.draw_numbers:
        want = set(args.draw_numbers)
        before = len(rows)
        rows = [r for r in rows if r[0] in want]
        print(f"🎯 --draw-number フィルタ: {before} 行 → {len(rows)} 行")
        if not rows:
            return

    db_url = resolve_postgres_url()
    use_rest = (
        not args.no_rest
        and _service_role_for_rest()
        and _supabase_rest_base()
        and (
            os.getenv("SUPABASE_USE_REST", "").lower() in ("1", "true", "yes")
            or not db_url
            or _is_localhost_dsn(db_url)
        )
    )

    if use_rest:
        print("🔌 PostgREST 経由で UPSERT します（loto6_draws）")
        try:
            upsert_via_supabase_rest(rows)
        except (ValueError, RuntimeError) as e:
            print(f"❌ {e}")
            sys.exit(1)
        return

    if not db_url:
        print("❌ Postgres 接続情報がありません")
        sys.exit(1)
    if "?schema" in db_url:
        db_url = db_url.split("?schema")[0]
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e:
        print(f"❌ Postgres 接続失敗: {e}")
        sys.exit(1)
    try:
        with conn.cursor() as cur:
            execute_batch(cur, UPSERT_SQL, rows, page_size=500)
        conn.commit()
        print(f"✅ PostgreSQL に {len(rows)} 件を UPSERT しました")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

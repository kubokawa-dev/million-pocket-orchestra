"""
numbers3/*.csv またはローカル lottery.db の numbers3_draws を PostgreSQL（ローカル / Supabase）に投入する。

想定CSV（3列の最小形式）:
  第1234回,2026/04/10,123

numbers4 月次CSVと同じく、当選番号の次から8列（口数・払戻×4等級）があれば取り込みます:
  第1234回,2026/04/10,123,t1w,t1y,t2w,t2y,t3w,t3y,t4w,t4y

スキーマ:
  apps/web/supabase/migrations または tools/ddl_numbers3_draws_postgres.sql（numbers4_draws と同列）

Postgres 直結 UPSERT では、CSVに等級列が無い場合は既存の tier 値を COALESCE で保持します。
PostgREST 経由では、等級が NULL の列は JSON に含めず既存行の値を残しやすくします。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import shutil
import subprocess
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

from tools.utils import DB_PATH, parse_numbers4_int_cell

load_dotenv(os.path.join(ROOT, ".env"))
load_dotenv(os.path.join(ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(ROOT, "apps", "web", ".env.local"), override=True)

CSV_DIR = os.path.join(ROOT, "numbers3")

REST_COLUMNS = [
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
]

UPSERT_SQL = """
INSERT INTO numbers3_draws (
    draw_number, draw_date, numbers,
    tier1_winners, tier1_payout_yen,
    tier2_winners, tier2_payout_yen,
    tier3_winners, tier3_payout_yen,
    tier4_winners, tier4_payout_yen
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (draw_number) DO UPDATE SET
    draw_date = EXCLUDED.draw_date,
    numbers = EXCLUDED.numbers,
    tier1_winners = COALESCE(EXCLUDED.tier1_winners, numbers3_draws.tier1_winners),
    tier1_payout_yen = COALESCE(EXCLUDED.tier1_payout_yen, numbers3_draws.tier1_payout_yen),
    tier2_winners = COALESCE(EXCLUDED.tier2_winners, numbers3_draws.tier2_winners),
    tier2_payout_yen = COALESCE(EXCLUDED.tier2_payout_yen, numbers3_draws.tier2_payout_yen),
    tier3_winners = COALESCE(EXCLUDED.tier3_winners, numbers3_draws.tier3_winners),
    tier3_payout_yen = COALESCE(EXCLUDED.tier3_payout_yen, numbers3_draws.tier3_payout_yen),
    tier4_winners = COALESCE(EXCLUDED.tier4_winners, numbers3_draws.tier4_winners),
    tier4_payout_yen = COALESCE(EXCLUDED.tier4_payout_yen, numbers3_draws.tier4_payout_yen)
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="numbers3 CSV / SQLite → PostgreSQL UPSERT")
    p.add_argument(
        "--source",
        choices=("csv", "sqlite", "both"),
        default="csv",
        help="csv=numbers3/*.csv のみ, sqlite=lottery.db の numbers3_draws, both=両方（同一回は CSV 優先）",
    )
    p.add_argument(
        "--sqlite-path",
        default=None,
        help="--source sqlite/both 時の DB パス（省略時はルートの lottery.db）",
    )
    p.add_argument("--no-rest", action="store_true")
    p.add_argument("--use-cli-login", action="store_true")
    p.add_argument(
        "--skip-if-unconfigured",
        action="store_true",
        help="Postgres URI も Supabase REST 用の認証も無いときは何もせず終了（CI 向け）",
    )
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


def _strip_q(s: str) -> str:
    return s.strip().strip('"')


def resolve_supabase_project_ref(explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    env_ref = os.environ.get("SUPABASE_PROJECT_REF", "").strip()
    if env_ref:
        return env_ref
    linked = os.path.join(ROOT, "apps", "web", "supabase", ".temp", "project-ref")
    if os.path.isfile(linked):
        with open(linked, encoding="utf-8") as f:
            s = f.read().strip()
            if s:
                return s
    pub = _strip_q(os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "")).rstrip("/")
    m = re.match(r"https?://([^.]+)\.supabase\.co/?$", pub)
    if m:
        return m.group(1)
    print("❌ Supabase の project ref が分かりません（--project-ref を指定してください）")
    sys.exit(1)


def inject_service_role_from_supabase_cli(project_ref: str) -> None:
    if not shutil.which("supabase"):
        print("❌ supabase CLI が PATH にありません")
        sys.exit(1)
    web_dir = os.path.join(ROOT, "apps", "web")
    proc = subprocess.run(
        [
            "supabase",
            "projects",
            "api-keys",
            "--project-ref",
            project_ref,
            "-o",
            "json",
        ],
        cwd=web_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:2000]
        print(f"❌ supabase projects api-keys が失敗しました（exit {proc.returncode}）:\n{err}")
        sys.exit(1)
    keys = json.loads(proc.stdout)
    service_key = ""
    for item in keys:
        if item.get("name") == "service_role":
            service_key = item.get("api_key") or ""
            break
    if not service_key:
        print("❌ api-keys に service_role がありません")
        sys.exit(1)
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = service_key
    os.environ["NEXT_PUBLIC_SUPABASE_URL"] = f"https://{project_ref}.supabase.co"


def try_inject_service_role_from_cli(project_ref: str | None) -> bool:
    """
    SUPABASE_SERVICE_ROLE_KEY が未設定でも、supabase login 済みなら CLI で取得して環境に載せる。
    （ resolve / inject は失敗時に sys.exit するため SystemExit を握りつぶす ）
    """
    if _service_role_for_rest():
        return True
    if not shutil.which("supabase"):
        return False
    try:
        ref = resolve_supabase_project_ref(project_ref)
        inject_service_role_from_supabase_cli(ref)
    except SystemExit:
        return False
    except Exception as e:
        print(f"[warn] CLI での service_role 取得をスキップ: {e}")
        return False
    return bool(_service_role_for_rest())


def _should_try_cli_service_role(args: argparse.Namespace) -> bool:
    """PostgREST を使いたいがキーだけ無いとき、CLI で補えるか。"""
    if args.no_rest or args.use_cli_login or _service_role_for_rest():
        return False
    if not _supabase_rest_base():
        return False
    if not shutil.which("supabase"):
        return False
    db_url = resolve_postgres_url()
    rest_flag = os.getenv("SUPABASE_USE_REST", "").lower() in ("1", "true", "yes")
    return bool(rest_flag or not db_url or _is_localhost_dsn(db_url))


def resolve_postgres_url() -> str:
    v = _strip_q(os.environ.get("SUPABASE_DATABASE_URL", ""))
    if v:
        return v

    pwd = _strip_q(os.environ.get("SUPABASE_DB_PASSWORD", ""))
    pub = _strip_q(os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "")).rstrip("/")
    if pwd and pub:
        m = re.match(r"https?://([^.]+)\.supabase\.co/?$", pub)
        if m:
            ref = m.group(1)
            return (
                f"postgresql://postgres:{quote_plus(pwd)}@db.{ref}.supabase.co:5432/postgres"
                "?sslmode=require"
            )
    return _strip_q(os.environ.get("DATABASE_URL", ""))


def _service_role_for_rest() -> str:
    k = _strip_q(os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))
    if not k or k in ("dummy-key", "your-service-role-key") or "dummy" in k.lower():
        return ""
    if not k.startswith("eyJ"):
        return ""
    return k


def _supabase_rest_base() -> str:
    pub = _strip_q(os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "")).rstrip("/")
    if not pub or "supabase.co" not in pub:
        return ""
    return pub


def _is_localhost_dsn(url: str) -> bool:
    u = url.lower()
    return "localhost" in u or "127.0.0.1" in u


def parse_csv_row(row: list[str]) -> tuple | None:
    if len(row) < 3:
        return None
    kai_match = re.search(r"(\d+)", row[0] or "")
    if not kai_match:
        return None
    draw_number = int(kai_match.group(1))
    draw_date = row[1].strip()
    numbers = row[2].strip()
    if not re.fullmatch(r"\d{3}", numbers):
        return None

    t1w = parse_numbers4_int_cell(row[3]) if len(row) > 3 else None
    t1y = parse_numbers4_int_cell(row[4]) if len(row) > 4 else None
    t2w = parse_numbers4_int_cell(row[5]) if len(row) > 5 else None
    t2y = parse_numbers4_int_cell(row[6]) if len(row) > 6 else None
    t3w = parse_numbers4_int_cell(row[7]) if len(row) > 7 else None
    t3y = parse_numbers4_int_cell(row[8]) if len(row) > 8 else None
    t4w = parse_numbers4_int_cell(row[9]) if len(row) > 9 else None
    t4y = parse_numbers4_int_cell(row[10]) if len(row) > 10 else None

    return (
        draw_number,
        draw_date,
        numbers,
        t1w,
        t1y,
        t2w,
        t2y,
        t3w,
        t3y,
        t4w,
        t4y,
    )


def _read_csv_path(csv_path: str) -> list[tuple]:
    rows: list[tuple] = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                parsed = parse_csv_row(row)
                if parsed:
                    rows.append(parsed)
    except Exception as e:
        print(f"[warn] Error reading {csv_path}: {e}")
    return rows


def load_all_csv_files() -> list[tuple]:
    """月次 YYYYMM.csv を優先し、draws_export.csv は未掲載の回のみ補完する（同一回は等級付きを残す）。"""
    export_rows: list[tuple] = []
    monthly_rows: list[tuple] = []
    for csv_path in sorted(glob.glob(os.path.join(CSV_DIR, "*.csv"))):
        base = os.path.basename(csv_path)
        if base == "draws_normalized.csv":
            continue
        chunk = _read_csv_path(csv_path)
        if base == "draws_export.csv":
            export_rows.extend(chunk)
        else:
            monthly_rows.extend(chunk)
    return merge_rows_by_draw_number(export_rows, monthly_rows)


def _sqlite_cell_tier(raw: object) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    return parse_numbers4_int_cell(raw)


def load_rows_from_sqlite(db_path: str) -> list[tuple]:
    """lottery.db の numbers3_draws を 11 列タプルに正規化する。"""
    import sqlite3

    if not os.path.isfile(db_path):
        print(f"❌ SQLite が見つかりません: {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='numbers3_draws'"
        )
        if cur.fetchone() is None:
            print("⚠️ numbers3_draws テーブルがありません")
            return []
        cur = conn.execute("PRAGMA table_info(numbers3_draws)")
        col_names = [row[1] for row in cur.fetchall()]
        cur = conn.execute(
            f"SELECT {', '.join(col_names)} FROM numbers3_draws ORDER BY draw_number ASC"
        )
        raw_rows = cur.fetchall()
    finally:
        conn.close()

    out: list[tuple] = []
    for tup in raw_rows:
        d = dict(zip(col_names, tup))
        num = str(d.get("numbers") or "").strip()
        if not re.fullmatch(r"\d{3}", num):
            continue
        out.append(
            (
                int(d["draw_number"]),
                str(d.get("draw_date") or "").strip(),
                num,
                _sqlite_cell_tier(d.get("tier1_winners")),
                _sqlite_cell_tier(d.get("tier1_payout_yen")),
                _sqlite_cell_tier(d.get("tier2_winners")),
                _sqlite_cell_tier(d.get("tier2_payout_yen")),
                _sqlite_cell_tier(d.get("tier3_winners")),
                _sqlite_cell_tier(d.get("tier3_payout_yen")),
                _sqlite_cell_tier(d.get("tier4_winners")),
                _sqlite_cell_tier(d.get("tier4_payout_yen")),
            )
        )
    return out


def merge_rows_by_draw_number(*row_lists: list[tuple]) -> list[tuple]:
    """同一 draw_number は後から渡したリストが優先（CSV で SQLite を上書きする用途）。"""
    by_draw: dict[int, tuple] = {}
    for rows in row_lists:
        for r in rows:
            by_draw[r[0]] = r
    return sorted(by_draw.values(), key=lambda x: x[0])


def load_rows_for_source(source: str, sqlite_path: str | None) -> tuple[list[tuple], str]:
    """行と、ログ用ラベルを返す。"""
    path = sqlite_path or DB_PATH
    if source == "csv":
        rows = load_all_csv_files()
        return rows, "numbers3/*.csv"
    if source == "sqlite":
        rows = load_rows_from_sqlite(path)
        return rows, path
    # both
    s_rows = load_rows_from_sqlite(path)
    c_rows = load_all_csv_files()
    merged = merge_rows_by_draw_number(s_rows, c_rows)
    return merged, f"{path} + numbers3/*.csv（同一回は CSV 優先）"


def row_to_rest_payload(row: tuple) -> dict:
    """PostgREST 一括 UPSERT は配列内で全オブジェクトのキー一致が必須（PGRST102）。"""
    d = dict(zip(REST_COLUMNS, row))
    return {k: d[k] for k in REST_COLUMNS}


def upsert_via_supabase_rest(rows: list[tuple], *, chunk_size: int = 500) -> None:
    base = _supabase_rest_base()
    key = _service_role_for_rest()
    if not base or not key:
        raise ValueError("PostgREST 用の URL / service_role が不足しています")

    endpoint = f"{base}/rest/v1/numbers3_draws?on_conflict=draw_number"
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
                "numbers3_draws UPSERT をスキップします（--skip-if-unconfigured）。"
                "ローカル DATABASE_URL のみの場合は .env.local に "
                "NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY を追加するか、"
                "SUPABASE_DATABASE_URL で本番 DB を指定してください。"
            )
            return

    rows, label = load_rows_for_source(args.source, args.sqlite_path)
    print(f"📊 numbers3 抽選データ（{label}）から {len(rows)} 行を読み込み")
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
        print("🔌 PostgREST 経由で UPSERT します（numbers3_draws）")
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

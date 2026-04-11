"""
numbers3/*.csv を PostgreSQL（ローカル Postgres / Supabase）に投入する。

想定CSV:
  第1234回,2026/04/10,123
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

load_dotenv(os.path.join(ROOT, ".env"))
load_dotenv(os.path.join(ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(ROOT, "apps", "web", ".env.local"), override=True)

CSV_DIR = os.path.join(ROOT, "numbers3")
REST_COLUMNS = ["draw_number", "draw_date", "numbers"]

UPSERT_SQL = """
INSERT INTO numbers3_draws (draw_number, draw_date, numbers)
VALUES (%s, %s, %s)
ON CONFLICT (draw_number) DO UPDATE SET
  draw_date = EXCLUDED.draw_date,
  numbers = EXCLUDED.numbers
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="numbers3 CSV → PostgreSQL UPSERT")
    p.add_argument("--no-rest", action="store_true")
    p.add_argument("--use-cli-login", action="store_true")
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


def parse_csv_row(row: list[str]) -> tuple[int, str, str] | None:
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
    return (draw_number, draw_date, numbers)


def load_all_csv_files() -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    for csv_path in sorted(glob.glob(os.path.join(CSV_DIR, "*.csv"))):
        base = os.path.basename(csv_path)
        if base == "draws_normalized.csv":
            continue
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


def upsert_via_supabase_rest(rows: list[tuple[int, str, str]], *, chunk_size: int = 500) -> None:
    base = _supabase_rest_base()
    key = _service_role_for_rest()
    if not base or not key:
        raise ValueError("PostgREST 用の URL / service_role が不足しています")

    endpoint = f"{base}/rest/v1/numbers3_draws?on_conflict=draw_number"
    payload_rows = [dict(zip(REST_COLUMNS, r)) for r in rows]
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

    rows = load_all_csv_files()
    print(f"📊 numbers3 CSV から {len(rows)} 行を読み込み")
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

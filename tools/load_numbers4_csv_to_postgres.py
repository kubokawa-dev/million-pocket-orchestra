"""
numbers4/*.csv を PostgreSQL（ローカル Postgres / Supabase）に投入する。

前提:
  pip install psycopg2-binary
  環境変数 DATABASE_URL（?schema=public は可。接続時に除去）

スキーマ:
  tools/ddl_numbers4_draws_postgres.sql を先に実行して列を揃えてください。

年で絞る例:
  python tools/load_numbers4_csv_to_postgres.py --min-year 2015 --max-year 2020

接続文字列の優先順位（.env / .env.local / apps/web/.env.local を読込）:
  1. SUPABASE_DATABASE_URL … リモート Postgres の URI を直指定（推奨）
  2. SUPABASE_DB_PASSWORD + NEXT_PUBLIC_SUPABASE_URL … db.<ref>.supabase.co を自動組立
  3. DATABASE_URL … ローカル用

  DATABASE_URL が localhost のままのとき、.env.local に SUPABASE_SERVICE_ROLE_KEY（本番キー）があれば
  PostgREST（HTTPS）経由でリモートに UPSERT する（--no-rest で無効化）。

  --use-cli-login … supabase login 済みの CLI で `projects api-keys` を実行し service_role を取得、
  PostgREST UPSERT する（秘密は .env に書かない。apps/web が link 先であること）。
"""
from __future__ import annotations

import argparse
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

from tools.load_csv_to_db import load_all_csv_files, load_csv_files_for_year_range

load_dotenv(os.path.join(ROOT, ".env"))
load_dotenv(os.path.join(ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(ROOT, "apps", "web", ".env.local"), override=True)

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
INSERT INTO numbers4_draws (
    draw_number, draw_date, numbers,
    tier1_winners, tier1_payout_yen,
    tier2_winners, tier2_payout_yen,
    tier3_winners, tier3_payout_yen,
    tier4_winners, tier4_payout_yen
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (draw_number) DO UPDATE SET
    draw_date = EXCLUDED.draw_date,
    numbers = EXCLUDED.numbers,
    tier1_winners = EXCLUDED.tier1_winners,
    tier1_payout_yen = EXCLUDED.tier1_payout_yen,
    tier2_winners = EXCLUDED.tier2_winners,
    tier2_payout_yen = EXCLUDED.tier2_payout_yen,
    tier3_winners = EXCLUDED.tier3_winners,
    tier3_payout_yen = EXCLUDED.tier3_payout_yen,
    tier4_winners = EXCLUDED.tier4_winners,
    tier4_payout_yen = EXCLUDED.tier4_payout_yen
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="numbers4 CSV → PostgreSQL UPSERT")
    p.add_argument(
        "--min-year",
        type=int,
        default=None,
        help="含む。YYYYMM.csv の年でフィルタ（--max-year と併用）",
    )
    p.add_argument(
        "--max-year",
        type=int,
        default=None,
        help="含む。YYYYMM.csv の年でフィルタ（--min-year と併用）",
    )
    p.add_argument(
        "--no-rest",
        action="store_true",
        help="PostgREST フォールバックを使わず Postgres 直結のみ",
    )
    p.add_argument(
        "--use-cli-login",
        action="store_true",
        help="supabase login 済みの access token で service_role を取得して PostgREST に送る",
    )
    p.add_argument(
        "--project-ref",
        default=None,
        help="--use-cli-login 時のプロジェクト ref（省略時は link 先や NEXT_PUBLIC_SUPABASE_URL から推定）",
    )
    p.add_argument(
        "--draw-number",
        type=int,
        default=None,
        action="append",
        dest="draw_numbers",
        metavar="N",
        help="指定した回号だけ UPSERT（複数回は --draw-number を繰り返す）",
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
    print(
        "❌ Supabase の project ref が分かりません。"
        " --project-ref を付けるか、apps/web で supabase link を実行してください。"
    )
    sys.exit(1)


def inject_service_role_from_supabase_cli(project_ref: str) -> None:
    """supabase CLI（login 済み）で api-keys を取得し、環境変数にだけ載せる。"""
    if not shutil.which("supabase"):
        print("❌ supabase CLI が PATH にありません")
        sys.exit(1)
    web_dir = os.path.join(ROOT, "apps", "web")
    if not os.path.isdir(web_dir):
        print(f"❌ {web_dir} がありません")
        sys.exit(1)
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
    try:
        keys = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ api-keys の JSON が解析できません: {e}")
        sys.exit(1)
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
    """リモート優先で Postgres 接続 URI を決める。"""
    for key in ("SUPABASE_DATABASE_URL",):
        v = _strip_q(os.environ.get(key, ""))
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

    v = _strip_q(os.environ.get("DATABASE_URL", ""))
    return v


def _is_localhost_dsn(url: str) -> bool:
    u = url.lower()
    return "localhost" in u or "127.0.0.1" in u


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


def upsert_via_supabase_rest(rows: list[tuple], *, chunk_size: int = 300) -> None:
    base = _supabase_rest_base()
    key = _service_role_for_rest()
    if not base or not key:
        raise ValueError("PostgREST 用の URL / service_role が不足しています")

    endpoint = f"{base}/rest/v1/numbers4_draws?on_conflict=draw_number"
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
        print(
            "🔑 Supabase CLI のログイン情報で service_role を取得しました（メモリ内のみ・ファイルには書きません）"
        )

    if args.min_year is not None or args.max_year is not None:
        if args.min_year is None or args.max_year is None:
            print("❌ 年で絞る場合は --min-year と --max-year の両方を指定してください")
            sys.exit(1)
        rows = load_csv_files_for_year_range(args.min_year, args.max_year)
    else:
        rows = load_all_csv_files()
        print(f"📊 全月次CSVから {len(rows)} 行を読み込み")

    if not rows:
        print("⚠️ 投入する行がありません")
        return

    if args.draw_numbers:
        want = set(args.draw_numbers)
        before = len(rows)
        rows = [r for r in rows if r[0] in want]
        print(f"🎯 --draw-number フィルタ: {before} 行 → {len(rows)} 行（対象: {sorted(want)}）")
        if not rows:
            print("⚠️ フィルタ後に行がありません")
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
        print("🔌 PostgREST 経由で UPSERT します（service_role）")
        try:
            upsert_via_supabase_rest(rows)
        except (ValueError, RuntimeError) as e:
            print(f"❌ {e}")
            sys.exit(1)
        return

    if not db_url:
        print(
            "❌ Postgres 接続情報がありません。.env.local に次のいずれかを設定してください:\n"
            "   • SUPABASE_DATABASE_URL または SUPABASE_DB_PASSWORD\n"
            "   • または DATABASE_URL（ローカル Postgres）\n"
            "   • または DATABASE_URL が localhost のままなら SUPABASE_SERVICE_ROLE_KEY（PostgREST）\n"
            "   ※ anon キーだけでは投入できません。"
        )
        sys.exit(1)
    if "?schema" in db_url:
        db_url = db_url.split("?schema")[0]

    try:
        conn = psycopg2.connect(db_url)
    except Exception as e:
        print(f"❌ Postgres 接続失敗: {e}")
        if _is_localhost_dsn(db_url) and _supabase_rest_base():
            if not _service_role_for_rest():
                print(
                    "   💡 このマシンで supabase login 済みなら:\n"
                    "      python tools/load_numbers4_csv_to_postgres.py --use-cli-login\n"
                    "      または .env.local に SUPABASE_SERVICE_ROLE_KEY / SUPABASE_DATABASE_URL を追加。"
                )
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

"""
predictions/daily の JSON を Supabase（PostgREST）の numbers4_daily_prediction_documents に UPSERT。

  python tools/load_numbers4_daily_json_to_postgres.py --use-cli-login

  ※ ペイロードが大きいのでデフォルト chunk は小さめ（--chunk-size で調整）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

from tools.daily_predictions_json_common import collect_daily_prediction_records
from tools.load_numbers4_csv_to_postgres import (
    inject_service_role_from_supabase_cli,
    resolve_supabase_project_ref,
    _service_role_for_rest,
    _supabase_rest_base,
)

load_dotenv(os.path.join(ROOT, ".env"))
load_dotenv(os.path.join(ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(ROOT, "apps", "web", ".env.local"), override=True)


def upsert_daily_documents_via_rest(
    records: list, *, chunk_size: int = 12
) -> None:
    base = _supabase_rest_base()
    key = _service_role_for_rest()
    if not base or not key:
        raise ValueError("PostgREST 用の URL / service_role が不足しています")

    endpoint = (
        f"{base}/rest/v1/numbers4_daily_prediction_documents"
        "?on_conflict=target_draw_number,doc_kind,method_slug"
    )
    rows = [
        {
            "target_draw_number": r.target_draw_number,
            "doc_kind": r.doc_kind,
            "method_slug": r.method_slug,
            "relative_path": r.relative_path,
            "payload": r.payload,
            "payload_sha256": r.payload_sha256,
            "file_mtime": r.file_mtime,
        }
        for r in records
    ]
    total = 0
    n = len(rows)
    for i in range(0, n, chunk_size):
        chunk = rows[i : i + chunk_size]
        body = json.dumps(chunk, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(endpoint, data=body, method="POST")
        req.add_header("apikey", key)
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "resolution=merge-duplicates,return=minimal")
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:4000]
            raise RuntimeError(
                f"PostgREST HTTP {e.code} (chunk {i // chunk_size + 1}): {err_body}"
            ) from e
        total += len(chunk)
        print(f"   … {total} / {n} 件送信")

    print(f"✅ numbers4_daily_prediction_documents に {n} 件 UPSERT しました")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="predictions/daily JSON → Supabase PostgREST"
    )
    p.add_argument(
        "--use-cli-login",
        action="store_true",
        help="supabase login 済み CLI で service_role を取得",
    )
    p.add_argument("--project-ref", default=None)
    p.add_argument(
        "--chunk-size",
        type=int,
        default=12,
        help="1リクエストあたりの行数（大きいと 413 / タイムアウトしやすい）",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if not args.use_cli_login:
        print("❌ --use-cli-login を付けて実行してください（リモート投入用）")
        sys.exit(1)

    ref = resolve_supabase_project_ref(args.project_ref)
    inject_service_role_from_supabase_cli(ref)
    print(
        "🔑 Supabase CLI で service_role を取得しました（メモリ内のみ）"
    )

    records, skipped = collect_daily_prediction_records()
    print(f"📂 対象 {len(records)} 件（パターン外スキップ {skipped}）")

    if not records:
        print("⚠️ 投入する行がありません")
        return

    if args.dry_run:
        return

    print(
        f"🔌 PostgREST UPSERT（chunk={args.chunk_size}）…"
    )
    try:
        upsert_daily_documents_via_rest(records, chunk_size=args.chunk_size)
    except (ValueError, RuntimeError) as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

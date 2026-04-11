"""
predictions/daily のロト6 JSON を Supabase loto6_daily_prediction_documents に UPSERT。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

from tools.daily_predictions_json_common import collect_daily_prediction_records_for_lottery
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
        f"{base}/rest/v1/loto6_daily_prediction_documents"
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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    req = urllib.request.Request(endpoint, data=body, method="POST")
                    req.add_header("apikey", key)
                    req.add_header("Authorization", f"Bearer {key}")
                    req.add_header("Content-Type", "application/json")
                    req.add_header("Prefer", "resolution=merge-duplicates,return=minimal")
                with urllib.request.urlopen(req, timeout=300) as resp:
                    resp.read()
                break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")[:4000]
                if e.code in (502, 503, 504) and attempt < max_retries - 1:
                    wait = 2**attempt * 5
                    print(f"   ⚠️ HTTP {e.code} — {wait}秒後にリトライ ({attempt + 1}/{max_retries})")
                    time.sleep(wait)
                    continue
                raise RuntimeError(
                    f"PostgREST HTTP {e.code} (chunk {i // chunk_size + 1}): {err_body}"
                ) from e
        total += len(chunk)
        print(f"   … {total} / {n} 件送信")

    print(f"✅ loto6_daily_prediction_documents に {n} 件 UPSERT しました")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="predictions/daily のロト6 JSON → Supabase PostgREST"
    )
    p.add_argument("--use-cli-login", action="store_true")
    p.add_argument("--project-ref", default=None)
    p.add_argument("--chunk-size", type=int, default=12)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--skip-if-unconfigured",
        action="store_true",
        help="NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY が無いときは成功終了",
    )
    p.add_argument("--target-draw-number", type=int, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.use_cli_login:
        ref = resolve_supabase_project_ref(args.project_ref)
        inject_service_role_from_supabase_cli(ref)
        print("🔑 Supabase CLI で service_role を取得しました")
    else:
        base = _supabase_rest_base()
        key = _service_role_for_rest()
        if not base or not key:
            if args.skip_if_unconfigured:
                print("⚠️ Supabase 未設定のため loto6_daily_prediction_documents UPSERT をスキップ")
                return
            print("❌ PostgREST 用の認証がありません")
            sys.exit(1)
        print("🔑 環境変数で PostgREST に接続します")

    records, skipped = collect_daily_prediction_records_for_lottery(
        lottery="loto6",
        target_draw_number=args.target_draw_number,
    )
    hint = (
        f"（回号 {args.target_draw_number} のみ）"
        if args.target_draw_number is not None
        else ""
    )
    print(f"📂 対象 {len(records)} 件{hint}（スキップ {skipped}）")

    if not records:
        print("⚠️ 投入する行がありません")
        return

    if args.dry_run:
        return

    try:
        upsert_daily_documents_via_rest(records, chunk_size=args.chunk_size)
    except (ValueError, RuntimeError) as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

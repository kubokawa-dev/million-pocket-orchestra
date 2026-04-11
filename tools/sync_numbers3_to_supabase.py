#!/usr/bin/env python3
"""
Numbers3 のリモート（Supabase）向け一括同期:
  1) numbers3_draws … lottery.db と numbers3/*.csv をマージして UPSERT
  2) numbers3_daily_prediction_documents … predictions/daily の JSON を UPSERT

前提:
  - NEXT_PUBLIC_SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY（または --use-cli-login）
  - lottery.db は .gitignore のため CI には無い。ローカルでフル投入するか、
    CSV をコミットして CI / 本番同期に使う。

例:
  SUPABASE_USE_REST=1 python tools/sync_numbers3_to_supabase.py
  SUPABASE_USE_REST=1 python tools/sync_numbers3_to_supabase.py --skip-if-unconfigured
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Numbers3 → Supabase 一式同期")
    p.add_argument(
        "--skip-if-unconfigured",
        action="store_true",
        help="認証が無いときは両ステップともスキップ（フォーク・未設定 CI 向け）",
    )
    p.add_argument(
        "--use-cli-login",
        action="store_true",
        help="supabase login 済み CLI で service_role を取得（draws / daily 共通）",
    )
    p.add_argument("--project-ref", default=None)
    p.add_argument(
        "--daily-chunk-size",
        type=int,
        default=24,
        help="numbers3_daily_prediction_documents の PostgREST チャンク",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    py = sys.executable
    db = os.path.join(ROOT, "lottery.db")
    env = os.environ.copy()
    if env.get("SUPABASE_USE_REST") is None:
        env["SUPABASE_USE_REST"] = "1"

    draw_cmd = [
        py,
        os.path.join(ROOT, "tools", "load_numbers3_csv_to_postgres.py"),
    ]
    if args.use_cli_login:
        draw_cmd.append("--use-cli-login")
        if args.project_ref:
            draw_cmd.extend(["--project-ref", args.project_ref])
    if args.skip_if_unconfigured:
        draw_cmd.append("--skip-if-unconfigured")

    if os.path.isfile(db):
        draw_cmd.extend(["--source", "both", "--sqlite-path", db])
    else:
        draw_cmd.extend(["--source", "csv"])

    print("=" * 60, flush=True)
    print("Step 1/2: numbers3_draws → Supabase", flush=True)
    print("=" * 60, flush=True)
    r = subprocess.run(draw_cmd, cwd=ROOT, env=env)
    if r.returncode != 0:
        return r.returncode

    daily_cmd = [
        py,
        os.path.join(ROOT, "tools", "load_numbers3_daily_json_to_postgres.py"),
        "--chunk-size",
        str(args.daily_chunk_size),
    ]
    if args.use_cli_login:
        daily_cmd.append("--use-cli-login")
        if args.project_ref:
            daily_cmd.extend(["--project-ref", args.project_ref])
    if args.skip_if_unconfigured:
        daily_cmd.append("--skip-if-unconfigured")

    print("", flush=True)
    print("=" * 60, flush=True)
    print("Step 2/2: numbers3_daily_prediction_documents → Supabase", flush=True)
    print("=" * 60, flush=True)
    r = subprocess.run(daily_cmd, cwd=ROOT, env=env)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())

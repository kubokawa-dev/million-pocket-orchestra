"""
Numbers3 自動予測パイプライン（存在するスクリプトのみ実行）
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable or "python"


def run(cmd: str) -> None:
    print(f"[run] {cmd}")
    res = subprocess.run(cmd, cwd=ROOT, shell=True)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def run_if_exists(path: str, *, required: bool = False) -> bool:
    abs_path = os.path.join(ROOT, path)
    if not os.path.exists(abs_path):
        msg = f"[skip] not found: {path}"
        if required:
            print(f"[error] {msg}")
            raise SystemExit(1)
        print(msg)
        return False
    run(f'"{PY}" "{abs_path}"')
    return True


def main() -> None:
    print("=" * 60)
    print("🚀 Numbers3 自動予測パイプライン")
    print("=" * 60)

    print("\n[Step 1] 最新データの取得")
    run_if_exists("tools/scrape_numbers3_rakuten.py")

    print("\n[Step 2] アンサンブル予測")
    # numbers3 の実装がある場合のみ実行
    ran = run_if_exists("numbers3/predict_ensemble.py")
    if not ran:
        print("⚠️ numbers3/predict_ensemble.py が未実装のため、予測生成はスキップしました")

    print("\n✅ Numbers3 パイプライン完了")


if __name__ == "__main__":
    main()

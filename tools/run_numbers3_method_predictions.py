"""
Numbers3 手法別予測ランナー（numbers3 実装がある場合のみ実行）
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable or "python"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Numbers3 method predictions")
    parser.add_argument("--methods", type=str, default="")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--methods-dir", type=str, default=None)
    args = parser.parse_args()

    script = os.path.join(ROOT, "numbers3", "run_method_predictions.py")
    if not os.path.exists(script):
        print("⚠️ numbers3/run_method_predictions.py が未実装のためスキップしました")
        return

    cmd = [PY, script, "--limit", str(args.limit), "--top", str(args.top)]
    if args.methods:
        cmd.extend(["--methods", args.methods])
    if args.methods_dir:
        cmd.extend(["--methods-dir", args.methods_dir])

    print(f"[run] {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=ROOT)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from collections import defaultdict

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from numbers3.prediction_utils import get_predictions_dir, load_predictions_by_draw


def detect_latest_draw() -> int:
    pdir = get_predictions_dir()
    files = [
        fn
        for fn in os.listdir(pdir)
        if fn.startswith("numbers3_") and fn.endswith(".json")
    ]
    if not files:
        raise RuntimeError("numbers3_*.json がありません")
    files.sort(reverse=True)
    return int(files[0][9:-5])


def main() -> None:
    parser = argparse.ArgumentParser(description="Numbers3 JSONサマリー生成")
    parser.add_argument("--draw", type=int, required=False)
    parser.add_argument("--output", type=str, required=False)
    args = parser.parse_args()

    draw = args.draw if args.draw is not None else detect_latest_draw()
    data = load_predictions_by_draw(draw)
    if not data:
        raise SystemExit(f"numbers3_{draw}.json が見つかりません")

    stats = defaultdict(lambda: {"count": 0, "best_rank": 999})
    preds = data.get("predictions", [])
    for entry in preds:
        for p in entry.get("top_predictions", []):
            n = str(p.get("number", "")).zfill(3)
            r = int(p.get("rank", 999))
            stats[n]["count"] += 1
            stats[n]["best_rank"] = min(stats[n]["best_rank"], r)

    ranked = sorted(stats.items(), key=lambda x: (-x[1]["count"], x[1]["best_rank"], x[0]))[:20]

    lines = []
    lines.append(f"# Numbers3 第{draw}回 サマリー")
    lines.append("")
    lines.append(f"- 予測回数: {len(preds)}")
    lines.append("")
    lines.append("| 順位 | 番号 | 出現回数 | 最高順位 |")
    lines.append("|:---:|:---:|:---:|:---:|")
    for i, (n, s) in enumerate(ranked, 1):
        lines.append(f"| {i} | `{n}` | {s['count']} | {s['best_rank']} |")
    lines.append("")

    text = "\n".join(lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"saved: {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()

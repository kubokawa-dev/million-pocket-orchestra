from __future__ import annotations

import argparse
import json
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
    parser = argparse.ArgumentParser(description="Numbers3 予算プラン生成")
    parser.add_argument("--draw", type=int, required=False)
    args = parser.parse_args()

    draw = args.draw if args.draw is not None else detect_latest_draw()
    data = load_predictions_by_draw(draw)
    if not data:
        raise SystemExit(f"numbers3_{draw}.json が見つかりません")

    latest = data.get("predictions", [])[-1] if data.get("predictions") else {}
    top = latest.get("top_predictions", [])
    plan_5 = top[:5]
    plan_10 = top[:10]

    out = {
        "target_draw_number": draw,
        "planner_version": "numbers3-v1",
        "plan_5": {
            "budget": "1,000円",
            "slots": 5,
            "recommendations": plan_5,
        },
        "plan_10": {
            "budget": "2,000円",
            "slots": 10,
            "recommendations": plan_10,
        },
    }
    p = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "predictions",
        "daily",
        f"budget_plan_numbers3_{draw}.json",
    )
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"saved: {p}")


if __name__ == "__main__":
    main()

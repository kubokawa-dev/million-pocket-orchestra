from __future__ import annotations

import argparse
import os
import sys
from typing import List

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from numbers3.core import METHODS, load_numbers3_draws, predict_by_method, resolve_target_draw_number, to_scored_df
from numbers3.save_method_prediction_json import save_method_prediction_to_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Numbers3 手法別予測")
    parser.add_argument("--methods", type=str, default="")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--methods-dir", type=str, default=None)
    args = parser.parse_args()

    methods: List[str]
    if args.methods.strip():
        methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    else:
        methods = METHODS[:]

    df = load_numbers3_draws()
    target_draw = resolve_target_draw_number(df)

    print(f"🧭 Numbers3 手法別予測を開始: target={target_draw}, methods={methods}")
    for method in methods:
        preds = predict_by_method(df, method, limit=args.limit)
        out_df = to_scored_df(preds)
        save_method_prediction_to_json(
            predictions_df=out_df,
            method=method,
            target_draw_number=target_draw,
            top_n=args.top,
            metadata={"limit": args.limit, "total_predictions": len(out_df)},
        )


if __name__ == "__main__":
    main()

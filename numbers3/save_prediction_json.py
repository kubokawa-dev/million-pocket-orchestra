from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict

import pandas as pd

from numbers3.prediction_utils import get_predictions_dir


def save_prediction_to_json(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict[str, float],
    target_draw_number: int,
    top_n: int = 20,
) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    predictions_dir = get_predictions_dir()
    draw_file = os.path.join(predictions_dir, f"numbers3_{target_draw_number}.json")

    if os.path.exists(draw_file):
        with open(draw_file, "r", encoding="utf-8") as f:
            daily_data = json.load(f)
    else:
        daily_data = {
            "draw_number": target_draw_number,
            "target_draw_number": target_draw_number,
            "date": date_str,
            "predictions": [],
        }

    top_predictions = []
    for idx, row in predictions_df.head(top_n).iterrows():
        top_predictions.append(
            {
                "rank": int(idx + 1),
                "number": str(row["prediction"]).zfill(3),
                "score": round(float(row["score"]), 4),
            }
        )

    entry = {
        "time": now.isoformat(),
        "time_jst": (now.replace(tzinfo=None) + pd.Timedelta(hours=9)).strftime("%H:%M"),
        "ensemble_weights": ensemble_weights,
        "top_predictions": top_predictions,
    }
    daily_data["predictions"].append(entry)
    daily_data["last_updated"] = now.isoformat()
    daily_data["prediction_count"] = len(daily_data["predictions"])

    with open(draw_file, "w", encoding="utf-8") as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 予測結果をJSONに保存: {draw_file}")
    return draw_file

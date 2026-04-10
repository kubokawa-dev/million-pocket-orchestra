from __future__ import annotations

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from numbers3.core import (
    METHODS,
    aggregate_method_predictions,
    load_numbers3_draws,
    predict_by_method,
    resolve_target_draw_number,
)
from numbers3.save_prediction_history import save_ensemble_prediction
from numbers3.save_prediction_json import save_prediction_to_json


DEFAULT_WEIGHTS = {
    "box_model": 30.0,
    "ml_neighborhood": 24.0,
    "even_odd_pattern": 22.0,
    "lgbm_box": 22.0,
    "sequential_pattern": 20.0,
    "cold_revival": 20.0,
    "hot_pair": 18.0,
    "adjacent_digit": 18.0,
    "digit_freq_box": 16.0,
    "global_frequency": 16.0,
    "lightgbm": 14.0,
    "state_chain": 14.0,
    "box_pattern": 14.0,
    "low_sum_specialist": 12.0,
}


def run_ensemble_prediction_cli() -> None:
    df = load_numbers3_draws()
    target_draw = resolve_target_draw_number(df)

    print("=" * 60)
    print(f"🎯 Numbers3 アンサンブル予測: 第{target_draw}回")
    print("=" * 60)

    predictions_by_model = {
        method: predict_by_method(df, method, limit=200) for method in METHODS
    }
    final_df = aggregate_method_predictions(
        predictions_by_model,
        method_weights=DEFAULT_WEIGHTS,
        top_n=300,
    )

    save_ensemble_prediction(
        predictions_df=final_df,
        ensemble_weights=DEFAULT_WEIGHTS,
        predictions_by_model=predictions_by_model,
        target_draw_number=target_draw,
        notes="numbers3 ensemble prediction",
    )
    save_prediction_to_json(
        predictions_df=final_df,
        ensemble_weights=DEFAULT_WEIGHTS,
        target_draw_number=target_draw,
        top_n=20,
    )

    print("✅ Numbers3 ensemble prediction completed")


if __name__ == "__main__":
    run_ensemble_prediction_cli()

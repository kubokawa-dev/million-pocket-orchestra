"""
Numbers4 手法特化の予測パイプライン
"""
import argparse
import os
import sys
from typing import Callable, Dict, List

import pandas as pd

# プロジェクトルートをパスに追加
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.utils import get_db_connection, load_all_numbers4_draws
from numbers4.save_prediction_history import get_latest_draw_info
from numbers4.save_method_prediction_json import save_method_prediction_to_json
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_from_exploratory_heuristics,
    predict_from_extreme_patterns,
    predict_from_digit_repetition_model_n4,
    predict_from_digit_continuation_model_n4,
    predict_from_large_change_model_n4,
    predict_from_realistic_frequency_model_n4,
    predict_from_transition_probability_n4,
    predict_from_global_frequency_n4,
    predict_from_box_pattern_analysis_n4,
    predict_from_hot_pair_combination_n4,
    predict_from_digit_frequency_box_n4,
    predict_from_cold_number_revival_n4,
    predict_from_ml_neighborhood_search_n4,
    predict_from_even_odd_pattern_n4,
    predict_from_low_sum_specialist_n4,
    predict_from_sequential_pattern_n4,
    predict_from_lightgbm_with_probs,
    predict_from_model_state_v2,
)
from numbers4.box_learning import (
    load_box_model,
    predict_boxes_from_model,
    predict_numbers_from_boxes,
    rebuild_box_model,
)


DEFAULT_METHODS = [
    "box_model",
    "ml_neighborhood",
    "even_odd_pattern",
    "low_sum_specialist",
    "sequential_pattern",
    "cold_revival",
    "hot_pair",
    "box_pattern",
    "digit_freq_box",
    "global_frequency",
]


def _normalize_predictions(predictions: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for pred in predictions:
        s = str(pred)
        if s.isdigit():
            s = s.zfill(4)
        if len(s) != 4 or not s.isdigit():
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _to_scored_df(predictions: List[str]) -> pd.DataFrame:
    if not predictions:
        return pd.DataFrame({'prediction': [], 'score': []})
    n = len(predictions)
    rows = []
    for i, pred in enumerate(predictions):
        score = (n - i) / n * 100.0
        rows.append({'prediction': pred, 'score': score})
    return pd.DataFrame(rows)


def _predict_box_model(limit: int) -> List[str]:
    box_model_state = load_box_model()
    if not box_model_state.get('box_counts'):
        rebuild_box_model()
        box_model_state = load_box_model()
    box_predictions = predict_boxes_from_model(box_model_state, limit=limit)
    predictions_box_model = predict_numbers_from_boxes(box_predictions, limit=limit)
    return [num for num, _ in predictions_box_model]


def _predict_lightgbm(df: pd.DataFrame, limit: int) -> List[str]:
    predictions, _ = predict_from_lightgbm_with_probs(df, limit=limit)
    return predictions


def _get_target_draw_number() -> int:
    conn = get_db_connection()
    try:
        latest_draw = get_latest_draw_info(conn)
        if latest_draw and latest_draw.get('draw_number'):
            return int(latest_draw['draw_number']) + 1
    finally:
        conn.close()
    raise RuntimeError("最新の抽選回号が取得できません")


def _build_method_map(df: pd.DataFrame) -> Dict[str, Callable[[int], List[str]]]:
    return {
        "basic_stats": lambda limit: predict_from_basic_stats(df, limit),
        "advanced_heuristics": lambda limit: predict_from_advanced_heuristics(df, limit),
        "exploratory": lambda limit: predict_from_exploratory_heuristics(df, limit),
        "extreme_patterns": lambda limit: predict_from_extreme_patterns(df, limit),
        "digit_repetition": lambda limit: predict_from_digit_repetition_model_n4(df, limit),
        "digit_continuation": lambda limit: predict_from_digit_continuation_model_n4(df, limit),
        "large_change": lambda limit: predict_from_large_change_model_n4(df, limit),
        "realistic_frequency": lambda limit: predict_from_realistic_frequency_model_n4(df, limit),
        "transition_probability": lambda limit: predict_from_transition_probability_n4(df, limit),
        "global_frequency": lambda limit: predict_from_global_frequency_n4(df, limit),
        "box_pattern": lambda limit: predict_from_box_pattern_analysis_n4(df, limit),
        "hot_pair": lambda limit: predict_from_hot_pair_combination_n4(df, limit),
        "digit_freq_box": lambda limit: predict_from_digit_frequency_box_n4(df, limit),
        "cold_revival": lambda limit: predict_from_cold_number_revival_n4(df, limit),
        "box_model": lambda limit: _predict_box_model(limit),
        "ml_neighborhood": lambda limit: predict_from_ml_neighborhood_search_n4(df, limit),
        "even_odd_pattern": lambda limit: predict_from_even_odd_pattern_n4(df, limit),
        "low_sum_specialist": lambda limit: predict_from_low_sum_specialist_n4(df, limit),
        "sequential_pattern": lambda limit: predict_from_sequential_pattern_n4(df, limit),
        "lightgbm": lambda limit: _predict_lightgbm(df, limit),
        "state_chain": lambda limit: predict_from_model_state_v2(limit=limit),
    }


def main():
    parser = argparse.ArgumentParser(description="Numbers4 手法特化の予測を生成")
    parser.add_argument(
        "--method",
        action="append",
        help="実行する手法名（複数指定可）",
    )
    parser.add_argument(
        "--methods",
        type=str,
        help="カンマ区切りの手法リスト",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="生成する予測数（デフォルト: 200）",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="JSONに保存する上位件数（デフォルト: 20）",
    )
    parser.add_argument(
        "--methods-dir",
        type=str,
        default=None,
        help="手法別予測JSONの出力ディレクトリ",
    )
    args = parser.parse_args()

    methods: List[str] = []
    if args.method:
        methods.extend(args.method)
    if args.methods:
        methods.extend([m.strip() for m in args.methods.split(",") if m.strip()])
    if not methods:
        methods = DEFAULT_METHODS[:]

    print(f"🧭 手法別予測を開始: {methods}")

    all_draws_df = load_all_numbers4_draws()
    if all_draws_df.empty:
        raise SystemExit("❌ 抽選データが見つかりません")

    target_draw = _get_target_draw_number()
    method_map = _build_method_map(all_draws_df)

    for method in methods:
        if method not in method_map:
            print(f"⚠️ 未対応の手法: {method}")
            continue

        print(f"\n[Method] {method}")
        try:
            predictions = method_map[method](args.limit)
            predictions = _normalize_predictions(predictions)
            df = _to_scored_df(predictions)

            save_method_prediction_to_json(
                predictions_df=df,
                method=method,
                target_draw_number=target_draw,
                top_n=args.top,
                metadata={
                    "limit": args.limit,
                    "total_predictions": len(df),
                },
            )
        except Exception as e:
            print(f"❌ 予測失敗: {method} ({e})")


if __name__ == "__main__":
    main()

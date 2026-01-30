"""
攻めモードの当たりやすさを過去データで評価し、最適な設定を探索する。

使い方:
  python numbers4/tune_aggressive.py --tune
  python numbers4/tune_aggressive.py --min-draw 6891 --max-draw 6898
"""
import argparse
import json
import os
import re
import sys
from itertools import product
from typing import Dict, List, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from numbers4.summarize_from_json import (
    aggregate_predictions,
    build_aggressive_recommendations,
    get_digit_signature,
)
from tools.utils import get_db_connection

PREDICTIONS_DIR = os.path.join(ROOT_DIR, "predictions", "daily")
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "numbers4", "aggressive_config.json")


def load_actual_results() -> Dict[int, str]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT draw_number, numbers FROM numbers4_draws")
        rows = cur.fetchall()
    finally:
        conn.close()
    results = {}
    for draw_number, numbers in rows:
        if numbers:
            results[int(draw_number)] = str(numbers).strip()
    return results


def list_prediction_files() -> List[str]:
    files = []
    for name in os.listdir(PREDICTIONS_DIR):
        if re.match(r"numbers4_\d+\.json$", name):
            files.append(os.path.join(PREDICTIONS_DIR, name))
    return sorted(files, key=lambda p: int(re.findall(r"(\d+)", os.path.basename(p))[-1]))


def evaluate_config(
    config: Dict,
    files: List[str],
    actuals: Dict[int, str],
    top_n: int,
    min_draw: int | None = None,
    max_draw: int | None = None,
    print_per_draw: bool = False,
) -> Tuple[int, int, int]:
    hits_exact = 0
    hits_box = 0
    total = 0

    for path in files:
        draw_number = int(re.findall(r"(\d+)", os.path.basename(path))[-1])
        if min_draw and draw_number < min_draw:
            continue
        if max_draw and draw_number > max_draw:
            continue
        actual = actuals.get(draw_number)
        if not actual:
            continue

        with open(path, "r", encoding="utf-8") as f:
            daily_data = json.load(f)
        aggregated = aggregate_predictions(daily_data)
        recs = build_aggressive_recommendations(
            daily_data, aggregated, top_n=top_n, config_override=config
        )
        numbers = [r["number"] for r in recs]
        actual_sig = get_digit_signature(actual)
        exact = actual in numbers
        box = any(get_digit_signature(n) == actual_sig for n in numbers)

        hits_exact += 1 if exact else 0
        hits_box += 1 if box else 0
        total += 1

        if print_per_draw:
            status = "EXACT" if exact else ("BOX" if box else "-")
            print(f"{draw_number}: {actual} -> {status}")

    return hits_exact, hits_box, total


def main():
    parser = argparse.ArgumentParser(description="攻めモードの評価とチューニング")
    parser.add_argument("--top", type=int, default=20, help="攻めモードの候補数")
    parser.add_argument("--top-list", type=str, default=None, help="候補数の複数指定（例: 20,30,40）")
    parser.add_argument("--min-draw", type=int, default=None, help="評価対象の最小回号")
    parser.add_argument("--max-draw", type=int, default=None, help="評価対象の最大回号")
    parser.add_argument("--tune", action="store_true", help="簡易チューニングを実行")
    parser.add_argument("--print-per-draw", action="store_true", help="回号ごとの結果を表示")
    parser.add_argument(
        "--write-config", type=str, default=DEFAULT_CONFIG_PATH, help="設定の保存先"
    )
    args = parser.parse_args()

    actuals = load_actual_results()
    files = list_prediction_files()

    base_config = {}
    base_hits = evaluate_config(
        base_config,
        files,
        actuals,
        top_n=args.top,
        min_draw=args.min_draw,
        max_draw=args.max_draw,
        print_per_draw=args.print_per_draw,
    )
    print(f"[base] exact={base_hits[0]} box={base_hits[1]} total={base_hits[2]}")

    if not args.tune:
        return

    top_list = [args.top]
    if args.top_list:
        try:
            top_list = [int(x.strip()) for x in args.top_list.split(",") if x.strip()]
        except ValueError:
            top_list = [args.top]

    coverage_weights = [10, 12, 14]
    similar_main = [4, 6, 8]
    similar_similar = [5, 7, 9]
    both_bonus = [8, 12]
    ml_bonus = [6, 10]
    best_rank_weight = [1.0, 1.4]
    appearance_weight = [0.4, 0.6]
    avg_score_weight = [0.1, 0.3]
    parent_rank_weight = [0.5, 0.8]

    best = None
    best_config = None

    for cw, sm, ss, bb, mb, brw, aw, asw, prw in product(
        coverage_weights,
        similar_main,
        similar_similar,
        both_bonus,
        ml_bonus,
        best_rank_weight,
        appearance_weight,
        avg_score_weight,
        parent_rank_weight,
    ):
        for top_n in top_list:
            config = {
                "coverage_weight_main": cw,
                "coverage_weight_similar": cw,
                "similar_bonus_main": sm,
                "similar_bonus_similar": ss,
                "both_bonus": bb,
                "ml_bonus": mb,
                "best_rank_weight": brw,
                "appearance_weight": aw,
                "avg_score_weight": asw,
                "parent_rank_weight": prw,
                "top_n": top_n,
            }
            exact, box, total = evaluate_config(
                config,
                files,
                actuals,
                top_n=top_n,
                min_draw=args.min_draw,
                max_draw=args.max_draw,
            )
            score = (exact, box, top_n)
            if best is None or score > best:
                best = score
                best_config = config

    if best_config:
        print(f"[best] exact={best[0]} box={best[1]} total={base_hits[2]}")
        print(json.dumps(best_config, ensure_ascii=False, indent=2))
        os.makedirs(os.path.dirname(args.write_config), exist_ok=True)
        with open(args.write_config, "w", encoding="utf-8") as f:
            json.dump(best_config, f, ensure_ascii=False, indent=2)
        print(f"✅ saved: {args.write_config}")


if __name__ == "__main__":
    main()

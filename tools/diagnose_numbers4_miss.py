import os
import sys
import pandas as pd
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.utils import load_all_numbers4_draws
from numbers4.learning_logic import learn_model_from_data
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model,
)


def analyze_miss(target_number: str, cutoff_date: str | None = None):
    """
    Analyze why a target_number (e.g., '1350') may have been missed.
    Uses only data up to cutoff_date (YYYY/MM/DD). If None, uses all but last row.
    """
    df = load_all_numbers4_draws()
    # Expand winning_numbers into digits d1..d4
    df = df.copy()
    df['d1'] = df['winning_numbers'].str[0].astype(int)
    df['d2'] = df['winning_numbers'].str[1].astype(int)
    df['d3'] = df['winning_numbers'].str[2].astype(int)
    df['d4'] = df['winning_numbers'].str[3].astype(int)

    if cutoff_date:
        df = df[df['date'] <= cutoff_date]
    else:
        # exclude last observed draw to simulate pre-draw state
        df = df.iloc[:-1]

    # Run three models
    basic = predict_from_basic_stats(df, 20)
    adv = predict_from_advanced_heuristics(df, 20)
    weights = learn_model_from_data(df)
    ml = predict_with_model(df, model_weights=weights, num_predictions=50)

    # Compute set/box forms
    target = target_number
    target_box = ''.join(sorted(target))

    def to_box_list(seq):
        return [''.join(sorted(x)) for x in seq]

    basic_hit = target in basic
    adv_hit = target in adv
    ml_hit = target in ml

    basic_box_hit = target_box in to_box_list(basic)
    adv_box_hit = target_box in to_box_list(adv)
    ml_box_hit = target_box in to_box_list(ml)

    # Explain counts and proximity
    def hamming(a, b):
        return sum(1 for x, y in zip(a, b) if x != y)

    # Top-N closeness examples
    def closest_examples(cands, k=5):
        scored = [(hamming(target, c), c) for c in cands]
        scored.sort()
        return scored[:k]

    print("=== Miss Analysis for Numbers4 ===")
    print(f"Target: {target} (box={target_box}) using history up to {df['date'].max()}")
    print("-- Straight prediction hits --")
    print(f"  basic: {basic_hit}")
    print(f"  adv:   {adv_hit}")
    print(f"  ml:    {ml_hit}")
    print("-- Box prediction hits --")
    print(f"  basic: {basic_box_hit}")
    print(f"  adv:   {adv_box_hit}")
    print(f"  ml:    {ml_box_hit}")

    if not any([basic_hit, adv_hit, ml_hit, basic_box_hit, adv_box_hit, ml_box_hit]):
        print("No model picked it. Showing closest candidates per model (by Hamming distance):")
        print("  basic:", closest_examples(basic))
        print("  adv:  ", closest_examples(adv))
        print("  ml:   ", closest_examples(ml))

    # Simple diagnostics on digits
    digits = list(map(int, list(target)))
    digit_counts = {
        'pos1': Counter(df['d1']),
        'pos2': Counter(df['d2']),
        'pos3': Counter(df['d3']),
        'pos4': Counter(df['d4']),
    }
    print("-- Positional frequencies for target digits --")
    for i, d in enumerate(digits, start=1):
        c = digit_counts[f'pos{i}'][d]
        print(f"  d{i}={d}: count={c}")


if __name__ == '__main__':
    # Analyze the reported miss: 6835 -> 1350, using history up to previous draw
    analyze_miss('1350')

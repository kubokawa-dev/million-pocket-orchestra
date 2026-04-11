from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from tools.utils import get_db_connection


METHODS = [
    "box_model",
    "ml_neighborhood",
    "even_odd_pattern",
    "lgbm_box",
    "sequential_pattern",
    "cold_revival",
    "hot_pair",
    "adjacent_digit",
    "digit_freq_box",
    "global_frequency",
    "lightgbm",
    "state_chain",
    "box_pattern",
    "low_sum_specialist",
]


@dataclass(frozen=True)
class DrawRecord:
    draw_number: int
    numbers: str


def load_numbers3_draws() -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            """
            SELECT draw_number, draw_date, numbers
            FROM numbers3_draws
            ORDER BY draw_number ASC
            """,
            conn,
        )
    finally:
        conn.close()

    if df.empty:
        return df
    df["numbers"] = df["numbers"].astype(str).str.zfill(3)
    df = df[df["numbers"].str.match(r"^\d{3}$", na=False)].copy()
    return df


def resolve_target_draw_number(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["draw_number"].max()) + 1


def generate_all_numbers3() -> List[str]:
    return [f"{n:03d}" for n in range(1000)]


def _stable_jitter(method: str, number: str) -> float:
    h = hashlib.sha256(f"{method}:{number}".encode("utf-8")).hexdigest()[:8]
    v = int(h, 16) / 0xFFFFFFFF
    return (v - 0.5) * 0.06


def _calc_features(df: pd.DataFrame) -> Dict:
    if df.empty:
        zero = [0.1] * 10
        return {
            "pos_freq": [zero[:], zero[:], zero[:]],
            "overall_freq": zero[:],
            "recent_numbers": set(),
            "cold_digits": {0, 1, 2},
            "hot_pairs": Counter(),
            "common_parity": {"EOE", "OEO", "EEE", "OOO"},
        }

    nums = df["numbers"].astype(str).str.zfill(3).tolist()
    recent = nums[-60:]
    all_digits = [int(ch) for n in nums for ch in n]
    overall = Counter(all_digits)

    pos_freq: List[List[float]] = []
    for pos in range(3):
        c = Counter(int(n[pos]) for n in nums)
        total = max(1, sum(c.values()))
        pos_freq.append([(c[d] + 1) / (total + 10) for d in range(10)])

    total_digits = max(1, len(all_digits))
    overall_freq = [(overall[d] + 1) / (total_digits + 10) for d in range(10)]

    recent_digits = [int(ch) for n in recent for ch in n]
    recent_count = Counter(recent_digits)
    cold_digits = {d for d, _ in sorted(recent_count.items(), key=lambda x: x[1])[:4]}

    pair_counter: Counter[Tuple[int, int]] = Counter()
    for n in nums:
        a, b, c = int(n[0]), int(n[1]), int(n[2])
        pair_counter[(a, b)] += 1
        pair_counter[(b, c)] += 1

    parity_counter = Counter("".join("E" if int(ch) % 2 == 0 else "O" for ch in n) for n in nums)
    common_parity = {p for p, _ in parity_counter.most_common(4)}

    return {
        "pos_freq": pos_freq,
        "overall_freq": overall_freq,
        "recent_numbers": set(recent),
        "cold_digits": cold_digits,
        "hot_pairs": pair_counter,
        "common_parity": common_parity,
    }


def _score_number(number: str, method: str, feat: Dict) -> float:
    digits = [int(ch) for ch in number]
    base = (
        feat["pos_freq"][0][digits[0]]
        + feat["pos_freq"][1][digits[1]]
        + feat["pos_freq"][2][digits[2]]
    ) / 3.0
    base += sum(feat["overall_freq"][d] for d in digits) / 6.0

    if number in feat["recent_numbers"]:
        base *= 0.75

    if method == "box_model":
        base += 0.25 if len(set(digits)) == 3 else -0.05
    elif method == "cold_revival":
        base += sum(0.08 for d in digits if d in feat["cold_digits"])
    elif method == "hot_pair":
        base += feat["hot_pairs"][(digits[0], digits[1])] / 200.0
        base += feat["hot_pairs"][(digits[1], digits[2])] / 200.0
    elif method == "even_odd_pattern":
        parity = "".join("E" if d % 2 == 0 else "O" for d in digits)
        base += 0.16 if parity in feat["common_parity"] else -0.04
    elif method == "low_sum_specialist":
        s = sum(digits)
        base += max(0.0, (18 - s) / 30.0)
    elif method == "sequential_pattern":
        if abs(digits[0] - digits[1]) == 1 or abs(digits[1] - digits[2]) == 1:
            base += 0.14
    elif method == "adjacent_digit":
        if abs(digits[0] - digits[1]) <= 1 and abs(digits[1] - digits[2]) <= 1:
            base += 0.15
    elif method == "digit_freq_box":
        base += 0.18 if len(set(digits)) <= 2 else 0.03
    elif method == "global_frequency":
        base += sum(feat["overall_freq"][d] for d in set(digits)) / 5.0
    elif method == "box_pattern":
        pattern = sorted(Counter(digits).values(), reverse=True)
        base += 0.15 if pattern == [2, 1] else 0.1 if pattern == [1, 1, 1] else 0.0
    elif method == "state_chain":
        base += feat["hot_pairs"][(digits[0], digits[1])] / 260.0
    elif method in {"lightgbm", "lgbm_box", "ml_neighborhood"}:
        base += 0.05

    base += _stable_jitter(method, number)
    return base


def predict_by_method(df: pd.DataFrame, method: str, limit: int = 200) -> List[str]:
    feat = _calc_features(df)
    all_nums = generate_all_numbers3()
    scored = [(n, _score_number(n, method, feat)) for n in all_nums]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [n for n, _ in scored[:limit]]


def to_scored_df(predictions: List[str]) -> pd.DataFrame:
    rows = []
    n = max(1, len(predictions))
    for idx, number in enumerate(predictions):
        rows.append(
            {
                "prediction": number,
                "score": round((n - idx) / n * 100.0, 6),
            }
        )
    return pd.DataFrame(rows)


def aggregate_method_predictions(
    method_predictions: Dict[str, List[str]],
    method_weights: Dict[str, float],
    top_n: int = 200,
) -> pd.DataFrame:
    score_map: Dict[str, float] = {}
    contrib: Dict[str, List[str]] = {}
    for method, preds in method_predictions.items():
        w = method_weights.get(method, 1.0)
        n = max(1, len(preds))
        for i, p in enumerate(preds):
            rank_score = (n - i) / n
            score_map[p] = score_map.get(p, 0.0) + rank_score * w
            contrib.setdefault(p, []).append(method)

    rows = [
        {"prediction": p, "score": s, "contributing_models": sorted(contrib.get(p, []))}
        for p, s in score_map.items()
    ]
    out = pd.DataFrame(rows).sort_values("score", ascending=False).head(top_n).reset_index(drop=True)
    return out

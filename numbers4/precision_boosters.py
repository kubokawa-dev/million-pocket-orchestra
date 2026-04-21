"""Numbers4 精度ブースター集 (v17.0)

直近の精度向上のために導入した後処理＆特徴抽出ユーティリティ群。

🅰️ apply_digit_position_boost
    LightGBM の桁別確率を使い、特に弱点になりがちな d2/d3 桁の精度を強化する。

🅱️ predict_from_repetition_pattern_n4
    直近のホット数字を 2 桁以上含む「ゾロ目／ペア寄り」の候補を生成する新モデル。

🅱️ apply_repetition_bonus
    直近 N 回の繰り返し率がベースライン (≒49.6%) を上回っている場合、
    繰り返しを含む候補にスコアボーナスを付与する後処理。

🅳️ apply_category_diversity_bonus
    候補の出所モデル（カテゴリ）を集計し、上位候補の偏りを抑制してアンサンブルの
    多様性を強制的に確保する後処理。
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# モデルカテゴリ定義（🅳 アンサンブル多様性で使用）
# ---------------------------------------------------------------------------

METHOD_CATEGORIES: Dict[str, str] = {
    # ボックス特化系
    "box_model": "box",
    "box_pattern": "box",
    "hot_pair": "box",
    "digit_freq_box": "box",
    "lgbm_box": "box",
    # 機械学習系
    "lightgbm": "ml",
    "ml_model_new": "ml",
    "ml_neighborhood": "ml",
    # 構造／パターン系
    "even_odd_pattern": "pattern",
    "low_sum_specialist": "pattern",
    "sequential_pattern": "pattern",
    "adjacent_digit": "pattern",
    # 頻度／遷移系
    "transition_probability": "transition",
    "state_chain": "transition",
    "global_frequency": "transition",
    # 直近ホット／コールド系
    "cold_revival": "hot_cold",
    "digit_repetition": "hot_cold",
    "digit_continuation": "hot_cold",
    "realistic_frequency": "hot_cold",
    # 変化／ヒューリスティック系
    "large_change": "heuristic",
    "advanced_heuristics": "heuristic",
    "exploratory": "heuristic",
    "extreme_patterns": "heuristic",
    "basic_stats": "heuristic",
    # 🅱 新モデル
    "repetition_pattern": "hot_cold",
}


# ---------------------------------------------------------------------------
# 🅰️ d2/d3 を含む桁別ブースター
# ---------------------------------------------------------------------------

def apply_digit_position_boost(
    df: pd.DataFrame,
    preds_probs: Optional[Dict[str, Sequence[float]]],
    *,
    position_weights: Sequence[float] = (0.6, 1.4, 1.4, 0.6),
    boost_strength: float = 0.35,
    eps: float = 1e-12,
) -> pd.DataFrame:
    """LightGBM の桁別確率を使い、特に d2/d3 の精度を補正するスコアブーストを適用する。

    各候補に対して
        log_score = Σ_pos position_weights[pos] * log(p_pos[d_pos])
    を計算し、これを *boost_strength* 分だけ最終スコアに乗算で反映する。

    実績では `analysis_*.md` で d2/d3 が TOP3 に入らないケースが多発しているため、
    既定値では中央 2 桁を 1.4、両端 2 桁を 0.6 と中央寄せに設定している。

    Args:
        df: `prediction` と `score` を含む DataFrame。
        preds_probs: `{"d1": [10要素], ..., "d4": [10要素]}` の確率分布。
            None や欠損キーがある場合は何もせずに返す（安全フォールバック）。
        position_weights: 桁ごとの重み。デフォルトで d2/d3 を強調。
        boost_strength: ブーストの強さ。0 で無効、1 で素のログスコアをそのまま乗算。
        eps: log(0) 防止用の極小値。

    Returns:
        ブースト適用後にスコア降順で再ソートした DataFrame（コピー）。
    """
    if df is None or df.empty:
        return df
    if not preds_probs or not all(k in preds_probs for k in ("d1", "d2", "d3", "d4")):
        return df

    weights = np.asarray(position_weights, dtype=np.float64)
    if weights.shape[0] != 4:
        raise ValueError("position_weights must contain exactly 4 elements")

    # 各桁の log 確率テーブルを事前計算
    log_probs: Dict[str, np.ndarray] = {}
    for key in ("d1", "d2", "d3", "d4"):
        probs = np.asarray(preds_probs[key], dtype=np.float64)
        if probs.shape[0] != 10:
            return df  # 形が想定外なら何もしない
        log_probs[key] = np.log(probs + eps)

    # 4 桁文字列を整数配列にしておく（高速化）
    out = df.copy()
    digits_matrix = np.zeros((len(out), 4), dtype=np.int64)
    valid_mask = np.ones(len(out), dtype=bool)
    for row_idx, pred in enumerate(out["prediction"].astype(str).values):
        if not pred.isdigit() or len(pred) != 4:
            valid_mask[row_idx] = False
            continue
        for j, ch in enumerate(pred):
            digits_matrix[row_idx, j] = int(ch)

    pos_keys = ("d1", "d2", "d3", "d4")
    log_score = np.zeros(len(out), dtype=np.float64)
    for j, key in enumerate(pos_keys):
        log_score += weights[j] * log_probs[key][digits_matrix[:, j]]

    # 中央化して数値の暴れを抑える（平均 0、std 1 に正規化してから boost_strength 倍）
    if valid_mask.any():
        mean = log_score[valid_mask].mean()
        std = log_score[valid_mask].std()
        if std > 0:
            normalized = (log_score - mean) / std
        else:
            normalized = log_score - mean
        # 乗算ファクタ：exp(boost_strength * normalized)
        boost_factor = np.where(valid_mask, np.exp(boost_strength * normalized), 1.0)
        out["score"] = out["score"].astype(np.float64) * boost_factor

    out = out.sort_values(by="score", ascending=False).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# 🅱 ゾロ目／ペア検出 — 新モデル
# ---------------------------------------------------------------------------

def _has_repeat(num: str) -> bool:
    return len(set(num)) < len(num)


def _max_repeat_count(num: str) -> int:
    """同じ数字が最大何回出現するかを返す（4 ならゾロ目 AAAA）。"""
    if not num:
        return 0
    return max(Counter(num).values())


# 実データから観測される 4 桁ボックスタイプの理論的近似分布。
# AAAA は 0.1%、AAAB は 3.6%、AABB は 2.7%、AABC は 43.2%、ABCD は 50.4%。
# モデルが AAAA だらけにならないよう、希少パターンには強めのペナルティを掛ける。
BOX_TYPE_PRIOR: Dict[str, float] = {
    "AAAA": 0.001,
    "AAAB": 0.036,
    "AABB": 0.027,
    "AABC": 0.432,
    "ABCD": 0.504,
}


def _box_type_of(num: str) -> str:
    """``num`` のボックスタイプ（AAAA/AAAB/AABB/AABC/ABCD）を返す。"""
    counts = sorted(Counter(num).values(), reverse=True)
    if counts == [4]:
        return "AAAA"
    if counts == [3, 1]:
        return "AAAB"
    if counts == [2, 2]:
        return "AABB"
    if counts == [2, 1, 1]:
        return "AABC"
    return "ABCD"


def predict_from_repetition_pattern_n4(
    df: pd.DataFrame,
    limit: int = 150,
    *,
    recent_window: int = 30,
    hot_top_k: int = 6,
) -> List[str]:
    """直近のホット数字を 2 桁以上含む候補を集中生成するモデル（v17.0）。

    9227 や 7323 のように同じ数字が複数桁で出現するケース（AABC/AABB 型）に
    弱かったため、直近 ``recent_window`` 回でホットになっている数字を含む
    AABC・AABB 型を中心に候補を生成する。AAAA / AAAB は実データでも極めて稀なため、
    強めにダウンウェイトする（``BOX_TYPE_PRIOR`` を使用）。

    Args:
        df: 過去抽選データ（``d1``〜``d4`` 列を持つ DataFrame）。
        limit: 返す候補数の上限。
        recent_window: ホット数字を判定する直近回数。
        hot_top_k: ホット数字とみなす上位候補数。

    Returns:
        スコア降順の候補リスト（4 桁文字列）。
    """
    if df is None or df.empty:
        return []

    recent = df.tail(recent_window)
    digit_counter: Counter = Counter()
    for _, row in recent.iterrows():
        for col in ("d1", "d2", "d3", "d4"):
            digit_counter[int(row[col])] += 1

    if not digit_counter:
        return []

    # ホット数字とコールド数字のリスト（コールドも組み合わせ用に保持）
    sorted_by_freq = digit_counter.most_common()
    hot_digits = [d for d, _ in sorted_by_freq[:hot_top_k]]
    all_digits = [d for d, _ in sorted_by_freq] + [
        d for d in range(10) if d not in dict(sorted_by_freq)
    ]

    latest = (
        "".join(str(int(recent.iloc[-1][c])) for c in ("d1", "d2", "d3", "d4"))
        if not recent.empty
        else ""
    )

    from itertools import permutations

    scored: Dict[str, float] = {}

    # ターゲット A: AABC（最頻出 ~43%）— ホット数字 1 つを 2 回 + 異なる 2 数字
    for hot in hot_digits:
        for d1 in all_digits:
            if d1 == hot:
                continue
            for d2 in all_digits:
                if d2 == hot or d2 == d1:
                    continue
                base = [hot, hot, d1, d2]
                seen_local = set()
                for perm in permutations(base):
                    num_str = "".join(str(d) for d in perm)
                    if num_str in seen_local or num_str == latest:
                        continue
                    seen_local.add(num_str)

                    box_type = _box_type_of(num_str)
                    prior = BOX_TYPE_PRIOR.get(box_type, 0.001)
                    freq_score = (
                        digit_counter.get(hot, 0) * 2.0
                        + digit_counter.get(d1, 0)
                        + digit_counter.get(d2, 0)
                    )
                    score = freq_score * prior * 100.0
                    if num_str not in scored or scored[num_str] < score:
                        scored[num_str] = score

    # ターゲット B: AABB（~3%）— 2 つの異なるホット数字をそれぞれ 2 回
    for i, h1 in enumerate(hot_digits):
        for h2 in hot_digits[i + 1 :]:
            base = [h1, h1, h2, h2]
            seen_local = set()
            for perm in permutations(base):
                num_str = "".join(str(d) for d in perm)
                if num_str in seen_local or num_str == latest:
                    continue
                seen_local.add(num_str)
                prior = BOX_TYPE_PRIOR["AABB"]
                freq_score = (digit_counter.get(h1, 0) + digit_counter.get(h2, 0)) * 1.5
                score = freq_score * prior * 100.0
                if num_str not in scored or scored[num_str] < score:
                    scored[num_str] = score

    sorted_preds = sorted(scored.items(), key=lambda x: -x[1])
    return [num for num, _ in sorted_preds[:limit]]


# ---------------------------------------------------------------------------
# 🅱 繰り返し率に応じた後処理ボーナス
# ---------------------------------------------------------------------------

# 4 桁の数字（10000 通り）のうち、少なくとも 2 桁が同じ数字となる割合は
# 1 - (10*9*8*7)/10000 = 0.496（≒49.6%）。これをベースラインとして使う。
REPETITION_BASELINE: float = 0.496


def apply_repetition_bonus(
    df: pd.DataFrame,
    history_df: pd.DataFrame,
    *,
    recent_window: int = 30,
    max_bonus: float = 0.25,
    max_penalty: float = 0.10,
) -> pd.DataFrame:
    """直近の繰り返し率に応じて、繰り返しを含む候補のスコアを補正する。

    直近 ``recent_window`` 回における「同じ数字が 2 回以上含まれる抽選」の割合を計算し、
    ベースライン (49.6%) との差分に基づいて：

    - 直近の繰り返し率が高い → 繰り返し候補を最大 ``max_bonus`` だけ加点
    - 直近の繰り返し率が低い → 繰り返し候補を最大 ``max_penalty`` だけ減点

    Args:
        df: 候補 DataFrame（`prediction`, `score` 列）。
        history_df: 過去データ（`d1`〜`d4`）。
        recent_window: 集計する直近回数。
        max_bonus: 加点側の最大倍率（例: 0.25 → ×1.25）。
        max_penalty: 減点側の最大倍率（例: 0.10 → ×0.90）。

    Returns:
        補正＆再ソート済み DataFrame（コピー）。
    """
    if df is None or df.empty or history_df is None or history_df.empty:
        return df

    recent = history_df.tail(recent_window)
    repeat_count = 0
    total = 0
    for _, row in recent.iterrows():
        digits = [int(row[c]) for c in ("d1", "d2", "d3", "d4")]
        total += 1
        if len(set(digits)) < 4:
            repeat_count += 1
    if total == 0:
        return df

    recent_rate = repeat_count / total
    delta = recent_rate - REPETITION_BASELINE  # +で繰返し多め、-で少なめ

    out = df.copy()
    factors = []
    for pred in out["prediction"].astype(str).values:
        if not pred.isdigit() or len(pred) != 4:
            factors.append(1.0)
            continue
        repeats = _max_repeat_count(pred) - 1  # 0:全部ユニーク、1:ペアあり、2:三つ揃い、3:ゾロ目
        if repeats <= 0:
            # ユニーク候補は逆方向の補正（delta>0なら減点、delta<0なら加点）
            factor = 1.0 - delta * max_penalty * 2.0
            factor = max(min(factor, 1.0 + max_penalty), 1.0 - max_penalty)
            factors.append(factor)
            continue
        # 繰り返し度合いに応じてスケール (1〜3)
        scale = min(repeats / 3.0, 1.0)
        if delta >= 0:
            factor = 1.0 + delta * 2.0 * max_bonus * scale  # delta=最大0.5 → 最大 max_bonus
            factor = min(factor, 1.0 + max_bonus)
        else:
            factor = 1.0 + delta * 2.0 * max_penalty * scale
            factor = max(factor, 1.0 - max_penalty)
        factors.append(factor)

    out["score"] = out["score"].astype(np.float64) * np.asarray(factors, dtype=np.float64)
    out = out.sort_values(by="score", ascending=False).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# 🅳 アンサンブル多様性ボーナス
# ---------------------------------------------------------------------------

def _build_origin_index(
    predictions_by_model: Dict[str, List[str]],
    top_n_per_model: int = 30,
) -> Dict[str, set]:
    """予測候補ごとに、それを top_n に含めていたモデル名集合を返す。"""
    origin: Dict[str, set] = {}
    for model, preds in predictions_by_model.items():
        if not preds:
            continue
        for pred in list(preds)[:top_n_per_model]:
            origin.setdefault(str(pred), set()).add(model)
    return origin


def apply_category_diversity_bonus(
    df: pd.DataFrame,
    predictions_by_model: Dict[str, List[str]],
    *,
    top_k: int = 20,
    top_n_per_model: int = 30,
    bonus_per_new_category: float = 0.08,
    max_bonus: float = 0.30,
    category_map: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """上位 K 件のモデルカテゴリ多様性を強化する後処理。

    ある手法（例: ``box_model``）に偏った Top20 を、他カテゴリ（例: ``transition``）の
    候補が押しのけられないようにスコア面で補助する。

    アルゴリズム:
        1. 各候補について「どのモデルの top_n_per_model に含まれていたか」を集計。
        2. それを ``category_map`` でカテゴリ集合へ変換。
        3. スコア降順にスキャンし、すでに上位に出現したカテゴリと比較して
           「新カテゴリを連れてくる」候補に対して ``bonus_per_new_category`` を乗算。
        4. ボーナスは累積するが ``max_bonus`` で頭打ち。

    Args:
        df: 集計後の候補 DataFrame。
        predictions_by_model: 各モデルの予測リスト。
        top_k: 多様性を確保したい上位件数。
        top_n_per_model: 各モデルの何位までを「貢献」とみなすか。
        bonus_per_new_category: 新カテゴリ 1 つにつき与える乗算ボーナス。
        max_bonus: ボーナスの上限（例: 0.30 → ×1.30）。
        category_map: モデル名→カテゴリ名のマップ（None なら METHOD_CATEGORIES）。

    Returns:
        ボーナス適用＆再ソート後の DataFrame（コピー）。
    """
    if df is None or df.empty or not predictions_by_model:
        return df

    cat_map = category_map or METHOD_CATEGORIES
    origin = _build_origin_index(predictions_by_model, top_n_per_model=top_n_per_model)

    out = df.copy()
    seen_categories: set = set()
    factors = np.ones(len(out), dtype=np.float64)

    for idx in range(min(top_k, len(out))):
        pred = str(out.iloc[idx]["prediction"])
        models = origin.get(pred, set())
        cats = {cat_map.get(m, "other") for m in models}
        new_cats = cats - seen_categories

        if new_cats:
            bonus = min(bonus_per_new_category * len(new_cats), max_bonus)
            factors[idx] = 1.0 + bonus
            seen_categories.update(cats)

    out["score"] = out["score"].astype(np.float64) * factors
    out = out.sort_values(by="score", ascending=False).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# サマリ表示用ユーティリティ
# ---------------------------------------------------------------------------

def summarize_category_distribution(
    df: pd.DataFrame,
    predictions_by_model: Dict[str, List[str]],
    *,
    top_k: int = 20,
    top_n_per_model: int = 30,
    category_map: Optional[Dict[str, str]] = None,
) -> Dict[str, int]:
    """Top-K 候補のカテゴリ分布を辞書で返す（デバッグ・レポート用）。"""
    if df is None or df.empty:
        return {}
    cat_map = category_map or METHOD_CATEGORIES
    origin = _build_origin_index(predictions_by_model, top_n_per_model=top_n_per_model)
    counter: Counter = Counter()
    for idx in range(min(top_k, len(df))):
        pred = str(df.iloc[idx]["prediction"])
        cats = {cat_map.get(m, "other") for m in origin.get(pred, set())}
        for c in cats:
            counter[c] += 1
    return dict(counter)


__all__ = [
    "METHOD_CATEGORIES",
    "REPETITION_BASELINE",
    "apply_digit_position_boost",
    "predict_from_repetition_pattern_n4",
    "apply_repetition_bonus",
    "apply_category_diversity_bonus",
    "summarize_category_distribution",
]

"""
同一ボックス（4桁の multiset）からストレート1本を選ぶユーティリティ。

ボックス確定後に random.shuffle だけだと並びがランダムになり、モデル別の
「同じ数字の組み合わせ」をアンサンブルが束ねるときにストレートのばらつきが増える。
直近の抽選データについて、各桁位置にどの数字が何回出たかを数え、
その合計が最大になる順列を選ぶ（同点は辞書順最小で固定）。
未来の当選番号は参照しない。
"""

from __future__ import annotations

from collections import Counter
from itertools import permutations
from typing import Any

import pandas as pd

_DRAW_COLS = ("d1", "d2", "d3", "d4")


def _position_digit_counts(df_recent: pd.DataFrame) -> list[Counter[str]] | None:
    if df_recent is None or len(df_recent) == 0:
        return None
    for c in _DRAW_COLS:
        if c not in df_recent.columns:
            return None
    out: list[Counter[str]] = []
    for c in _DRAW_COLS:
        cnt: Counter[str] = Counter()
        for v in df_recent[c].values:
            cnt[str(int(v))] += 1
        out.append(cnt)
    return out


def best_straight_for_sorted_box(
    box_sorted: str,
    latest_number: str,
    df_recent: pd.DataFrame,
) -> str | None:
    """
    ソート済み4桁（例 '1234'）の全順列のうち、直近ウィンドウでの桁位置別出現回数の
    合計が最大のストレートを返す。latest_number と同じ並びは除外（前回と重複しないため）。
    候補が無ければ None。
    """
    if not box_sorted or len(box_sorted) != 4 or not box_sorted.isdigit():
        return None
    pos_counts = _position_digit_counts(df_recent)
    if pos_counts is None:
        return None

    best_score = float("-inf")
    best_cand: str | None = None
    for perm in set(permutations(list(box_sorted))):
        cand = "".join(perm)
        if cand == latest_number:
            continue
        sc = sum(pos_counts[i].get(cand[i], 0) for i in range(4))
        if sc > best_score:
            best_score = sc
            best_cand = cand
        elif sc == best_score and best_cand is not None and cand < best_cand:
            best_cand = cand
    return best_cand


def refine_top_predictions_numbers(
    predictions: list[dict[str, Any]],
    df_all: pd.DataFrame,
    recent_n: int = 50,
) -> list[dict[str, Any]]:
    """
    予測リストの各 number を、同一ボックス内で best_straight_for_sorted_box に従って置換。
    df_all の最終行は「集計時点の直近当選」として latest に使い、桁頻度は tail(recent_n) のみ。
    """
    if not predictions or df_all is None or len(df_all) < 1:
        return predictions
    for c in _DRAW_COLS:
        if c not in df_all.columns:
            return predictions

    latest_number = "".join(map(str, df_all.iloc[-1][list(_DRAW_COLS)].values))
    recent = df_all.tail(max(1, recent_n))

    out: list[dict[str, Any]] = []
    for p in predictions:
        raw = p.get("number", "")
        num = str(raw).strip()
        if len(num) != 4 or not num.isdigit():
            out.append(p)
            continue
        box = "".join(sorted(num))
        better = best_straight_for_sorted_box(box, latest_number, recent)
        if better is None:
            out.append(p)
            continue
        q = dict(p)
        q["number"] = better
        out.append(q)
    return out

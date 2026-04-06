"""
複数回分まとめて、当選番号の「ボックス一致が予測リストの何位か」を集計する。

- アンサンブル本体: predictions/daily/numbers4_{回}.json の最新スナップショット
- 手法別: predictions/daily/methods/{手法}/numbers4_{回}.json（evaluate_methods と同じ読み方）

注意:
  JSON に保存されている上位件数（例: ensemble は often top20）より下の順位は
  評価できない。その場合は box_rank が付かず「圏外」扱いになる。

使い方:
  python numbers4/report_box_rank_aggregates.py --last-n 20
  python numbers4/report_box_rank_aggregates.py --draw-from 6930 --draw-to 6950
  python numbers4/report_box_rank_aggregates.py --last-n 30 --top-k 100
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection  # noqa: E402
from numbers4.evaluate_methods import (  # noqa: E402
    ALL_METHODS,
    evaluate_method,
    get_actual_result,
    load_method_predictions,
)

PREDICTIONS_DAILY = os.path.join(project_root, "predictions", "daily")


def load_ensemble_predictions_last_run(draw_number: int) -> List[str]:
    """メイン JSON の predictions 配列のうち、最後のエントリの top_predictions 順に番号を返す。"""
    path = os.path.join(PREDICTIONS_DAILY, f"numbers4_{draw_number}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    blocks = data.get("predictions") or []
    if not blocks:
        return []
    last = blocks[-1]
    seen = set()
    out: List[str] = []
    for item in last.get("top_predictions") or []:
        raw = str(item.get("number", "")).strip()
        if not raw.isdigit():
            continue
        num = raw.zfill(4)
        if len(num) != 4:
            continue
        if num in seen:
            continue
        seen.add(num)
        out.append(num)
    return out


def fetch_draw_numbers_desc(limit: int) -> List[int]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT draw_number FROM numbers4_draws
            WHERE numbers IS NOT NULL AND TRIM(numbers) != ''
            ORDER BY draw_number DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [int(r[0]) for r in cur.fetchall()]
    finally:
        conn.close()


def fetch_draw_range(draw_from: int, draw_to: int) -> List[int]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT draw_number FROM numbers4_draws
            WHERE draw_number BETWEEN ? AND ?
              AND numbers IS NOT NULL AND TRIM(numbers) != ''
            ORDER BY draw_number ASC
            """,
            (draw_from, draw_to),
        )
        return [int(r[0]) for r in cur.fetchall()]
    finally:
        conn.close()


def box_rank_or_none(evaluation: Dict) -> Optional[int]:
    r = evaluation.get("box_rank")
    return int(r) if r is not None else None


def run_aggregate(
    draws: List[int],
    top_k: int,
    thresholds: Tuple[int, ...],
) -> None:
    # method -> list of (draw, box_rank or None)
    per_draw_method: Dict[str, List[Tuple[int, Optional[int]]]] = defaultdict(list)
    ensemble_rows: List[Tuple[int, Optional[int]]] = []

    for draw in draws:
        actual = get_actual_result(draw)
        if not actual:
            continue

        ens = load_ensemble_predictions_last_run(draw)
        if ens:
            ev = evaluate_method(ens, actual, top_k=top_k)
            ensemble_rows.append((draw, box_rank_or_none(ev)))
        else:
            ensemble_rows.append((draw, None))

        for method in ALL_METHODS:
            preds = load_method_predictions(draw, method)
            if not preds:
                per_draw_method[method].append((draw, None))
                continue
            ev = evaluate_method(preds, actual, top_k=top_k)
            per_draw_method[method].append((draw, box_rank_or_none(ev)))

    def summarize(
        label: str, rows: List[Tuple[int, Optional[int]]]
    ) -> None:
        n = len(rows)
        if n == 0:
            print(f"  {label}: 対象回なし")
            return
        misses = sum(1 for _, r in rows if r is None)
        line_parts = [f"n={n}", f"圏外/不一致={misses}"]
        for t in thresholds:
            hit = sum(1 for _, r in rows if r is not None and r <= t)
            pct = 100.0 * hit / n if n else 0.0
            line_parts.append(f"box≤{t}: {hit} ({pct:.1f}%)")
        print(f"  {label}: " + " | ".join(line_parts))

    print("=" * 72)
    print("ボックス一致ランク集計（保存済み予測リストの範囲内）")
    print(f"対象回: {len(draws)} 回（評価 top_k={top_k}）")
    if draws:
        print(f"  回号: {draws[0]} … {draws[-1]}" if len(draws) > 1 else f"  回号: {draws[0]}")
    print("=" * 72)
    print()
    summarize("ensemble (numbers4_*.json 最新スナップショット)", ensemble_rows)
    print()
    print("【手法別】")
    for method in ALL_METHODS:
        summarize(method, per_draw_method[method])


def main() -> None:
    parser = argparse.ArgumentParser(description="ボックス順位の回跨ぎ集計")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--last-n",
        type=int,
        metavar="N",
        help="DB上で新しい方から N 回を対象にする",
    )
    g.add_argument(
        "--draw-range",
        nargs=2,
        type=int,
        metavar=("FROM", "TO"),
        help="抽選回号の範囲（両端含む）",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=100,
        help="各リストの先頭から何件までボックス一致を探すか（デフォルト: 100）",
    )
    parser.add_argument(
        "--thresholds",
        type=str,
        default="1,5,10,20,50,100",
        help="集計する順位しきい値（カンマ区切り）例: 1,5,10,20",
    )
    args = parser.parse_args()

    try:
        thresholds = tuple(int(x.strip()) for x in args.thresholds.split(",") if x.strip())
    except ValueError:
        print("❌ --thresholds の形式が不正です", file=sys.stderr)
        sys.exit(1)

    if args.last_n is not None:
        draws = fetch_draw_numbers_desc(args.last_n)
        draws.reverse()  # 古い→新しいで表示しやすく
    else:
        df, dt = args.draw_range
        if df > dt:
            print("❌ --draw-range は FROM <= TO で指定してください", file=sys.stderr)
            sys.exit(1)
        draws = fetch_draw_range(df, dt)

    if not draws:
        print("❌ 対象となる抽選データがありません（DB・回号を確認してください）")
        sys.exit(1)

    run_aggregate(draws, top_k=args.top_k, thresholds=thresholds)


if __name__ == "__main__":
    main()

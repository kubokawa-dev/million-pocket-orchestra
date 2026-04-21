"""
バックテストベースの重み最適化 (v16.0)

直近N回分のバックテストを実行し、各モデルの実績に基づいて
最適な重みを算出する。1回の結果に振り回されない安定した重み。

使い方:
  python numbers4/backtest_weight_optimizer.py --last-n 50
  python numbers4/backtest_weight_optimizer.py --last-n 100 --verbose
  python numbers4/backtest_weight_optimizer.py --last-n 50 --apply  # 重みを実際に更新
"""

import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection
from numbers4.evaluate_methods import (
    ALL_METHODS,
    load_method_predictions,
    evaluate_method,
    load_method_weights,
    save_method_weights,
    get_default_method_weights,
    WEIGHTS_FILE,
)


def get_available_draw_numbers(last_n: int = 50) -> List[int]:
    """評価可能な直近N回の抽選回号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT draw_number FROM numbers4_draws
            ORDER BY draw_number DESC
            LIMIT ?
        """, (last_n,))
        rows = cur.fetchall()
        return sorted([r[0] for r in rows])
    finally:
        conn.close()


def get_actual_result(draw_number: int) -> Optional[str]:
    """当選番号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT numbers FROM numbers4_draws
            WHERE draw_number = ?
        """, (draw_number,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _compute_time_decay_weights(
    draw_numbers: List[int],
    half_life: Optional[float],
) -> Dict[int, float]:
    """各 draw_number に対する時間減衰重みを計算する（v17.0 🅲）。

    指数減衰: w_i = 0.5 ** ((latest - draw_i) / half_life)

    half_life が None または 0 以下なら全て 1.0（従来通りの一様評価）。
    """
    if not draw_numbers:
        return {}
    if not half_life or half_life <= 0:
        return {dn: 1.0 for dn in draw_numbers}
    latest = max(draw_numbers)
    return {dn: float(0.5 ** ((latest - dn) / half_life)) for dn in draw_numbers}


def run_backtest(
    draw_numbers: List[int],
    top_k: int = 100,
    verbose: bool = False,
    *,
    half_life: Optional[float] = None,
) -> Dict[str, Dict]:
    """
    直近N回分のバックテストを実行し、各モデルの性能を測定。

    v17.0 🅲: ``half_life`` を指定すると、各回号のスコアに指数減衰重みを掛けて
    集計する（直近寄りの局所最適化モード）。

    Returns:
        {method: {
            'box_hits': float,         # ボックス的中回数（重み加算）
            'straight_hits': float,    # ストレート的中回数（重み加算）
            'digit3_hits': float,      # 3桁一致回数（重み加算）
            'digit2_hits': float,      # 2桁一致回数（重み加算）
            'avg_score': float,        # 重み付き平均スコア
            'total_draws': int,        # 評価した回数（生）
            'effective_n': float,      # 重み合計（実効サンプル数）
            'box_hit_rate': float,     # ボックス的中率（重み付き）
            'scores': list[float],     # 全スコアの履歴
            'score_weights': list,     # 各スコアに対応する時間減衰重み
            'recent_trend': float,     # 直近10回のスコアトレンド
        }}
    """
    weights_by_draw = _compute_time_decay_weights(draw_numbers, half_life)

    results: Dict[str, Dict] = {}
    for method in ALL_METHODS:
        results[method] = {
            'box_hits': 0.0,
            'straight_hits': 0.0,
            'digit3_hits': 0.0,
            'digit2_hits': 0.0,
            'total_draws': 0,
            'effective_n': 0.0,
            'scores': [],
            'score_weights': [],
            'box_ranks': [],
        }

    for draw_num in draw_numbers:
        actual = get_actual_result(draw_num)
        if not actual:
            continue
        decay_w = weights_by_draw.get(draw_num, 1.0)

        for method in ALL_METHODS:
            predictions = load_method_predictions(draw_num, method)
            if not predictions:
                continue

            evaluation = evaluate_method(predictions, actual, top_k)
            r = results[method]
            r['total_draws'] += 1
            r['effective_n'] += decay_w
            r['scores'].append(evaluation['score'])
            r['score_weights'].append(decay_w)

            if evaluation['straight_rank']:
                r['straight_hits'] += decay_w
            if evaluation['box_rank']:
                r['box_hits'] += decay_w
                r['box_ranks'].append(evaluation['box_rank'])
            if evaluation['best_digit_hits'] >= 3 or evaluation['best_position_hits'] >= 3:
                r['digit3_hits'] += decay_w
            elif evaluation['best_digit_hits'] >= 2 or evaluation['best_position_hits'] >= 2:
                r['digit2_hits'] += decay_w

        if verbose:
            tag = f"(decay={decay_w:.3f})" if half_life else ""
            print(f"  回{draw_num} ({actual}) 完了 {tag}")

    # 集計
    for method, r in results.items():
        n = r['total_draws']
        eff = r['effective_n']
        if n > 0 and eff > 0:
            scores = np.asarray(r['scores'], dtype=np.float64)
            sw = np.asarray(r['score_weights'], dtype=np.float64)
            r['avg_score'] = float(np.average(scores, weights=sw))
            r['box_hit_rate'] = r['box_hits'] / eff
            r['straight_hit_rate'] = r['straight_hits'] / eff
            r['digit3_hit_rate'] = r['digit3_hits'] / eff
            # 直近10回のトレンド（重みは無視して生のトレンドを見る）
            recent = r['scores'][-10:] if len(r['scores']) >= 10 else r['scores']
            if len(recent) >= 2:
                first_half = float(np.mean(recent[:len(recent)//2]))
                second_half = float(np.mean(recent[len(recent)//2:]))
                r['recent_trend'] = second_half - first_half
            else:
                r['recent_trend'] = 0.0
            r['avg_box_rank'] = float(np.mean(r['box_ranks'])) if r['box_ranks'] else None
        else:
            r['avg_score'] = 0.0
            r['box_hit_rate'] = 0.0
            r['straight_hit_rate'] = 0.0
            r['digit3_hit_rate'] = 0.0
            r['recent_trend'] = 0.0
            r['avg_box_rank'] = None

    return results


def optimize_weights(
    backtest_results: Dict[str, Dict],
    current_weights: Dict[str, float],
) -> Dict[str, float]:
    """
    バックテスト結果に基づいて最適な重みを算出。

    重みの計算方法:
    1. ボックス的中率 × 40  (最重要: 当たったかどうか)
    2. 平均スコア × 0.3    (全体的な精度)
    3. 3桁一致率 × 15      (惜しい予測の能力)
    4. トレンドボーナス     (最近調子が良いモデルを優遇)
    5. 最低保証 1.0        (完全排除はしない)
    """
    new_weights = {}

    # まず全モデルの性能指標を計算
    for method, r in backtest_results.items():
        if r['total_draws'] == 0:
            # データなしの場合はデフォルト重みの半分
            default_w = get_default_method_weights().get(method, 10.0)
            new_weights[method] = default_w * 0.5
            continue

        # 複合スコア
        box_score = r['box_hit_rate'] * 40.0
        avg_score_component = r['avg_score'] * 0.3
        digit3_score = r['digit3_hit_rate'] * 15.0
        straight_bonus = r['straight_hit_rate'] * 60.0  # ストレート的中は超高評価

        # トレンドボーナス（直近が好調なら+20%、不調なら-10%）
        trend_factor = 1.0
        if r['recent_trend'] > 2.0:
            trend_factor = 1.2
        elif r['recent_trend'] > 0:
            trend_factor = 1.1
        elif r['recent_trend'] < -2.0:
            trend_factor = 0.9

        raw_weight = (box_score + avg_score_component + digit3_score + straight_bonus) * trend_factor

        # 最低保証
        new_weights[method] = max(1.0, raw_weight)

    # 正規化: 合計を現在の重みの合計に合わせる
    total_current = sum(current_weights.get(m, 10.0) for m in ALL_METHODS)
    total_new = sum(new_weights.values())
    if total_new > 0:
        scale = total_current / total_new
        new_weights = {k: max(1.0, min(60.0, v * scale)) for k, v in new_weights.items()}

    return new_weights


def print_backtest_report(
    backtest_results: Dict[str, Dict],
    current_weights: Dict[str, float],
    optimized_weights: Dict[str, float],
):
    """バックテスト結果のレポートを表示"""
    print("\n" + "=" * 80)
    print("📊 バックテスト結果レポート")
    print("=" * 80)

    # ソート: ボックス的中率 > 平均スコア順
    sorted_methods = sorted(
        backtest_results.items(),
        key=lambda x: (x[1]['box_hit_rate'], x[1]['avg_score']),
        reverse=True,
    )

    print(f"\n{'手法':<25s} {'回数':>4s} {'BOX的中':>7s} {'ST的中':>6s} {'3桁率':>6s} {'平均点':>6s} {'トレンド':>8s} {'現重み':>6s} {'新重み':>6s} {'変化':>6s}")
    print("-" * 100)

    for method, r in sorted_methods:
        n = r['total_draws']
        if n == 0:
            print(f"  {method:<23s} {'---':>4s}")
            continue

        box_rate = f"{r['box_hit_rate']*100:.1f}%"
        st_rate = f"{r['straight_hit_rate']*100:.1f}%"
        d3_rate = f"{r['digit3_hit_rate']*100:.1f}%"
        avg_s = f"{r['avg_score']:.1f}"
        trend = f"{r['recent_trend']:+.1f}"
        curr_w = f"{current_weights.get(method, 0):.1f}"
        new_w = f"{optimized_weights.get(method, 0):.1f}"
        diff = optimized_weights.get(method, 0) - current_weights.get(method, 0)
        diff_str = f"{diff:+.1f}"

        # ボックス的中があるモデルにマーク
        marker = "🏆" if r['box_hits'] > 0 else "  "
        print(f"{marker}{method:<23s} {n:>4d} {box_rate:>7s} {st_rate:>6s} {d3_rate:>6s} {avg_s:>6s} {trend:>8s} {curr_w:>6s} {new_w:>6s} {diff_str:>6s}")

    # サマリー
    total_box = sum(r['box_hits'] for r in backtest_results.values())
    total_draws = max(r['total_draws'] for r in backtest_results.values()) if backtest_results else 0
    contributing = sum(1 for r in backtest_results.values() if r['box_hits'] > 0)
    total_methods = len([r for r in backtest_results.values() if r['total_draws'] > 0])

    print(f"\n--- サマリー ---")
    print(f"評価回数: {total_draws}回")
    print(f"BOX的中に貢献したモデル: {contributing}/{total_methods}")
    print(f"全モデル合計BOX的中: {total_box}回")

    # 貢献しないモデルの警告
    no_contrib = [m for m, r in backtest_results.items()
                  if r['total_draws'] > 10 and r['box_hits'] == 0 and r['digit3_hit_rate'] < 0.05]
    if no_contrib:
        print(f"\n⚠️  ほぼ貢献していないモデル: {', '.join(no_contrib)}")
        print("   → これらのモデルの重みは自動的に下げられます")


def main():
    parser = argparse.ArgumentParser(
        description='バックテストベースの重み最適化'
    )
    parser.add_argument(
        '--last-n', type=int, default=50,
        help='直近N回分をバックテスト（デフォルト: 50）'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='詳細を表示'
    )
    parser.add_argument(
        '--apply', action='store_true',
        help='最適化された重みを実際に適用する'
    )
    parser.add_argument(
        '--top-k', type=int, default=100,
        help='評価対象のTop-K（デフォルト: 100）'
    )
    parser.add_argument(
        '--half-life', type=float, default=None,
        help='v17.0 🅲: 時間減衰の半減期（回号単位）。指定すると直近を強く重み付け（推奨: 15）'
    )
    parser.add_argument(
        '--focus-recent', type=int, default=None,
        help='v17.0 🅲: 直近N回のみで局所最適化（--last-nより細かく絞り込みたい場合）'
    )

    args = parser.parse_args()

    print(f"🔬 バックテスト重み最適化 (直近{args.last_n}回)")
    print("=" * 60)

    # 利用可能な回号を取得
    draw_numbers = get_available_draw_numbers(args.last_n)

    # v17.0 🅲: focus-recent でさらに局所化
    if args.focus_recent and args.focus_recent < len(draw_numbers):
        draw_numbers = draw_numbers[-args.focus_recent:]
        print(f"🎯 局所最適化モード: 直近{args.focus_recent}回に絞り込み")

    print(f"📅 対象: 第{draw_numbers[0]}回 〜 第{draw_numbers[-1]}回 ({len(draw_numbers)}回)")
    if args.half_life:
        print(f"⏰ 時間減衰モード: 半減期 = {args.half_life}回（直近重視）")

    # バックテスト実行
    print("\n🔄 バックテスト実行中...")
    results = run_backtest(
        draw_numbers,
        top_k=args.top_k,
        verbose=args.verbose,
        half_life=args.half_life,
    )

    # 現在の重みを読み込み
    current_weights = load_method_weights()

    # 最適化
    optimized = optimize_weights(results, current_weights)

    # レポート表示
    print_backtest_report(results, current_weights, optimized)

    if args.apply:
        print("\n✅ 最適化された重みを適用します...")
        metadata = {
            'optimizer': 'backtest_weight_optimizer',
            'backtest_draws': len(draw_numbers),
            'draw_range': f"{draw_numbers[0]}-{draw_numbers[-1]}",
            'half_life': args.half_life,
            'focus_recent': args.focus_recent,
        }
        save_method_weights(optimized, metadata)
        print(f"✅ {WEIGHTS_FILE} を更新しました")
    else:
        print("\n💡 --apply を付けると重みを実際に更新します")


if __name__ == '__main__':
    main()

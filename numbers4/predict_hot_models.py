"""
直近N回で成績が良かった「キテる」モデル（Hot Model）を分析するスクリプト
"""

import os
import sys
import argparse
from typing import Dict, List, Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection
from numbers4.evaluate_methods import (
    ALL_METHODS,
    get_actual_result,
    load_method_predictions,
    evaluate_method
)

def analyze_hot_models(target_draw: int, lookback: int = 5, top_k: int = 100, quiet: bool = False) -> Tuple[List[Tuple[str, float]], List[Dict]]:
    """
    指定した回の直前N回分の成績を分析し、Hot Modelのスコアと各回の最強モデルの履歴（flow）を返す
    """
    method_scores = {method: 0.0 for method in ALL_METHODS}
    flow = []
    
    start_draw = target_draw - lookback
    end_draw = target_draw - 1
    
    if not quiet:
        print(f"🔍 第{start_draw}回 〜 第{end_draw}回 (直近{lookback}回) のトレンドを分析中...✨")
    
    for draw in range(start_draw, end_draw + 1):
        actual = get_actual_result(draw)
        if not actual:
            if not quiet:
                print(f"⚠️ 第{draw}回の結果が見つからないからスキップするね！")
            continue
            
        best_draw_model = None
        best_draw_score = -1
            
        for method in ALL_METHODS:
            predictions = load_method_predictions(draw, method)
            if not predictions:
                continue
                
            eval_result = evaluate_method(predictions, actual, top_k=top_k)
            score = eval_result['score']
            method_scores[method] += score
            
            if score > best_draw_score:
                best_draw_score = score
                best_draw_model = method
                
        if best_draw_model and best_draw_score > 0:
            flow.append({"draw": draw, "model": best_draw_model, "score": best_draw_score})
            
    # スコアが高い順にソート
    sorted_methods = sorted(method_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_methods, flow

def run_backtest(latest_draw: int, lookback: int = 5, backtest_count: int = 50, top_k: int = 100):
    """
    過去N回分のデータで「Hot Model」戦略が本当に有効だったかをバックテストするよ！
    """
    print(f"\n📊 過去{backtest_count}回分で「Hot Model戦略」のバックテストを開始するよー！✨")
    print("=" * 60)
    
    hot_model_total_score = 0.0
    average_model_total_score = 0.0
    hits = {'straight': 0, 'box': 0, 'pos3': 0, 'digit3': 0}
    
    start_test_draw = latest_draw - backtest_count + 1
    
    for draw in range(start_test_draw, latest_draw + 1):
        actual = get_actual_result(draw)
        if not actual:
            continue
            
        # その回の直前lookback回で一番キテるモデルを探す
        hot_models, _ = analyze_hot_models(draw, lookback, top_k, quiet=True)
        if not hot_models or hot_models[0][1] == 0:
            continue
            
        best_method = hot_models[0][0]
        
        # その回の全モデルの平均スコアを計算
        draw_total_score = 0.0
        valid_methods = 0
        hot_model_score = 0.0
        hot_eval = None
        
        for method in ALL_METHODS:
            preds = load_method_predictions(draw, method)
            if not preds:
                continue
            
            eval_res = evaluate_method(preds, actual, top_k=top_k)
            score = eval_res['score']
            draw_total_score += score
            valid_methods += 1
            
            if method == best_method:
                hot_model_score = score
                hot_eval = eval_res
                
        avg_score = draw_total_score / valid_methods if valid_methods > 0 else 0.0
        
        hot_model_total_score += hot_model_score
        average_model_total_score += avg_score
        
        # ヒット記録
        if hot_eval:
            if hot_eval['straight_rank']: hits['straight'] += 1
            elif hot_eval['box_rank']: hits['box'] += 1
            elif hot_eval['best_position_hits'] >= 3: hits['pos3'] += 1
            elif hot_eval['best_digit_hits'] >= 3: hits['digit3'] += 1
            
        # 進行状況をちょっとだけ表示
        if draw % 10 == 0 or draw == latest_draw:
            print(f"  第{draw}回: Hot Model【{best_method}】のスコア: {hot_model_score:.1f} (全体平均: {avg_score:.1f})")

    print("=" * 60)
    print("🎉 バックテスト結果発表〜！！ 🎉")
    print(f"🎯 対象回数: {backtest_count}回")
    print(f"🔥 Hot Modelの平均スコア: {hot_model_total_score / backtest_count:.1f}")
    print(f"📊 全モデルの平均スコア: {average_model_total_score / backtest_count:.1f}")
    
    diff = (hot_model_total_score / backtest_count) - (average_model_total_score / backtest_count)
    if diff > 0:
        print(f"💖 Hot Model戦略の勝ち！平均より {diff:.1f} ポイント高いよ！天才！✨")
    else:
        print(f"🥺 うーん、平均より {-diff:.1f} ポイント低かった...戦略の見直しが必要かも💦")
        
    print("\n🎯 Hot Modelの的中実績:")
    print(f"  - ストレート的中: {hits['straight']}回")
    print(f"  - ボックス的中: {hits['box']}回")
    print(f"  - 3桁位置一致: {hits['pos3']}回")
    print(f"  - 3桁数字一致: {hits['digit3']}回")


def main():
    parser = argparse.ArgumentParser(description="直近の成績からHot Modelを分析するよ！💕")
    parser.add_argument('--target', type=int, required=True, help="予測したい回（この回の直前を分析するよ！）")
    parser.add_argument('--lookback', type=int, default=5, help="何回分さかのぼるか（デフォルト: 5）")
    parser.add_argument('--top-k', type=int, default=100, help="評価対象のTop-K（デフォルト: 100）")
    parser.add_argument('--backtest', type=int, help="過去N回分でバックテストを実行するよ！")
    parser.add_argument('--json', action='store_true', help="JSON形式で出力するよ！")
    
    args = parser.parse_args()
    
    if args.backtest:
        run_backtest(args.target, args.lookback, args.backtest, args.top_k)
        return
    else:
        hot_models, flow = analyze_hot_models(args.target, args.lookback, args.top_k, quiet=args.json)
        
        if args.json:
            import json
            from collections import Counter
            
            # 遷移分析
            transitions = []
            for i in range(len(flow)-1):
                transitions.append((flow[i]["model"], flow[i+1]["model"]))
                
            last_model = flow[-1]["model"] if flow else None
            next_counts = Counter([next_m for prev_m, next_m in transitions if prev_m == last_model])
            total_transitions = sum(next_counts.values())
            
            next_preds = []
            if total_transitions > 0:
                for m, c in next_counts.most_common(3):
                    next_preds.append({
                        "model": m,
                        "probability": c / total_transitions,
                        "count": c,
                        "total": total_transitions
                    })
                    
            result = {
                "hot_models": [{"model": m, "score": s} for m, s in hot_models],
                "recent_flow": flow[-10:],
                "last_model": last_model,
                "next_model_predictions": next_preds
            }
            print(json.dumps(result))
            return
            
        print("\n🏆 🔥 Hot Model ランキング 🔥 🏆")
        print("=" * 40)
        for i, (method, score) in enumerate(hot_models):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "✨"
            print(f"{medal} {i+1}位: {method:<20} (スコア: {score:.1f})")
        print("=" * 40)
        
        if hot_models[0][1] > 0:
            print(f"\n💖 今一番キテるのは【{hot_models[0][0]}】だよ！次の予測はこれに乗っかろー！🚀")
        else:
            print("\n🥺 うーん、最近どのモデルも調子悪いみたい...頑張って！💦")

if __name__ == '__main__':
    main()

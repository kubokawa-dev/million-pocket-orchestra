import os
import sys
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations

# 親ディレクトリをsys.pathに追加
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from tools.utils import load_all_loto6_draws
from loto6.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model,
    compute_advanced_stats,  # 組み合わせ評価のためにインポート
    score_combination
)
from loto6.learning_logic import learn_model_from_data

def format_predictions(predictions):
    """予測リストを整形して文字列として返す"""
    return [f"[{' '.join(f'{n:02d}' for n in p)}]" for p in predictions]

def run_advanced_ensemble_prediction(num_candidates=20, num_generate=5000, top_n=10):
    """
    高度なアンサンブル予測を実行します。
    1. 各モデルから予測された数字をすべて集め、スコアリングする。
    2. スコアの高い数字をプールとし、重み付けランダムサンプリングで組み合わせを生成する。
    3. 生成された組み合わせを評価し、質の高いものを最終予測とする。
    """
    print("データベースから全抽選データを読み込んでいます...")
    df = load_all_loto6_draws()
    if df.empty:
        print("データがありません。処理を中断します。")
        return

    last_draw_row = df.sort_values(by='date', ascending=False).iloc[0]
    last_draw_numbers = tuple(sorted(last_draw_row[[f'num{i}' for i in range(1, 7)]].astype(int).tolist()))

    print("各モデルで予測を生成しています...")
    basic_preds = predict_from_basic_stats(df, top_n=5)
    advanced_preds = predict_from_advanced_heuristics(df, samples=2000, top_n=5)
    print("- 機械学習モデルを再学習中...")
    ml_model_weights = learn_model_from_data(df)
    ml_preds = predict_with_model(ml_model_weights, top_n=12, exclude_last_draw=last_draw_numbers)
    
    # --- 1. 数字のスコアリング ---
    all_predicted_numbers = [num for pred in (basic_preds + advanced_preds + ml_preds) for num in pred]
    number_scores = Counter(all_predicted_numbers)
    
    print("\n--- 有望な数字トップ10 (スコア順) ---")
    for num, score in number_scores.most_common(10):
        print(f"  数字「{num:02d}」: スコア {score}")

    # --- 2. 組み合わせの再構築と評価 ---
    print(f"\n--- スコア上位の数字から {num_generate} 通りの組み合わせを生成・評価中... ---")
    
    # 候補となる数字プールを作成 (スコア上位 num_candidates 個)
    candidate_pool = [num for num, score in number_scores.most_common(num_candidates)]
    if len(candidate_pool) < 6:
        print("候補となる数字が6個未満のため、処理を中断します。")
        return
        
    # スコアを重みとして使用
    candidate_weights = np.array([number_scores[n] for n in candidate_pool], dtype=float)
    candidate_weights /= candidate_weights.sum()

    # 組み合わせを生成・評価
    generated_combinations = []
    generated_set = set()
    
    # 組み合わせ評価用の統計情報を計算
    adv_stats = compute_advanced_stats(df)

    for _ in range(num_generate):
        # 重み付きランダムサンプリングで6個の数字を選ぶ
        combo = tuple(sorted(np.random.choice(candidate_pool, 6, replace=False, p=candidate_weights)))
        
        if combo in generated_set or combo == last_draw_numbers:
            continue
        
        # 生成した組み合わせの質を評価
        quality_score = score_combination(combo, adv_stats)
        
        # 元の数字スコアの合計も加味する
        original_score_sum = sum(number_scores[n] for n in combo)
        
        # 最終スコア (組み合わせの質 + 元のスコア)
        final_score = quality_score + (original_score_sum / 50.0) # 重み調整
        
        generated_combinations.append((final_score, combo))
        generated_set.add(combo)

    # 最終スコアでソート
    generated_combinations.sort(key=lambda x: x[0], reverse=True)

    # --- 3. 最終結果の生成 ---
    results = []
    if not generated_combinations:
        return results

    for i in range(min(top_n, len(generated_combinations))):
        score, pred = generated_combinations[i]
        pred_str = ' '.join(f"{n:02d}" for n in pred)
        rating = "★" * int(score * 10) + "☆" * (5 - int(score * 10))
        results.append({
            "recommendation": rating,
            "score": f"{score:.4f}",
            "numbers": pred_str
        })

    # --- 4. 結果の表示 (main実行時のみ) ---
    if __name__ == '__main__':
        print("\n===========================================")
        print("👑 ロト6 改良版アンサンブル予測結果 👑")
        print("===========================================")
        print("--- 組み合わせ予測 (推奨度順) ---")
        for res in results:
            print(f"[推奨度: {res['recommendation']} (スコア: {res['score']})] ")
            print(f"  👉 {res['numbers']}")
        print("\n===========================================")
        print("推奨度は、各モデルの予測数字と組み合わせの統計的評価を統合した総合スコアです。")

    return results


if __name__ == '__main__':
    run_advanced_ensemble_prediction()

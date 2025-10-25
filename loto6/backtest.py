"""
ロト6用バックテスト基盤：時系列分割で予測モデルの性能を検証

指標：
- Top-K命中率（予測上位K件に正解が含まれる確率）
- 平均順位（正解が何位に予測されたか）
- 数字一致数（予測と正解で何個の数字が一致したか）
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Tuple
from collections import defaultdict


def time_series_split_backtest(
    df: pd.DataFrame,
    predict_function: Callable,
    train_size: int = 50,
    test_size: int = 1,
    top_k_list: List[int] = [10, 20, 50, 100],
    verbose: bool = True
) -> Dict[str, float]:
    """
    時系列分割でバックテストを実行（ロト6用）
    
    Args:
        df: 全抽選データ（時系列順）
        predict_function: 予測関数（df, limit）を受け取り、予測リスト（各要素は6個の数字のリスト）を返す
        train_size: 学習データのサイズ
        test_size: テストデータのサイズ（通常は1）
        top_k_list: 評価するTop-Kのリスト
        verbose: 進捗を表示するか
    
    Returns:
        評価指標の辞書
    """
    results = defaultdict(list)
    total_tests = len(df) - train_size - test_size + 1
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"ロト6 バックテスト開始")
        print(f"{'='*60}")
        print(f"学習データ: {train_size}回分")
        print(f"テスト回数: {total_tests}回")
        print(f"評価指標: Top-{top_k_list}命中率、平均順位、数字一致数")
        print(f"{'='*60}\n")
    
    for i in range(train_size, len(df) - test_size + 1):
        # 学習データとテストデータを分割
        train_df = df.iloc[i - train_size:i].copy()
        test_row = df.iloc[i]
        
        # 正解の当選番号（6個の数字）
        actual_numbers = set([test_row[f'num{j}'] for j in range(1, 7)])
        
        try:
            # 予測を実行（最大のKまで予測）
            max_k = max(top_k_list)
            predictions = predict_function(train_df, limit=max_k)
            
            # 予測が空の場合はスキップ
            if not predictions:
                continue
            
            # 各予測と正解の一致数を計算
            match_counts = []
            for pred in predictions:
                pred_set = set(pred)
                match_count = len(actual_numbers & pred_set)
                match_counts.append(match_count)
            
            # 完全一致（6個一致）が何位にあるか
            if 6 in match_counts:
                rank = match_counts.index(6) + 1
            else:
                rank = len(predictions) + 1  # 予測リスト外
            
            results['rank'].append(rank)
            
            # Top-K命中率を計算（完全一致）
            for k in top_k_list:
                hit = 1 if 6 in match_counts[:k] else 0
                results[f'top_{k}_hit'].append(hit)
            
            # 最高一致数（予測1位の一致数）
            if match_counts:
                results['best_match'].append(match_counts[0])
            
            # 平均一致数（Top-20の平均）
            if len(match_counts) >= 20:
                results['avg_match_top20'].append(np.mean(match_counts[:20]))
            
            if verbose and (i - train_size + 1) % 10 == 0:
                progress = (i - train_size + 1) / total_tests * 100
                print(f"進捗: {progress:.1f}% ({i - train_size + 1}/{total_tests}回)")
        
        except Exception as e:
            if verbose:
                print(f"⚠️ 第{i+1}回の予測でエラー: {e}")
            continue
    
    # 集計
    metrics = {}
    
    # 平均順位
    if results['rank']:
        metrics['avg_rank'] = np.mean(results['rank'])
        metrics['median_rank'] = np.median(results['rank'])
    
    # Top-K命中率
    for k in top_k_list:
        key = f'top_{k}_hit'
        if results[key]:
            metrics[f'top_{k}_hit_rate'] = np.mean(results[key]) * 100  # パーセント表示
    
    # 一致数
    if results['best_match']:
        metrics['avg_best_match'] = np.mean(results['best_match'])
    if results['avg_match_top20']:
        metrics['avg_match_top20'] = np.mean(results['avg_match_top20'])
    
    # 結果表示
    if verbose:
        print(f"\n{'='*60}")
        print(f"バックテスト結果")
        print(f"{'='*60}")
        print(f"テスト回数: {len(results['rank'])}回")
        print(f"\n【順位（完全一致）】")
        print(f"  平均順位: {metrics.get('avg_rank', 0):.1f}位")
        print(f"  中央値順位: {metrics.get('median_rank', 0):.1f}位")
        print(f"\n【Top-K命中率（完全一致）】")
        for k in top_k_list:
            rate = metrics.get(f'top_{k}_hit_rate', 0)
            print(f"  Top-{k:3d}: {rate:5.2f}%")
        print(f"\n【数字一致数】")
        print(f"  予測1位の平均一致数: {metrics.get('avg_best_match', 0):.2f}個")
        print(f"  Top-20の平均一致数: {metrics.get('avg_match_top20', 0):.2f}個")
        print(f"{'='*60}\n")
    
    return metrics


if __name__ == "__main__":
    # テスト用
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    from tools.utils import load_all_loto6_draws
    
    # データ読み込み
    df = load_all_loto6_draws()
    
    # 簡単なベースライン予測関数（テスト用）
    def baseline_predict(df, limit=50):
        """最頻出数字の組み合わせを返す"""
        from collections import Counter
        from itertools import combinations
        
        all_numbers = []
        for _, row in df.iterrows():
            for i in range(1, 7):
                if pd.notna(row[f'num{i}']):
                    all_numbers.append(int(row[f'num{i}']))
        
        freq = Counter(all_numbers)
        top_numbers = [n for n, _ in freq.most_common(15)]
        
        # 上位15個から6個を選ぶ組み合わせ
        predictions = []
        for combo in combinations(top_numbers, 6):
            predictions.append(list(combo))
            if len(predictions) >= limit:
                break
        
        return predictions
    
    # バックテスト実行
    print("ロト6 ベースラインモデルのバックテスト")
    metrics = time_series_split_backtest(
        df, baseline_predict, train_size=30, 
        top_k_list=[10, 20, 50], verbose=True
    )

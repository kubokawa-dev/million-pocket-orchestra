"""
ナンバーズ4用バックテスト基盤：時系列分割で予測モデルの性能を検証

指標（v2.0 ボックス評価追加）：
- Top-K命中率（予測上位K件に正解が含まれる確率）
- ボックスTop-K命中率（順不同で4桁が一致）
- 部分一致Top-K（3桁以上が一致）
- 平均順位（正解が何位に予測されたか）
- 合計値誤差（予測の合計値と正解の合計値の差）
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Tuple
from collections import defaultdict, Counter


def is_box_match(pred: str, actual: str) -> bool:
    """ボックス一致（順不同で数字が全て一致）をチェック"""
    return sorted(list(pred)) == sorted(list(actual))


def count_digit_matches(pred: str, actual: str) -> int:
    """何桁の数字が一致しているか（順不同）をカウント"""
    pred_counter = Counter(pred)
    actual_counter = Counter(actual)
    
    matches = 0
    for digit, count in actual_counter.items():
        matches += min(count, pred_counter.get(digit, 0))
    return matches


def time_series_split_backtest(
    df: pd.DataFrame,
    predict_function: Callable,
    train_size: int = 150,
    test_size: int = 1,
    top_k_list: List[int] = [10, 20, 50, 100],
    verbose: bool = True
) -> Dict[str, float]:
    """
    時系列分割でバックテストを実行（ナンバーズ4用）
    
    Args:
        df: 全抽選データ（時系列順）
        predict_function: 予測関数（df, limit）を受け取り、予測リストを返す
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
        print(f"ナンバーズ4 バックテスト開始 v2.0（ボックス評価対応）")
        print(f"{'='*60}")
        print(f"学習データ: {train_size}回分")
        print(f"テスト回数: {total_tests}回")
        print(f"評価指標:")
        print(f"  - ストレート命中率（完全一致）")
        print(f"  - ボックス命中率（順不同で4桁一致）")
        print(f"  - 部分一致率（3桁以上一致）")
        print(f"  - 平均順位、合計値誤差")
        print(f"{'='*60}\n")
    
    for i in range(train_size, len(df) - test_size + 1):
        # 学習データとテストデータを分割
        train_df = df.iloc[i - train_size:i].copy()
        test_row = df.iloc[i]
        
        # 正解の当選番号
        actual_number = "".join(map(str, test_row[['d1', 'd2', 'd3', 'd4']].values))
        actual_sum = sum(test_row[['d1', 'd2', 'd3', 'd4']].values)
        
        try:
            # 予測を実行（最大のKまで予測）
            max_k = max(top_k_list)
            predictions = predict_function(train_df, limit=max_k)
            
            # 予測がタプルのリストの場合、文字列に変換
            if predictions and isinstance(predictions[0], (list, tuple)):
                predictions = ["".join(map(str, p)) for p in predictions]
            
            # 正解が予測リストの何位にあるか
            if actual_number in predictions:
                rank = predictions.index(actual_number) + 1
            else:
                rank = len(predictions) + 1  # 予測リスト外
            
            results['rank'].append(rank)
            
            # Top-K命中率を計算
            for k in top_k_list:
                # ストレート一致
                straight_hit = 1 if actual_number in predictions[:k] else 0
                results[f'top_{k}_hit'].append(straight_hit)
                
                # ボックス一致（順不同で4桁全て一致）
                box_hit = 0
                for pred in predictions[:k]:
                    if is_box_match(pred, actual_number):
                        box_hit = 1
                        break
                results[f'top_{k}_box_hit'].append(box_hit)
                
                # 部分一致（3桁以上一致）
                partial_hit = 0
                for pred in predictions[:k]:
                    if count_digit_matches(pred, actual_number) >= 3:
                        partial_hit = 1
                        break
                results[f'top_{k}_partial_hit'].append(partial_hit)
            
            # 合計値誤差（予測1位の合計値と正解の合計値の差）
            if predictions:
                pred_sum = sum(int(d) for d in predictions[0])
                sum_error = abs(pred_sum - actual_sum)
                results['sum_error'].append(sum_error)
            
            if verbose and (i - train_size + 1) % 20 == 0:
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
    
    # Top-K命中率（ストレート）
    for k in top_k_list:
        key = f'top_{k}_hit'
        if results[key]:
            metrics[f'top_{k}_hit_rate'] = np.mean(results[key]) * 100  # パーセント表示
    
    # Top-K ボックス命中率
    for k in top_k_list:
        key = f'top_{k}_box_hit'
        if results[key]:
            metrics[f'top_{k}_box_hit_rate'] = np.mean(results[key]) * 100
    
    # Top-K 部分一致率
    for k in top_k_list:
        key = f'top_{k}_partial_hit'
        if results[key]:
            metrics[f'top_{k}_partial_hit_rate'] = np.mean(results[key]) * 100
    
    # 合計値誤差
    if results['sum_error']:
        metrics['avg_sum_error'] = np.mean(results['sum_error'])
    
    # 結果表示
    if verbose:
        print(f"\n{'='*60}")
        print(f"バックテスト結果 v2.0（ボックス評価対応）")
        print(f"{'='*60}")
        print(f"テスト回数: {len(results['rank'])}回")
        print(f"\n【順位】")
        print(f"  平均順位: {metrics.get('avg_rank', 0):.1f}位")
        print(f"  中央値順位: {metrics.get('median_rank', 0):.1f}位")
        
        print(f"\n【🎯 ストレート命中率（完全一致）】")
        for k in top_k_list:
            rate = metrics.get(f'top_{k}_hit_rate', 0)
            print(f"  Top-{k:3d}: {rate:5.2f}%")
        
        print(f"\n【📦 ボックス命中率（順不同で4桁一致）】")
        for k in top_k_list:
            rate = metrics.get(f'top_{k}_box_hit_rate', 0)
            print(f"  Top-{k:3d}: {rate:5.2f}%")
        
        print(f"\n【🎲 部分一致率（3桁以上一致）】")
        for k in top_k_list:
            rate = metrics.get(f'top_{k}_partial_hit_rate', 0)
            print(f"  Top-{k:3d}: {rate:5.2f}%")
        
        print(f"\n【合計値誤差】")
        print(f"  平均誤差: {metrics.get('avg_sum_error', 0):.2f}")
        print(f"{'='*60}\n")
    
    return metrics


if __name__ == "__main__":
    # テスト用
    import psycopg2
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # データ読み込み
    db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
    conn = psycopg2.connect(db_url)
    df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers4_draws ORDER BY draw_date ASC", conn)
    conn.close()
    
    # numbersを各桁に分割
    df['d1'] = df['numbers'].str[0].astype(int)
    df['d2'] = df['numbers'].str[1].astype(int)
    df['d3'] = df['numbers'].str[2].astype(int)
    df['d4'] = df['numbers'].str[3].astype(int)
    
    # 簡単なベースライン予測関数（テスト用）
    def baseline_predict(df, limit=50):
        """最頻出数字の組み合わせを返す"""
        from collections import Counter
        all_digits = pd.concat([df['d1'], df['d2'], df['d3'], df['d4']])
        freq = Counter(all_digits)
        top_digits = [d for d, _ in freq.most_common(7)]
        
        predictions = []
        for d1 in top_digits[:4]:
            for d2 in top_digits[:4]:
                for d3 in top_digits[:4]:
                    for d4 in top_digits[:4]:
                        predictions.append(f"{d1}{d2}{d3}{d4}")
                        if len(predictions) >= limit:
                            return predictions
        return predictions
    
    # バックテスト実行
    print("ナンバーズ4 ベースラインモデルのバックテスト")
    metrics = time_series_split_backtest(
        df, baseline_predict, train_size=100, 
        top_k_list=[10, 20, 50], verbose=True
    )

"""
ナンバーズ4 究極モデル - 第6844回(0017)のパターンを捉える

第6843回: 0523 (合計10)
第6844回: 0017 (合計8) - 0が2個、連続00、1桁目が連続

重要な特徴:
1. 0が複数個出現（特に連続00）
2. 1桁目の数字が連続
3. 極端に小さい合計値（5-10）
4. 小さい数字（0,1,2,3）が多い
"""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import product


def predict_from_zero_heavy_model(df: pd.DataFrame, limit: int = 300):
    """
    0重視モデル - 0が複数個出現するパターンを最優先
    
    第6844回(0017)のように0が2個以上出現するパターン
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近30回で0の出現頻度を確認
    recent_30 = df.tail(30)
    zero_count_by_pos = [0, 0, 0, 0]
    for _, row in recent_30.iterrows():
        for i in range(4):
            if row[f'd{i+1}'] == 0:
                zero_count_by_pos[i] += 1
    
    # === 戦略1: 0が2個出現するパターン（最優先） ===
    # 連続する00パターン
    for pos in range(3):  # 位置: 0-1, 1-2, 2-3
        for other1 in range(1, 10):
            for other2 in range(1, 10):
                if pos == 0:
                    num_str = f"00{other1}{other2}"
                elif pos == 1:
                    num_str = f"{other1}00{other2}"
                else:
                    num_str = f"{other1}{other2}00"
                
                if num_str != latest_number:
                    score = 50.0  # 非常に高いスコア
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 0が2個（非連続）
    for d1 in range(10):
        for d2 in range(10):
            for d3 in range(10):
                for d4 in range(10):
                    digits = [d1, d2, d3, d4]
                    if digits.count(0) == 2 and not (d1 == 0 and d2 == 0) and not (d2 == 0 and d3 == 0) and not (d3 == 0 and d4 == 0):
                        num_str = f"{d1}{d2}{d3}{d4}"
                        if num_str != latest_number:
                            score = 35.0
                            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 0が1個出現するパターン ===
    for pos in range(4):
        for d1 in range(10):
            for d2 in range(10):
                for d3 in range(10):
                    digits = [d1, d2, d3]
                    if pos == 0:
                        num_str = f"0{d1}{d2}{d3}"
                    elif pos == 1:
                        num_str = f"{d1}0{d2}{d3}"
                    elif pos == 2:
                        num_str = f"{d1}{d2}0{d3}"
                    else:
                        num_str = f"{d1}{d2}{d3}0"
                    
                    if num_str != latest_number and num_str.count('0') == 1:
                        score = 20.0
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_first_digit_continuation_model(df: pd.DataFrame, limit: int = 250):
    """
    1桁目継続モデル - 1桁目の数字が連続する可能性を最重視
    
    第6843回(0523) → 第6844回(0017): 1桁目の0が連続
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    first_digit = df.iloc[-1]['d1']
    
    # === 戦略1: 1桁目を完全に継続 ===
    for d2 in range(10):
        for d3 in range(10):
            for d4 in range(10):
                num_str = f"{first_digit}{d2}{d3}{d4}"
                if num_str != latest_number:
                    score = 40.0  # 非常に高いスコア
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_low_sum_model(df: pd.DataFrame, limit: int = 300):
    """
    低合計値モデル - 極端に小さい合計値（5-12）を重視
    
    第6844回(0017): 合計8
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近30回の合計値分布を確認
    recent_30 = df.tail(30)
    df_copy = recent_30.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3', 'd4']].sum(axis=1)
    sum_dist = Counter(df_copy['sum'])
    
    # === 戦略1: 極端に小さい合計値（5-12）を生成 ===
    target_sums = list(range(5, 13))  # 5-12
    
    for target_sum in target_sums:
        for d1 in range(10):
            for d2 in range(10):
                for d3 in range(10):
                    d4 = target_sum - d1 - d2 - d3
                    if 0 <= d4 <= 9:
                        num_str = f"{d1}{d2}{d3}{d4}"
                        if num_str != latest_number:
                            # 合計値が小さいほど高スコア
                            score = (13 - target_sum) * 5
                            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_small_digits_model(df: pd.DataFrame, limit: int = 300):
    """
    小数字重視モデル - 0,1,2,3の小さい数字を多く含むパターン
    
    第6844回(0017): 0,0,1,7 → 小さい数字が3個
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近30回で小さい数字（0-3）の出現頻度
    recent_30 = df.tail(30)
    small_digit_freq = Counter()
    for _, row in recent_30.iterrows():
        for i in range(4):
            digit = row[f'd{i+1}']
            if digit <= 3:
                small_digit_freq[digit] += 1
    
    # === 戦略1: 小さい数字（0-3）を多く含むパターン ===
    small_digits = [0, 1, 2, 3]
    
    # 4桁全て小さい数字
    for d1, d2, d3, d4 in product(small_digits, repeat=4):
        num_str = f"{d1}{d2}{d3}{d4}"
        if num_str != latest_number:
            score = 30.0
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 3桁が小さい数字
    for d1 in small_digits:
        for d2 in small_digits:
            for d3 in small_digits:
                for d4 in range(4, 10):
                    num_str = f"{d1}{d2}{d3}{d4}"
                    if num_str != latest_number:
                        score = 20.0
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_consecutive_same_digits_model(df: pd.DataFrame, limit: int = 250):
    """
    連続同数字モデル - 同じ数字が連続するパターン
    
    第6844回(0017): 00が連続
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近30回で各数字の出現頻度
    recent_30 = df.tail(30)
    all_digits = []
    for _, row in recent_30.iterrows():
        all_digits.extend([row['d1'], row['d2'], row['d3'], row['d4']])
    
    digit_freq = Counter(all_digits)
    top_digits = [d for d, _ in digit_freq.most_common(10)]
    
    # === 戦略1: 同じ数字が連続するパターン ===
    for digit in top_digits:
        # (d, d, x, y) パターン
        for other1 in range(10):
            for other2 in range(10):
                patterns = [
                    f"{digit}{digit}{other1}{other2}",
                    f"{other1}{digit}{digit}{other2}",
                    f"{other1}{other2}{digit}{digit}",
                ]
                for num_str in patterns:
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 15
                        if digit == 0:
                            score *= 2  # 0の連続は特に重視
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]

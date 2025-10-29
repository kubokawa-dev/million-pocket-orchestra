"""
予測ロジック v10.0 - 根本的改善版

問題点の分析:
- 第6843回: 631 (合計10)
- 第6844回: 656 (合計17) - 6が2回出現、1桁目が連続

従来モデルの問題:
1. 過去の当選番号を完全除外 → 実際は数字の再出現が多い
2. 直近の頻度のみ重視 → 大きな変化を見逃す
3. 同じ数字の複数出現を軽視

新アプローチ:
1. 数字の再出現を積極的に考慮
2. 前回の各桁が連続する可能性を重視
3. 同じ数字が複数桁に出現するパターンを生成
4. 大きな変化(±3-5)も考慮
"""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import product, combinations_with_replacement


def predict_from_digit_repetition_model(df: pd.DataFrame, limit: int = 300):
    """
    数字再出現モデル - 同じ数字が複数桁に出現するパターンを重視
    
    第6844回(656)のように、同じ数字が2-3回出現するケースを予測
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    # 直近30回で各数字の出現頻度を計算
    recent_30 = df.tail(30)
    all_digits = []
    for _, row in recent_30.iterrows():
        all_digits.extend([row['d1'], row['d2'], row['d3']])
    
    digit_freq = Counter(all_digits)
    top_digits = [d for d, _ in digit_freq.most_common(8)]
    
    # === 戦略1: 同じ数字が2回出現するパターン ===
    for digit in top_digits:
        # (digit, digit, x) パターン
        for third in range(10):
            if third != digit:  # 3つ全て同じは除外
                num_str = f"{digit}{digit}{third}"
                if num_str != latest_number:
                    score = digit_freq.get(digit, 0) * 15
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                
                # (digit, x, digit) パターン
                num_str = f"{digit}{third}{digit}"
                if num_str != latest_number:
                    score = digit_freq.get(digit, 0) * 15
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                
                # (x, digit, digit) パターン
                num_str = f"{third}{digit}{digit}"
                if num_str != latest_number:
                    score = digit_freq.get(digit, 0) * 15
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 3つ全て同じ数字 ===
    for digit in top_digits:
        num_str = f"{digit}{digit}{digit}"
        if num_str != latest_number:
            score = digit_freq.get(digit, 0) * 10
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_digit_continuation_model(df: pd.DataFrame, limit: int = 250):
    """
    桁継続モデル - 前回の各桁が次回も出現する可能性を重視
    
    第6844回(656)の1桁目6は第6843回(631)の1桁目6と同じ
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3']]
    
    # 直近10回の各桁の頻度
    recent_10 = df.tail(10)
    digit_freq_by_pos = []
    for i in range(3):
        freq = Counter(recent_10[f'd{i+1}'])
        digit_freq_by_pos.append(freq)
    
    # === 戦略1: 前回の各桁をそのまま使う ===
    # 1桁目を継続
    for d2 in range(10):
        for d3 in range(10):
            num_str = f"{latest_digits[0]}{d2}{d3}"
            if num_str != latest_number:
                score = 20.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 2桁目を継続
    for d1 in range(10):
        for d3 in range(10):
            num_str = f"{d1}{latest_digits[1]}{d3}"
            if num_str != latest_number:
                score = 18.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 3桁目を継続
    for d1 in range(10):
        for d2 in range(10):
            num_str = f"{d1}{d2}{latest_digits[2]}"
            if num_str != latest_number:
                score = 18.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 前回の数字を2つ継続 ===
    # 1桁目と2桁目を継続
    for d3 in range(10):
        num_str = f"{latest_digits[0]}{latest_digits[1]}{d3}"
        if num_str != latest_number:
            score = 25.0
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 2桁目と3桁目を継続
    for d1 in range(10):
        num_str = f"{d1}{latest_digits[1]}{latest_digits[2]}"
        if num_str != latest_number:
            score = 25.0
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 1桁目と3桁目を継続
    for d2 in range(10):
        num_str = f"{latest_digits[0]}{d2}{latest_digits[2]}"
        if num_str != latest_number:
            score = 25.0
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_large_change_model(df: pd.DataFrame, limit: int = 200):
    """
    大変化モデル - 前回から大きく変化するパターンを考慮
    
    第6843回(631) → 第6844回(656): 3桁目が1→6(+5)の大変化
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3']]
    
    # === 戦略1: 各桁に±3-5の大きな変化 ===
    large_deltas = [-5, -4, -3, 3, 4, 5]
    
    for delta1 in large_deltas + [0]:
        for delta2 in large_deltas + [0]:
            for delta3 in large_deltas + [0]:
                # 少なくとも1桁は大きく変化
                if abs(delta1) >= 3 or abs(delta2) >= 3 or abs(delta3) >= 3:
                    new_digits = [
                        latest_digits[0] + delta1,
                        latest_digits[1] + delta2,
                        latest_digits[2] + delta3
                    ]
                    if all(0 <= d <= 9 for d in new_digits):
                        num_str = "".join(map(str, new_digits))
                        if num_str != latest_number:
                            # 大きな変化ほど高スコア
                            total_change = abs(delta1) + abs(delta2) + abs(delta3)
                            score = total_change * 2
                            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_realistic_frequency_model(df: pd.DataFrame, limit: int = 400):
    """
    現実的頻度モデル - 過去の当選番号除外をやめ、実際の頻度を重視
    
    重要な変更: 過去の当選番号も候補に含める
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    # 直近データの分析
    recent_5 = df.tail(5)
    recent_10 = df.tail(10)
    recent_20 = df.tail(20)
    
    # 各桁の頻度（期間別）
    def get_top_digits(df_subset, position, top_n=7):
        freq = Counter(df_subset[f'd{position+1}'])
        return [d for d, _ in freq.most_common(top_n)]
    
    top_digits_5 = [get_top_digits(recent_5, i, 5) for i in range(3)]
    top_digits_10 = [get_top_digits(recent_10, i, 6) for i in range(3)]
    top_digits_20 = [get_top_digits(recent_20, i, 7) for i in range(3)]
    
    # 全組み合わせを生成（過去の当選番号も含む）
    all_top_digits = []
    for i in range(3):
        combined = list(set(top_digits_5[i] + top_digits_10[i] + top_digits_20[i]))
        all_top_digits.append(combined[:8])
    
    for d1, d2, d3 in product(all_top_digits[0], all_top_digits[1], all_top_digits[2]):
        num_str = f"{d1}{d2}{d3}"
        if num_str != latest_number:  # 前回のみ除外
            # スコア: 直近5回を最重視
            score = (recent_5['d1'].tolist().count(d1) * 25 +
                    recent_5['d2'].tolist().count(d2) * 25 +
                    recent_5['d3'].tolist().count(d3) * 25 +
                    recent_10['d1'].tolist().count(d1) * 10 +
                    recent_10['d2'].tolist().count(d2) * 10 +
                    recent_10['d3'].tolist().count(d3) * 10)
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_balanced_sum_model(df: pd.DataFrame, limit: int = 250):
    """
    バランス合計値モデル - 合計値の幅を広げる
    
    第6843回(631)合計10 → 第6844回(656)合計17
    大きな変化も考慮
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    # 直近30回の合計値分布
    recent_30 = df.tail(30)
    df_copy = recent_30.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3']].sum(axis=1)
    sum_dist = Counter(df_copy['sum'])
    
    # 頻出する合計値トップ15（幅広く）
    target_sums = [s for s, _ in sum_dist.most_common(15)]
    
    # 各桁の頻出数字
    top_digits = []
    for i in range(3):
        freq = Counter(recent_30[f'd{i+1}'])
        top_digits.append([d for d, _ in freq.most_common(8)])
    
    # 合計値に合致するパターンを生成
    for target_sum in target_sums:
        for d1 in top_digits[0]:
            for d2 in top_digits[1]:
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number:
                        sum_freq = sum_dist.get(target_sum, 0)
                        score = sum_freq * 8
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]

"""
ナンバーズ4予測ロジック v10.0 - ナンバーズ3の成功を適用

ナンバーズ3 v10.0で成功したアプローチをナンバーズ4に適用:
1. 数字再出現モデル - 同じ数字が複数桁に出現
2. 桁継続モデル - 前回の数字が次回も出現
3. 現実的頻度モデル - 過去当選番号も含む
4. 大変化モデル - ±3-5の大きな変化
"""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import product


def predict_from_digit_repetition_model_n4(df: pd.DataFrame, limit: int = 300):
    """
    数字再出現モデル（ナンバーズ4版）
    
    同じ数字が複数桁に出現するパターンを重視
    例: 0523 → 0が1回、5が1回、2が1回、3が1回
         1122 → 1が2回、2が2回
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近30回で各数字の出現頻度を計算
    recent_30 = df.tail(30)
    all_digits = []
    for _, row in recent_30.iterrows():
        all_digits.extend([row['d1'], row['d2'], row['d3'], row['d4']])
    
    digit_freq = Counter(all_digits)
    top_digits = [d for d, _ in digit_freq.most_common(8)]
    
    # === 戦略1: 同じ数字が2回出現するパターン ===
    for digit in top_digits:
        # (d, d, x, y) パターン
        for third in range(10):
            for fourth in range(10):
                if not (third == digit and fourth == digit):  # 3つ以上同じは別で生成
                    num_str = f"{digit}{digit}{third}{fourth}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                    
                    # (d, x, d, y) パターン
                    num_str = f"{digit}{third}{digit}{fourth}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                    
                    # (d, x, y, d) パターン
                    num_str = f"{digit}{third}{fourth}{digit}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                    
                    # (x, d, d, y) パターン
                    num_str = f"{third}{digit}{digit}{fourth}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                    
                    # (x, d, y, d) パターン
                    num_str = f"{third}{digit}{fourth}{digit}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                    
                    # (x, y, d, d) パターン
                    num_str = f"{third}{fourth}{digit}{digit}"
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 12
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 同じ数字が3回出現するパターン ===
    for digit in top_digits[:5]:  # 上位5個のみ
        for other in range(10):
            if other != digit:
                patterns = [
                    f"{digit}{digit}{digit}{other}",
                    f"{digit}{digit}{other}{digit}",
                    f"{digit}{other}{digit}{digit}",
                    f"{other}{digit}{digit}{digit}"
                ]
                for num_str in patterns:
                    if num_str != latest_number:
                        score = digit_freq.get(digit, 0) * 10
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略3: 4つ全て同じ数字 ===
    for digit in top_digits[:3]:
        num_str = f"{digit}{digit}{digit}{digit}"
        if num_str != latest_number:
            score = digit_freq.get(digit, 0) * 8
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_digit_continuation_model_n4(df: pd.DataFrame, limit: int = 250):
    """
    桁継続モデル（ナンバーズ4版）
    
    前回の各桁が次回も出現する可能性を重視
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3'], df.iloc[-1]['d4']]
    
    # === 戦略1: 前回の各桁を1つ継続 ===
    # 1桁目を継続
    for d2 in range(10):
        for d3 in range(10):
            for d4 in range(10):
                num_str = f"{latest_digits[0]}{d2}{d3}{d4}"
                if num_str != latest_number:
                    score = 18.0
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 2桁目を継続
    for d1 in range(10):
        for d3 in range(10):
            for d4 in range(10):
                num_str = f"{d1}{latest_digits[1]}{d3}{d4}"
                if num_str != latest_number:
                    score = 16.0
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 3桁目を継続
    for d1 in range(10):
        for d2 in range(10):
            for d4 in range(10):
                num_str = f"{d1}{d2}{latest_digits[2]}{d4}"
                if num_str != latest_number:
                    score = 16.0
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 4桁目を継続
    for d1 in range(10):
        for d2 in range(10):
            for d3 in range(10):
                num_str = f"{d1}{d2}{d3}{latest_digits[3]}"
                if num_str != latest_number:
                    score = 18.0
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 前回の2桁を継続 ===
    # 1-2桁目を継続
    for d3 in range(10):
        for d4 in range(10):
            num_str = f"{latest_digits[0]}{latest_digits[1]}{d3}{d4}"
            if num_str != latest_number:
                score = 22.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 3-4桁目を継続
    for d1 in range(10):
        for d2 in range(10):
            num_str = f"{d1}{d2}{latest_digits[2]}{latest_digits[3]}"
            if num_str != latest_number:
                score = 22.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_large_change_model_n4(df: pd.DataFrame, limit: int = 200):
    """
    大変化モデル（ナンバーズ4版）
    
    前回から大きく変化するパターンを考慮
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3'], df.iloc[-1]['d4']]
    
    # === 戦略1: 各桁に±3-5の大きな変化 ===
    large_deltas = [-5, -4, -3, 3, 4, 5]
    
    for delta1 in large_deltas + [0]:
        for delta2 in large_deltas + [0]:
            for delta3 in large_deltas + [0]:
                for delta4 in large_deltas + [0]:
                    # 少なくとも1桁は大きく変化
                    if abs(delta1) >= 3 or abs(delta2) >= 3 or abs(delta3) >= 3 or abs(delta4) >= 3:
                        new_digits = [
                            latest_digits[0] + delta1,
                            latest_digits[1] + delta2,
                            latest_digits[2] + delta3,
                            latest_digits[3] + delta4
                        ]
                        if all(0 <= d <= 9 for d in new_digits):
                            num_str = "".join(map(str, new_digits))
                            if num_str != latest_number:
                                # 大きな変化ほど高スコア
                                total_change = abs(delta1) + abs(delta2) + abs(delta3) + abs(delta4)
                                score = total_change * 1.5
                                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_realistic_frequency_model_n4(df: pd.DataFrame, limit: int = 400):
    """
    現実的頻度モデル（ナンバーズ4版）
    
    過去の当選番号除外をやめ、実際の頻度を重視
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 直近データの分析
    recent_5 = df.tail(5)
    recent_10 = df.tail(10)
    recent_20 = df.tail(20)
    
    # 各桁の頻度（期間別）
    def get_top_digits(df_subset, position, top_n=7):
        freq = Counter(df_subset[f'd{position+1}'])
        return [d for d, _ in freq.most_common(top_n)]
    
    top_digits_5 = [get_top_digits(recent_5, i, 5) for i in range(4)]
    top_digits_10 = [get_top_digits(recent_10, i, 6) for i in range(4)]
    top_digits_20 = [get_top_digits(recent_20, i, 7) for i in range(4)]
    
    # 全組み合わせを生成（過去の当選番号も含む）
    all_top_digits = []
    for i in range(4):
        combined = list(set(top_digits_5[i] + top_digits_10[i] + top_digits_20[i]))
        all_top_digits.append(combined[:7])  # 各桁上位7個
    
    for d1, d2, d3, d4 in product(all_top_digits[0], all_top_digits[1], all_top_digits[2], all_top_digits[3]):
        num_str = f"{d1}{d2}{d3}{d4}"
        if num_str != latest_number:  # 前回のみ除外
            # スコア: 直近5回を最重視
            score = (recent_5['d1'].tolist().count(d1) * 20 +
                    recent_5['d2'].tolist().count(d2) * 20 +
                    recent_5['d3'].tolist().count(d3) * 20 +
                    recent_5['d4'].tolist().count(d4) * 20 +
                    recent_10['d1'].tolist().count(d1) * 8 +
                    recent_10['d2'].tolist().count(d2) * 8 +
                    recent_10['d3'].tolist().count(d3) * 8 +
                    recent_10['d4'].tolist().count(d4) * 8)
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]

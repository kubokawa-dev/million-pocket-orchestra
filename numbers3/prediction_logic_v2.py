"""
改善版予測ロジック - 第6844回に向けた最適化

改善ポイント:
1. 実際の当選番号の特徴分析を強化
2. 連続性・周期性の検出精度向上
3. 各桁の独立性と相関性のバランス調整
4. 最近のトレンドへの適応力強化
"""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import product


def analyze_recent_patterns(df: pd.DataFrame, window_size: int = 20):
    """
    最近の当選番号から特徴的なパターンを抽出
    
    Returns:
        dict: パターン分析結果
    """
    recent = df.tail(window_size)
    
    patterns = {
        'digit_freq': [{}, {}, {}],  # 各桁の頻度
        'sum_dist': Counter(),       # 合計値の分布
        'diff_patterns': [],         # 前回からの差分パターン
        'pair_freq': Counter(),      # 隣接ペアの頻度
        'triple_patterns': Counter(), # 3桁の特徴（昇順/降順/ランダム）
    }
    
    # 各桁の頻度
    for i in range(3):
        patterns['digit_freq'][i] = Counter(recent[f'd{i+1}'])
    
    # 合計値の分布
    patterns['sum_dist'] = Counter(recent[['d1', 'd2', 'd3']].sum(axis=1))
    
    # 差分パターン（前回からの変化）
    for i in range(1, len(recent)):
        prev_row = recent.iloc[i-1]
        curr_row = recent.iloc[i]
        diff = [
            curr_row['d1'] - prev_row['d1'],
            curr_row['d2'] - prev_row['d2'],
            curr_row['d3'] - prev_row['d3']
        ]
        patterns['diff_patterns'].append(diff)
    
    # ペア頻度
    for _, row in recent.iterrows():
        patterns['pair_freq'][(row['d1'], row['d2'])] += 1
        patterns['pair_freq'][(row['d2'], row['d3'])] += 1
    
    # 3桁のパターン（昇順/降順/その他）
    for _, row in recent.iterrows():
        digits = [row['d1'], row['d2'], row['d3']]
        if digits == sorted(digits):
            patterns['triple_patterns']['ascending'] += 1
        elif digits == sorted(digits, reverse=True):
            patterns['triple_patterns']['descending'] += 1
        else:
            patterns['triple_patterns']['random'] += 1
    
    return patterns


def predict_from_enhanced_statistical_model(df: pd.DataFrame, limit: int = 300):
    """
    強化版統計モデル - 実際の当選傾向を重視
    
    特徴:
    1. 直近10回の各桁頻度を最優先
    2. 合計値の実績分布に厳密に従う
    3. 前回からの変化パターンを学習
    4. 過去の当選番号は完全除外
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # パターン分析
    patterns_10 = analyze_recent_patterns(df, 10)
    patterns_30 = analyze_recent_patterns(df, 30)
    
    # === 戦略1: 各桁の頻出数字の組み合わせ（最重要） ===
    top_digits = []
    for i in range(3):
        # 直近10回の頻度を最優先（重み5倍）
        combined = Counter()
        for digit in range(10):
            score = (patterns_10['digit_freq'][i].get(digit, 0) * 5 + 
                    patterns_30['digit_freq'][i].get(digit, 0))
            combined[digit] = score
        
        # 上位5個を抽出
        top_5 = [d for d, _ in combined.most_common(5)]
        # 次点3個も追加（多様性確保）
        next_3 = [d for d, _ in combined.most_common(8) if d not in top_5][:3]
        top_digits.append(top_5 + next_3)
    
    # 全組み合わせを生成
    for d1, d2, d3 in product(top_digits[0], top_digits[1], top_digits[2]):
        num_str = f"{d1}{d2}{d3}"
        if num_str != latest_number and num_str not in historical_numbers:
            # スコア計算
            score = (patterns_10['digit_freq'][0].get(d1, 0) * 10 +
                    patterns_10['digit_freq'][1].get(d2, 0) * 10 +
                    patterns_10['digit_freq'][2].get(d3, 0) * 10 +
                    patterns_30['digit_freq'][0].get(d1, 0) * 2 +
                    patterns_30['digit_freq'][1].get(d2, 0) * 2 +
                    patterns_30['digit_freq'][2].get(d3, 0) * 2)
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 合計値の実績分布に従う ===
    # 頻出する合計値トップ10
    target_sums = [s for s, _ in patterns_30['sum_dist'].most_common(10)]
    
    for target_sum in target_sums:
        for d1 in top_digits[0]:
            for d2 in top_digits[1]:
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number and num_str not in historical_numbers:
                        sum_freq = patterns_30['sum_dist'].get(target_sum, 0)
                        score = sum_freq * 5
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略3: 頻出ペアを活用 ===
    top_pairs = [pair for pair, _ in patterns_30['pair_freq'].most_common(15)]
    
    for pair in top_pairs:
        d1, d2 = pair
        # (d1, d2) + 任意のd3
        for d3 in range(10):
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number and num_str not in historical_numbers:
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 15
        
        # 任意のd1 + (d2, d3)
        for d1_new in range(10):
            num_str = f"{d1_new}{d1}{d2}"
            if num_str != latest_number and num_str not in historical_numbers:
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 15
    
    # === 戦略4: 前回からの変化パターン学習 ===
    if len(patterns_10['diff_patterns']) > 0:
        # 最頻出の変化パターンを抽出
        diff_counter = Counter([tuple(d) for d in patterns_10['diff_patterns']])
        top_diffs = [list(d) for d, _ in diff_counter.most_common(5)]
        
        latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3']]
        
        for diff in top_diffs:
            new_digits = [
                latest_digits[0] + diff[0],
                latest_digits[1] + diff[1],
                latest_digits[2] + diff[2]
            ]
            if all(0 <= d <= 9 for d in new_digits):
                num_str = "".join(map(str, new_digits))
                if num_str != latest_number and num_str not in historical_numbers:
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 20
    
    # スコア順にソート
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_cycle_analysis(df: pd.DataFrame, limit: int = 200):
    """
    周期性分析モデル - N回前との類似性を検出
    
    特徴:
    - 5回前、10回前、15回前との相関を分析
    - 微小な変化（±1-2）を考慮
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    cycles = [5, 7, 10, 14, 15, 20]
    
    for cycle in cycles:
        if len(df) > cycle:
            past_row = df.iloc[-cycle-1]
            past_digits = [past_row['d1'], past_row['d2'], past_row['d3']]
            
            # ±0-2の変化を試行
            for delta1 in range(-2, 3):
                for delta2 in range(-2, 3):
                    for delta3 in range(-2, 3):
                        new_digits = [
                            past_digits[0] + delta1,
                            past_digits[1] + delta2,
                            past_digits[2] + delta3
                        ]
                        if all(0 <= d <= 9 for d in new_digits):
                            num_str = "".join(map(str, new_digits))
                            if num_str != latest_number and num_str not in historical_numbers:
                                # 変化が小さいほど高スコア
                                delta_penalty = abs(delta1) + abs(delta2) + abs(delta3)
                                score = 10.0 / (1 + delta_penalty) / cycle
                                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_trend_continuation(df: pd.DataFrame, limit: int = 150):
    """
    トレンド継続モデル - 最近の変化傾向を延長
    
    特徴:
    - 直近3-5回の各桁の増減傾向を分析
    - トレンドが継続すると仮定
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    if len(df) < 5:
        return []
    
    recent_5 = df.tail(5)
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3']]
    
    # 各桁のトレンド分析
    trends = []
    for i in range(3):
        values = recent_5[f'd{i+1}'].values
        # 線形回帰的な傾向
        if len(values) >= 3:
            avg_change = (values[-1] - values[0]) / (len(values) - 1)
            trends.append(avg_change)
        else:
            trends.append(0)
    
    # トレンドを延長して予測
    for scale in [0.5, 1.0, 1.5, 2.0]:
        new_digits = [
            int(latest_digits[0] + trends[0] * scale),
            int(latest_digits[1] + trends[1] * scale),
            int(latest_digits[2] + trends[2] * scale)
        ]
        
        # 範囲内に収める
        new_digits = [max(0, min(9, d)) for d in new_digits]
        
        num_str = "".join(map(str, new_digits))
        if num_str != latest_number and num_str not in historical_numbers:
            score = 20.0 / scale
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
        
        # 微調整版も生成
        for adj1 in [-1, 0, 1]:
            for adj2 in [-1, 0, 1]:
                for adj3 in [-1, 0, 1]:
                    adjusted = [
                        max(0, min(9, new_digits[0] + adj1)),
                        max(0, min(9, new_digits[1] + adj2)),
                        max(0, min(9, new_digits[2] + adj3))
                    ]
                    num_str = "".join(map(str, adjusted))
                    if num_str != latest_number and num_str not in historical_numbers:
                        score = 5.0 / scale
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]

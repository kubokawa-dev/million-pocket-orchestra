import pandas as pd
import numpy as np
import json
from collections import Counter

def learn_model_from_data(df: pd.DataFrame):
    """
    過去のデータから各数字の出現確率を学習し、モデルの状態を返します。
    Loto6用に調整。
    """
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 1から43までの全ての数字を対象
    all_possible_numbers = list(range(1, 44))
    
    # 各数字の出現回数をカウント
    all_draws = df[num_cols].values.flatten()
    all_draws = all_draws[~np.isnan(all_draws)] # NaNを除外
    number_counts = Counter(all_draws.astype(int))
    
    total_draws = len(df)
    
    # 各数字の出現確率を計算 (ラプラススムージング)
    # 各数字は6回/抽選のチャンスがあるので、総数は total_draws * 6
    total_numbers_drawn = total_draws * 6
    
    # 各数字ごとの確率を計算
    # Loto6には「桁」の概念がないため、全数字で一つの確率分布を持つ
    probabilities = {}
    for num in all_possible_numbers:
        # スムージングを追加して、一度も出ていない数字にもわずかな確率を与える
        probabilities[num] = (number_counts.get(num, 0) + 1) / (total_numbers_drawn + len(all_possible_numbers))
        
    # 重みを正規化
    total_prob = sum(probabilities.values())
    normalized_probabilities = {str(k): v / total_prob for k, v in probabilities.items()}
    
    # モデルの状態を構築
    # Numbers4と異なり、桁ごとの重みはない
    model_state = {
        "model_type": "loto6_probability_model",
        "total_draws_analyzed": total_draws,
        "number_probabilities": normalized_probabilities # 1-43の数字ごとの確率
    }
    
    return model_state

def save_model_state(model_state, path):
    """モデルの状態をJSONファイルに保存します。"""
    with open(path, 'w') as f:
        json.dump(model_state, f, indent=4)

def load_model_state(path):
    """JSONファイルからモデルの状態を読み込みます。"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

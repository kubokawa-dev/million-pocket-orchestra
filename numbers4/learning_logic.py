import numpy as np
import pandas as pd

def learn_model_from_data(df: pd.DataFrame, initial_weights=None, learning_rate=0.05):
    """
    過去の抽選データから桁ごとの数字の出現確率を学習する。
    元の learn_from_predictions.py のロジックを一般化。

    :param df: 学習に使用する抽選データ（'d1', 'd2', 'd3', 'd4' カラムが必要）
    :param initial_weights: 初期重み。Noneの場合は均等に初期化。
    :param learning_rate: 学習率。新しいデータにどれだけ重みを与えるか。
    :return: 学習後の重み（4x10のnumpy配列）
    """
    if initial_weights:
        weights = [np.array(w) for w in initial_weights]
    else:
        # 均等な確率で初期化
        weights = [np.full(10, 0.1) for _ in range(4)]

    # DataFrameの各行（過去の抽選結果）をループして学習
    for _, row in df.iterrows():
        winning_numbers = [row['d1'], row['d2'], row['d3'], row['d4']]
        
        for i in range(4):
            actual_digit = winning_numbers[i]
            
            # 当選した数字の確率を上げる
            weights[i][actual_digit] += learning_rate
            
            # 全体の合計が1になるように正規化
            weights[i] /= weights[i].sum()

    return weights

import pandas as pd
import numpy as np
from collections import Counter
import json
import os

# --- 1. predict_numbers.py からのロジック ---
def predict_from_basic_stats(df: pd.DataFrame, num_predictions: int = 5):
    """
    基本的な統計情報（出現頻度、最新の数字）に基づいて予測を生成する。
    元々の predict_numbers.py のロジック。
    """
    # 各桁の数字をリストに変換
    first_digits = df['d1'].tolist()
    second_digits = df['d2'].tolist()
    third_digits = df['d3'].tolist()
    fourth_digits = df['d4'].tolist()

    # 各桁の数字の出現回数をカウント
    first_counts = Counter(first_digits)
    second_counts = Counter(second_digits)
    third_counts = Counter(third_digits)
    fourth_counts = Counter(fourth_digits)

    # 最新の抽選番号
    latest_draw = df.iloc[-1]
    
    predictions = []
    for _ in range(num_predictions):
        prediction = ""
        # 1桁目: 出現回数が多く、かつ最新の数字に近いものを優先
        prediction += str(sorted(first_counts.keys(), key=lambda x: (first_counts[x], -abs(x - latest_draw['d1'])), reverse=True)[len(predictions) % len(first_counts)])
        # 2桁目: 同様に、出現回数と近さでソート
        prediction += str(sorted(second_counts.keys(), key=lambda x: (second_counts[x], -abs(x - latest_draw['d2'])), reverse=True)[len(predictions) % len(second_counts)])
        # 3桁目
        prediction += str(sorted(third_counts.keys(), key=lambda x: (third_counts[x], -abs(x - latest_draw['d3'])), reverse=True)[len(predictions) % len(third_counts)])
        # 4桁目
        prediction += str(sorted(fourth_counts.keys(), key=lambda x: (fourth_counts[x], -abs(x - latest_draw['d4'])), reverse=True)[len(predictions) % len(fourth_counts)])
        predictions.append(prediction)
    
    # 重複を除去して返す
    return list(dict.fromkeys(predictions))

# --- 2. advanced_predict_numbers4.py からのロジック ---
def predict_from_advanced_heuristics(df: pd.DataFrame, num_predictions: int = 5):
    """
    高度なヒューリスティック（合計値、偶数奇数、ペアの頻度）に基づいて予測を生成する。
    元々の advanced_predict_numbers4.py のロジック。
    """
    df['sum'] = df[['d1', 'd2', 'd3', 'd4']].sum(axis=1)
    df['even_count'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda row: sum(x % 2 == 0 for x in row), axis=1)
    
    # ペアの頻度を計算
    pairs = []
    for _, row in df.iterrows():
        for i in range(3):
            pairs.append(tuple(sorted((row[f'd{i+1}'], row[f'd{i+2}']))) )

    pair_counts = Counter(pairs)
    
    # スコアリング
    scored_numbers = []
    for i in range(10000):
        num_str = f"{i:04d}"
        n1, n2, n3, n4 = [int(d) for d in num_str]
        
        current_sum = n1 + n2 + n3 + n4
        current_even_count = sum(x % 2 == 0 for x in [n1, n2, n3, n4])
        
        # スコア計算
        score = 0
        # 合計値の近さ
        score += 1 / (1 + abs(current_sum - df['sum'].mode()[0]))
        # 偶数・奇数のバランス
        score += 1 / (1 + abs(current_even_count - df['even_count'].mode()[0]))
        # ペアの頻度
        score += pair_counts[tuple(sorted((n1, n2)))]
        score += pair_counts[tuple(sorted((n2, n3)))]
        score += pair_counts[tuple(sorted((n3, n4)))]
        
        scored_numbers.append((num_str, score))
        
    # スコア上位を予測とする
    scored_numbers.sort(key=lambda x: x[1], reverse=True)
    
    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    predictions = []
    for num, _ in scored_numbers:
        if num != latest_number:
            predictions.append(num)
        if len(predictions) == num_predictions:
            break
            
    return predictions

# --- 3. predict_numbers_with_model.py からのロジック ---
def predict_with_model(df: pd.DataFrame, model_state_path: str, num_predictions: int = 12):
    """
    機械学習モデルの状態に基づいて予測を生成する。
    元々の predict_numbers_with_model.py のロジック。
    """
    if not os.path.exists(model_state_path):
        # モデルがない場合は、基本的な予測にフォールバック
        return predict_from_basic_stats(df, num_predictions)

    with open(model_state_path, 'r') as f:
        model_state = json.load(f)

    weights = [np.array(w) for w in model_state['weights']]
    
    # 最新の当選番号
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))

    predictions = set()
    attempts = 0
    while len(predictions) < num_predictions and attempts < 1000:
        prediction_list = []
        for i in range(4):
            # 重み付き確率で数字を選択
            digit = np.random.choice(10, p=weights[i])
            prediction_list.append(str(digit))
        
        prediction = "".join(prediction_list)
        
        # 最新の当選番号と重複しないようにする
        if prediction != latest_number:
            predictions.add(prediction)
        attempts += 1
        
    return list(predictions)

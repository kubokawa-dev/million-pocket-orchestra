import pandas as pd
import numpy as np
from collections import Counter
import json
import os

# --- 1. predict_numbers.py からのロジック ---
def predict_from_basic_stats(df: pd.DataFrame, limit: int = 5):
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
    for _ in range(limit):
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
def predict_from_advanced_heuristics(df: pd.DataFrame, limit: int = 5):
    """
    高度なヒューリスティック（合計値、偶数奇数、ペアの頻度）に基づいて予測を生成する。
    元々の advanced_predict_numbers4.py のロジック。
    """
    # コピーして安全に列を追加（SettingWithCopyWarning 回避）
    df = df.copy()
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
        if len(predictions) == limit:
            break
            
    return predictions

# --- 3. predict_numbers_with_model.py からのロジック ---
def predict_with_model(
    model_weights: list | None,
    limit: int = 12,
):
    """
    機械学習モデルの状態に基づいて予測を生成する。
    """
    if model_weights is None:
        # モデルがなければ空リストを返す
        return []
    
    weights = [np.array(w) for w in model_weights]
    
    predictions = set()
    attempts = 0
    while len(predictions) < limit and attempts < 1000:
        prediction_list = []
        for i in range(4):
            # 重み付き確率で数字を選択
            digit = np.random.choice(10, p=weights[i])
            prediction_list.append(str(digit))
        
        prediction = "".join(prediction_list)
        predictions.add(prediction)
        attempts += 1
        
    return list(predictions)


# --- 4. Exploratory Prediction (New) ---
def predict_from_exploratory_heuristics(df: pd.DataFrame, limit: int = 5):
    """
    探索的ヒューリスティックに基づき、統計的な「穴」を狙う予測を生成する。
    合計値が極端に低い/高い組み合わせや、長期間出現していない数字を重視する。
    """
    df = df.copy()
    df['sum'] = df[['d1', 'd2', 'd3', 'd4']].sum(axis=1)

    # 長期間出現していない数字（コールドナンバー）を特定
    all_digits = pd.concat([df[f'd{i+1}'] for i in range(4)])
    digit_counts = Counter(all_digits)
    cold_digits = [digit for digit, count in digit_counts.items() if count <= np.percentile(list(digit_counts.values()), 25)]
    if not cold_digits: # もしコールドな数字がなければ、最も出現頻度の低いものを選ぶ
        cold_digits = [digit_counts.most_common()[-1][0]]

    predictions = set()
    attempts = 0

    # 1. 超低合計値/超高合計値を狙う
    low_sum_target = 9  # e.g., 0-9
    high_sum_target = 28 # e.g., 28-36

    while len(predictions) < limit and attempts < 20000:
        attempts += 1
        # 候補をランダムに生成
        pred = np.random.randint(0, 10000)
        num_str = f"{pred:04d}"
        n1, n2, n3, n4 = [int(d) for d in num_str]
        current_sum = sum([n1, n2, n3, n4])

        # 50%の確率で低合計値、50%の確率で高合計値を狙う
        if np.random.rand() < 0.5:
            # 低合計値に近ければ採用
            if current_sum <= low_sum_target:
                predictions.add(num_str)
        else:
            # 高合計値に近ければ採用
            if current_sum >= high_sum_target:
                predictions.add(num_str)

    # 2. コールドな数字を積極的に使う
    while len(predictions) < limit * 2 and attempts < 40000:
        attempts += 1
        pred_list = np.random.choice(cold_digits, 4, replace=True)
        np.random.shuffle(pred_list)
        num_str = "".join(map(str, pred_list))
        if len(num_str) == 4:
            predictions.add(num_str)

    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    if latest_number in predictions:
        predictions.remove(latest_number)

    return list(predictions)[:limit]


def aggregate_predictions(predictions_by_model: dict, weights: dict):
    """
    モデルごとの予測リストと重みを受け取り、重み付け集計してスコア付きのDataFrameを返す。

    Args:
        predictions_by_model (dict): モデル名をキー、予測文字列のリストを値とする辞書。
                                     例: {'basic_stats': ['1111', '2222'], ...}
        weights (dict): モデル名をキー、重み（数値）を値とする辞書。
                        例: {'basic_stats': 1.5, ...}

    Returns:
        pd.DataFrame: 'prediction'と'score'列を持つ、スコア順にソートされたDataFrame。
    """
    scores = Counter()
    for model_name, predictions in predictions_by_model.items():
        weight = weights.get(model_name, 1) # 重みがなければデフォルトで1
        for pred in predictions:
            scores[pred] += weight

    if not scores:
        return pd.DataFrame({'prediction': [], 'score': []})

    # DataFrameを作成
    df = pd.DataFrame(scores.items(), columns=['prediction', 'score'])
    
    # スコアの高い順にソート
    df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    return df


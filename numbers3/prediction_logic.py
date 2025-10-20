import pandas as pd
import numpy as np
from collections import Counter

# --- 1. 基本統計モデル ---
def predict_from_basic_stats(df: pd.DataFrame, limit: int = 5):
    """
    基本的な統計情報（出現頻度、最新の数字）に基づいて予測を生成する。
    改善版：時系列重み付け、多様性向上。
    """
    # 最近のデータにより高い重みを付与（指数減衰）
    n = len(df)
    weights = np.exp(np.linspace(-2, 0, n))  # 最新に近いほど重みが大きい
    weights = weights / weights.sum()
    
    # 各桁の重み付き出現頻度を計算
    def weighted_counter(series, weights):
        counter = Counter()
        for val, w in zip(series, weights):
            counter[val] += w
        return counter
    
    first_counts = weighted_counter(df['d1'], weights)
    second_counts = weighted_counter(df['d2'], weights)
    third_counts = weighted_counter(df['d3'], weights)

    # 最新の抽選番号
    latest_draw = df.iloc[-1]
    
    # 多様性を確保するため、確率的サンプリングを使用
    predictions = set()
    attempts = 0
    max_attempts = limit * 100
    
    while len(predictions) < limit and attempts < max_attempts:
        attempts += 1
        prediction = ""
        
        # 各桁を確率的に選択（重み付き頻度に基づく）
        for counts in [first_counts, second_counts, third_counts]:
            total = sum(counts.values())
            probs = {k: v/total for k, v in counts.items()}
            # 上位候補から確率的に選択（多様性確保）
            candidates = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:7]
            if candidates:
                digit = np.random.choice(
                    [c[0] for c in candidates],
                    p=[c[1]/sum(c[1] for c in candidates) for c in candidates]
                )
                prediction += str(digit)
            else:
                prediction += str(np.random.randint(0, 10))
        
        # 最新の当選番号を除外
        latest_number = "".join(map(str, latest_draw[['d1', 'd2', 'd3']].values))
        if prediction != latest_number:
            predictions.add(prediction)
    
    return list(predictions)[:limit]


def calculate_heuristic_score(num_str: str, sum_mode: float, even_count_mode: float, pair_counts: Counter):
    """指定された番号文字列のヒューリスティックスコアを計算する"""
    n1, n2, n3 = [int(d) for d in num_str]
    
    current_sum = n1 + n2 + n3
    current_even_count = sum(x % 2 == 0 for x in [n1, n2, n3])
    
    score = 0
    # 合計値の近さ
    score += 1 / (1 + abs(current_sum - sum_mode))
    # 偶数・奇数のバランス
    score += 1 / (1 + abs(current_even_count - even_count_mode))
    # ペアの頻度
    score += pair_counts[tuple(sorted((n1, n2)))]
    score += pair_counts[tuple(sorted((n2, n3)))]
    
    return score


# --- 2. 高度なヒューリスティックモデル ---
def predict_from_advanced_heuristics(df: pd.DataFrame, limit: int = 5):
    """
    高度なヒューリスティック（合計値、偶数奇数、ペアの頻度）に基づいて予測を生成する。
    改善版：時系列重み付け、最近のトレンドを反映。
    """
    # コピーして安全に列を追加（SettingWithCopyWarning 回避）
    df = df.copy()
    df['sum'] = df[['d1', 'd2', 'd3']].sum(axis=1)
    df['even_count'] = df[['d1', 'd2', 'd3']].apply(lambda row: sum(x % 2 == 0 for x in row), axis=1)
    
    # 最近のデータに重みを付けてペア頻度を計算
    n = len(df)
    weights = np.exp(np.linspace(-1.5, 0, n))  # 時系列重み
    
    pair_counts = Counter()
    for idx, row in df.iterrows():
        w = weights[idx]
        for i in range(2):  # Numbers3は3桁なので2つのペアのみ
            pair_counts[tuple(sorted((row[f'd{i+1}'], row[f'd{i+2}'])))] += w
    
    # 最近100件の統計（トレンド重視）
    recent_df = df.tail(100)
    sum_mode = recent_df['sum'].mode()[0] if not recent_df['sum'].mode().empty else df['sum'].mode()[0]
    even_count_mode = recent_df['even_count'].mode()[0] if not recent_df['even_count'].mode().empty else df['even_count'].mode()[0]
    
    # スコアリング（全組み合わせは重いので、サンプリング戦略を使用）
    scored_numbers = []
    
    # 1. 高スコア候補を効率的に生成（全探索の代わり）
    for _ in range(min(5000, limit * 500)):
        # 合計値を目標に近づける
        target_sum = int(sum_mode + np.random.normal(0, 2))
        target_sum = max(0, min(27, target_sum))  # Numbers3は最大27
        
        # ランダム生成して条件に近いものを選択
        num_str = f"{np.random.randint(0, 1000):03d}"
        score = calculate_heuristic_score(num_str, sum_mode, even_count_mode, pair_counts)
        scored_numbers.append((num_str, score))
    
    # スコア上位を予測とする
    scored_numbers.sort(key=lambda x: x[1], reverse=True)
    
    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    predictions = []
    seen = set()
    for num, _ in scored_numbers:
        if num != latest_number and num not in seen:
            predictions.append(num)
            seen.add(num)
        if len(predictions) == limit:
            break
            
    return predictions


# --- 3. 探索的ヒューリスティックモデル ---
def predict_from_exploratory_heuristics(df: pd.DataFrame, limit: int = 5):
    """
    探索的ヒューリスティックに基づき、統計的な「穴」を狙う予測を生成する。
    合計値が極端に低い/高い組み合わせや、長期間出現していない数字を重視する。
    """
    df = df.copy()
    df['sum'] = df[['d1', 'd2', 'd3']].sum(axis=1)

    # 長期間出現していない数字（コールドナンバー）を特定
    all_digits = pd.concat([df[f'd{i+1}'] for i in range(3)])
    digit_counts = Counter(all_digits)
    cold_digits = [digit for digit, count in digit_counts.items() if count <= np.percentile(list(digit_counts.values()), 25)]
    if not cold_digits:
        cold_digits = [digit_counts.most_common()[-1][0]]

    predictions = set()
    attempts = 0

    # 1. 超低合計値/超高合計値を狙う
    low_sum_target = 6   # e.g., 0-6
    high_sum_target = 21  # e.g., 21-27

    while len(predictions) < limit and attempts < 10000:
        attempts += 1
        pred = np.random.randint(0, 1000)
        num_str = f"{pred:03d}"
        n1, n2, n3 = [int(d) for d in num_str]
        current_sum = sum([n1, n2, n3])

        if np.random.rand() < 0.5:
            if current_sum <= low_sum_target:
                predictions.add(num_str)
        else:
            if current_sum >= high_sum_target:
                predictions.add(num_str)

    # 2. ゼロ頻度ペアとコールドナンバーを組み合わせる
    historical_pairs = set()
    for _, row in df.iterrows():
        for i in range(2):  # Numbers3は2つのペア
            historical_pairs.add(tuple(sorted((row[f'd{i+1}'], row[f'd{i+2}']))))
    
    all_possible_pairs = {tuple(sorted((i, j))) for i in range(10) for j in range(10)}
    zero_freq_pairs = list(all_possible_pairs - historical_pairs)

    if zero_freq_pairs and cold_digits:
        while len(predictions) < limit * 2 and attempts < 20000:
            attempts += 1
            target_pair = list(zero_freq_pairs[np.random.randint(len(zero_freq_pairs))])
            other_digit = np.random.choice(cold_digits, 1)[0]
            pred_list = target_pair + [other_digit]
            np.random.shuffle(pred_list)
            num_str = "".join(map(str, pred_list))
            predictions.add(num_str)

    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    if latest_number in predictions:
        predictions.remove(latest_number)

    return list(predictions)[:limit]


def aggregate_predictions(predictions_by_model: dict, weights: dict):
    """
    モデルごとの予測リストと重みを受け取り、重み付け集計してスコア付きのDataFrameを返す。

    Args:
        predictions_by_model (dict): モデル名をキー、予測文字列のリストを値とする辞書。
                                     例: {'basic_stats': ['111', '222'], ...}
        weights (dict): モデル名をキー、重み（数値）を値とする辞書。
                        例: {'basic_stats': 1.5, ...}

    Returns:
        pd.DataFrame: 'prediction'と'score'列を持つ、スコア順にソートされたDataFrame。
    """
    scores = Counter()
    for model_name, predictions in predictions_by_model.items():
        weight = weights.get(model_name, 1)
        for pred in predictions:
            scores[pred] += weight

    if not scores:
        return pd.DataFrame({'prediction': [], 'score': []})

    df = pd.DataFrame(scores.items(), columns=['prediction', 'score'])
    df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    return df

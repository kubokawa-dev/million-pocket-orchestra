import pandas as pd
import numpy as np
from collections import Counter
import json
import os
# from numbers4.predict_numbers_with_model import predict_top_k as _predict_top_k_model  # 削除されたファイル

# --- 1. predict_numbers.py からのロジック ---
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
    fourth_counts = weighted_counter(df['d4'], weights)

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
        for counts in [first_counts, second_counts, third_counts, fourth_counts]:
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
        latest_number = "".join(map(str, latest_draw[['d1', 'd2', 'd3', 'd4']].values))
        if prediction != latest_number:
            predictions.add(prediction)
    
    return list(predictions)[:limit]

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
    
def calculate_heuristic_score(num_str: str, sum_mode: float, even_count_mode: float, pair_counts: Counter):
    """指定された番号文字列のヒューリスティックスコアを計算する"""
    n1, n2, n3, n4 = [int(d) for d in num_str]
    
    current_sum = n1 + n2 + n3 + n4
    current_even_count = sum(x % 2 == 0 for x in [n1, n2, n3, n4])
    
    score = 0
    # 合計値の近さ
    score += 1 / (1 + abs(current_sum - sum_mode))
    # 偶数・奇数のバランス
    score += 1 / (1 + abs(current_even_count - even_count_mode))
    # ペアの頻度
    score += pair_counts[tuple(sorted((n1, n2)))]
    score += pair_counts[tuple(sorted((n2, n3)))]
    score += pair_counts[tuple(sorted((n3, n4)))]
    
    return score

# --- 2. advanced_predict_numbers4.py からのロジック ---
def predict_from_advanced_heuristics(df: pd.DataFrame, limit: int = 5):
    """
    高度なヒューリスティック（合計値、偶数奇数、ペアの頻度）に基づいて予測を生成する。
    改善版：時系列重み付け、最近のトレンドを反映。
    """
    # コピーして安全に列を追加（SettingWithCopyWarning 回避）
    df = df.copy()
    df['sum'] = df[['d1', 'd2', 'd3', 'd4']].sum(axis=1)
    df['even_count'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda row: sum(x % 2 == 0 for x in row), axis=1)
    
    # 最近のデータに重みを付けてペア頻度を計算
    n = len(df)
    weights = np.exp(np.linspace(-1.5, 0, n))  # 時系列重み
    
    pair_counts = Counter()
    for i, (idx, row) in enumerate(df.iterrows()):
        w = weights[i]  # インデックスではなく位置を使用
        for j in range(3):
            pair_counts[tuple(sorted((row[f'd{j+1}'], row[f'd{j+2}'])))] += w
    
    # 最近100件の統計（トレンド重視）
    recent_df = df.tail(100)
    sum_mode = recent_df['sum'].mode()[0] if not recent_df['sum'].mode().empty else df['sum'].mode()[0]
    even_count_mode = recent_df['even_count'].mode()[0] if not recent_df['even_count'].mode().empty else df['even_count'].mode()[0]
    
    # スコアリング（全組み合わせは重いので、サンプリング戦略を使用）
    scored_numbers = []
    
    # 1. 高スコア候補を効率的に生成（全探索の代わり）
    for _ in range(min(5000, limit * 500)):
        # 合計値を目標に近づける
        target_sum = int(sum_mode + np.random.normal(0, 3))
        target_sum = max(0, min(36, target_sum))
        
        # 偶奇バランスを目標に近づける
        target_even = int(even_count_mode)
        
        # ランダム生成して条件に近いものを選択
        num_str = f"{np.random.randint(0, 10000):04d}"
        score = calculate_heuristic_score(num_str, sum_mode, even_count_mode, pair_counts)
        scored_numbers.append((num_str, score))
    
    # スコア上位を予測とする
    scored_numbers.sort(key=lambda x: x[1], reverse=True)
    
    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    predictions = []
    seen = set()
    for num, _ in scored_numbers:
        if num != latest_number and num not in seen:
            predictions.append(num)
            seen.add(num)
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


# --- 3b. Wrapper for new ML model API expected by ensemble ---
def predict_with_new_ml_model(df: pd.DataFrame, limit: int = 12):
    """
    新しいMLモデルの予測を返すための互換ラッパー関数。
    削除されたファイルの代わりに、基本的な統計予測を返す。
    """
    try:
        # 削除されたファイルの代わりに、基本的な統計予測を使用
        return predict_from_basic_stats(df, limit)
    except Exception:
        return []

# --- 4. Exploratory Prediction (New) ---
def predict_from_extreme_patterns(df: pd.DataFrame, limit: int = 10):
    """
    極端なパターン（超低合計値、超高合計値、特殊パターン）を体系的に生成する。
    0100のような極端に低い合計値のパターンをカバーする。
    改善版：合計値0-2を明示的に列挙し、確実にカバーする。
    """
    predictions = set()
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 1a. 超極端な低合計値パターン（合計0-2）を明示的に列挙
    # これにより0100のようなパターンを確実にカバー
    for d1 in range(3):  # 0, 1, 2
        for d2 in range(3):
            for d3 in range(3):
                for d4 in range(3):
                    if d1 + d2 + d3 + d4 <= 2:
                        num_str = f"{d1}{d2}{d3}{d4}"
                        if num_str != latest_number:
                            predictions.add(num_str)
    
    # 1b. 低合計値パターン（合計3-5）をランダムサンプリング
    for target_sum in range(3, 6):
        attempts = 0
        while attempts < 3000:
            attempts += 1
            # ランダムに4桁を生成
            digits = []
            remaining = target_sum
            for i in range(3):
                max_val = min(remaining, 9)
                d = np.random.randint(0, max_val + 1)
                digits.append(d)
                remaining -= d
            # 最後の桁は残りの値
            if 0 <= remaining <= 9:
                digits.append(remaining)
                num_str = "".join(map(str, digits))
                if num_str != latest_number:
                    predictions.add(num_str)
            if len(predictions) >= limit * 0.6:  # 60%を低合計値に割り当て
                break
    
    # 2. 超高合計値パターン（合計31-36）
    for target_sum in range(31, 37):
        attempts = 0
        while attempts < 3000:
            attempts += 1
            digits = []
            remaining = target_sum
            for i in range(3):
                min_val = max(0, remaining - 9 * (3 - i))
                max_val = min(remaining, 9)
                if min_val <= max_val:
                    d = np.random.randint(min_val, max_val + 1)
                    digits.append(d)
                    remaining -= d
                else:
                    break
            else:
                if 0 <= remaining <= 9:
                    digits.append(remaining)
                    num_str = "".join(map(str, digits))
                    if num_str != latest_number:
                        predictions.add(num_str)
            if len(predictions) >= limit:
                break
    
    # 3. 特殊パターン: 同一数字の繰り返し
    special_patterns = set()
    for digit in range(10):
        # AAAA パターン
        num_str = str(digit) * 4
        if num_str != latest_number:
            special_patterns.add(num_str)
        
        # AAAB, AABA, ABAA, BAAA パターン
        for other in range(10):
            if other != digit:
                for pos in range(4):
                    num_list = [digit] * 4
                    num_list[pos] = other
                    num_str = "".join(map(str, num_list))
                    if num_str != latest_number:
                        special_patterns.add(num_str)
    
    # 合計0-2のパターンを優先的に返す（さらに合計値でソート）
    very_low_sum = sorted([p for p in predictions if sum(int(d) for d in p) <= 2], 
                          key=lambda x: sum(int(d) for d in x))
    other_predictions = [p for p in predictions if sum(int(d) for d in p) > 2]
    special_list = list(special_patterns)
    
    # 結合: 超低合計値（合計値順） + その他 + 特殊パターン
    # 確実に合計0,1,2のパターンすべてが含まれるようにする
    final_predictions = very_low_sum + other_predictions + special_list
    
    return final_predictions[:limit]


def predict_from_exploratory_heuristics(df: pd.DataFrame, limit: int = 20):
    """
    探索的ヒューリスティックに基づき、統計的な「穴」を狙う予測を生成する。
    合計値が極端に低い/高い組み合わせや、長期間出現していない数字を重視する。
    改善版：予測数を大幅に増加（5→20）
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

    # 2. ゼロ頻度ペアとコールドナンバーを組み合わせる (Refined)
    # 過去の全ペアを計算
    historical_pairs = set()
    for _, row in df.iterrows():
        for i in range(3):
            historical_pairs.add(tuple(sorted((row[f'd{i+1}'], row[f'd{i+2}']))) )
    
    # ゼロ頻度のペアを特定
    all_possible_pairs = {tuple(sorted((i, j))) for i in range(10) for j in range(10)}
    zero_freq_pairs = list(all_possible_pairs - historical_pairs)

    if zero_freq_pairs and cold_digits:
        while len(predictions) < limit * 2 and attempts < 40000:
            attempts += 1
            # ゼロ頻度ペアをランダムに1つ選択
            target_pair = list(zero_freq_pairs[np.random.randint(len(zero_freq_pairs))])
            # 残りの2桁をコールドナンバーから選択
            other_digits = np.random.choice(cold_digits, 2, replace=True).tolist()
            # 4桁のリストを作成してシャッフル
            pred_list = target_pair + other_digits
            np.random.shuffle(pred_list)
            num_str = "".join(map(str, pred_list))
            predictions.add(num_str)


    # 最新の当選番号を除外
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    if latest_number in predictions:
        predictions.remove(latest_number)
    
    # 予測数が不足している場合は、低頻度の数字を含むパターンを追加
    if len(predictions) < limit:
        all_digits = pd.concat([df[f'd{i+1}'] for i in range(4)])
        digit_counts = Counter(all_digits)
        cold_digits = [d for d, _ in digit_counts.most_common()[-5:]]  # 最も出現頻度が低い5つ
        
        attempts = 0
        while len(predictions) < limit and attempts < 10000:
            attempts += 1
            # コールドナンバーから2つ以上選ぶ
            num_cold = np.random.randint(2, 5)
            cold_selected = np.random.choice(cold_digits, num_cold, replace=True)
            other_selected = np.random.choice(10, 4 - num_cold, replace=True)
            all_digits_list = np.concatenate([cold_selected, other_selected])
            np.random.shuffle(all_digits_list)
            num_str = "".join(map(str, all_digits_list))
            if num_str != latest_number:
                predictions.add(num_str)

    return list(predictions)[:limit]


def aggregate_predictions(predictions_by_model: dict, weights: dict, normalize_scores: bool = True):
    """
    モデルごとの予測リストと重みを受け取り、重み付け集計してスコア付きのDataFrameを返す。

    Args:
        predictions_by_model (dict): モデル名をキー、予測文字列のリストを値とする辞書。
                                     例: {'basic_stats': ['1111', '2222'], ...}
        weights (dict): モデル名をキー、重み（数値）を値とする辞書。
                        例: {'basic_stats': 1.5, ...}
        normalize_scores (bool): 各モデルのスコアを0-1に正規化するか（デフォルト: True）

    Returns:
        pd.DataFrame: 'prediction'と'score'列を持つ、スコア順にソートされたDataFrame。
    """
    # 各モデルの予測にランクベースのスコアを付与（正規化）
    model_scores = {}
    
    for model_name, predictions in predictions_by_model.items():
        weight = weights.get(model_name, 1)
        
        if normalize_scores and predictions:
            # ランクベーススコア：1位=1.0, 最下位=0.0
            n = len(predictions)
            for rank, pred in enumerate(predictions):
                # 線形減衰: 1位=1.0, 2位=0.99, ..., 最下位=0.0
                normalized_score = (n - rank) / n
                
                if pred not in model_scores:
                    model_scores[pred] = 0
                model_scores[pred] += normalized_score * weight
        else:
            # 正規化なし（従来の方法）
            for pred in predictions:
                if pred not in model_scores:
                    model_scores[pred] = 0
                model_scores[pred] += weight

    if not model_scores:
        return pd.DataFrame({'prediction': [], 'score': []})

    # DataFrameを作成
    df = pd.DataFrame(model_scores.items(), columns=['prediction', 'score'])
    
    # スコアの高い順にソート
    df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    return df


def apply_diversity_penalty(df: pd.DataFrame, penalty_strength: float = 0.3, similarity_threshold: int = 3):
    """
    多様性ペナルティを適用：類似した候補のスコアを下げる（ナンバーズ4用）
    
    Args:
        df: 予測結果のDataFrame（'prediction'と'score'列を持つ）
        penalty_strength: ペナルティの強さ（0.0-1.0、デフォルト: 0.3）
        similarity_threshold: 類似と判定する共通桁数（デフォルト: 3）
    
    Returns:
        多様性ペナルティ適用後のDataFrame
    """
    if df.empty or len(df) <= 1:
        return df
    
    df = df.copy()
    df['adjusted_score'] = df['score'].copy()
    
    # 上位から順に処理
    for i in range(len(df)):
        current_pred = df.iloc[i]['prediction']
        current_digits = set(current_pred)
        
        # それより下位の候補と比較
        for j in range(i + 1, len(df)):
            other_pred = df.iloc[j]['prediction']
            other_digits = set(other_pred)
            
            # 共通する桁数を計算
            common_digits = len(current_digits & other_digits)
            
            # 類似度が閾値以上ならペナルティ
            if common_digits >= similarity_threshold:
                penalty = penalty_strength * (common_digits / 4.0)  # 4桁中の共通割合
                df.loc[j, 'adjusted_score'] *= (1 - penalty)
    
    # 調整後のスコアで再ソート
    df = df.sort_values(by='adjusted_score', ascending=False).reset_index(drop=True)
    df['score'] = df['adjusted_score']  # スコアを更新
    df = df.drop(columns=['adjusted_score'])
    
    return df


import pandas as pd
import numpy as np
from collections import Counter
import json
import os
from itertools import product
from numbers4.prediction_logic_lgbm import (
    predict_from_lightgbm,  # LightGBM
    train_and_predict_lgbm_with_probs,
    DEFAULT_TEMPERATURE,
)
from numbers4.learn_from_predictions import (
    ensure_state_schema,
    rank_numbers_from_state,
)
# from numbers4.predict_numbers_with_model import predict_top_k as _predict_top_k_model  # 削除されたファイル


# --- ML近傍探索モデル（v11.1 NEW!）---
def predict_from_ml_neighborhood_search_n4(df: pd.DataFrame, limit: int = 200):
    """
    ML近傍探索モデル：LightGBMの確率分布を使って、近傍空間を探索
    
    背景:
    - 第6895回で「2827」が当選したが、前回予測では82～92位（ML近傍探索）だった
    - メイン予測では捉えきれなかったが、ML近傍探索では見つかっていた
    - → ML近傍探索を独立したモデルとして重み付けを強化
    
    Args:
        df: 全抽選データ
        limit: 生成する予測数
    
    Returns:
        予測番号のリスト
    """
    try:
        # LightGBMで各桁の確率分布を取得
        _, preds_probs = predict_from_lightgbm_with_probs(df, limit=20)
        
        if not preds_probs or not all(k in preds_probs for k in ['d1', 'd2', 'd3', 'd4']):
            return []
        
        # 各桁の確率分布から上位候補を取得 (正規化して安全に)
        topk = 5
        top_digits = {}
        normalized_probs = {}
        for pos, key in enumerate(['d1', 'd2', 'd3', 'd4']):
            probs = np.array(preds_probs[key], dtype=np.float64)
            # 確率の正規化 (合計が1になるように)
            probs = np.clip(probs, 0, None)  # 負の値を0に
            prob_sum = probs.sum()
            if prob_sum > 0:
                probs = probs / prob_sum
            else:
                probs = np.ones(10) / 10  # フォールバック: 均等分布
            normalized_probs[key] = probs
            top_digits[pos] = [int(i) for i in probs.argsort()[::-1][:topk]]
        
        # 近傍探索用の候補生成
        candidates = {}
        
        # 確率分布からサンプリング (多様性重視)
        rng = np.random.default_rng(42)  # 固定seed
        keep_prob = 0.60  # 高確率数字を保持する確率 (やや低めで多様性確保)
        
        for _ in range(limit * 5):
            digits = []
            for pos, key in enumerate(['d1', 'd2', 'd3', 'd4']):
                if rng.random() < keep_prob:
                    # 高確率数字から選択
                    digits.append(int(rng.choice(top_digits[pos])))
                else:
                    # 正規化された確率分布からサンプリング
                    digits.append(int(rng.choice(10, p=normalized_probs[key])))
            
            cand = "".join(map(str, digits))
            if cand not in candidates:
                candidates[cand] = True
                if len(candidates) >= limit:
                    break
        
        return list(candidates.keys())[:limit]
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"⚠️ ML近傍探索モデルエラー: {e}")
        return []

def predict_from_lightgbm_with_probs(
    df: pd.DataFrame,
    limit: int = 15,
    temperature: float = DEFAULT_TEMPERATURE
):
    """
    LightGBM予測 + 各桁確率分布を返す（類似候補生成などで利用）。

    Returns:
        (predictions: List[str], preds_probs: Dict[str, np.ndarray])
    """
    try:
        df_local = df.copy()
        if 'draw_date' not in df_local.columns and 'date' in df_local.columns:
            df_local['draw_date'] = df_local['date']
        return train_and_predict_lgbm_with_probs(df_local, limit=limit, temperature=temperature)
    except Exception as e:
        print(f"[LightGBM] Error (with_probs): {e}")
        import traceback
        traceback.print_exc()
        return [], {}

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


def predict_from_model_state_v2(
    limit: int = 120,
    model_state_path: str | None = None,
):
    """
    model_state.jsonの桁間相関（pair_probs）を使ったチェーンモデル予測。
    limit件を確率順で返す。
    """
    try:
        if model_state_path is None:
            model_state_path = os.path.join(os.path.dirname(__file__), 'model_state.json')
        if not os.path.exists(model_state_path):
            return []
        with open(model_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        state = ensure_state_schema(state)
        ranked = rank_numbers_from_state(state, top_n=limit * 2)
        preds = []
        seen = set()
        for num, _score in ranked:
            if num not in seen:
                preds.append(num)
                seen.add(num)
            if len(preds) >= limit:
                break
        return preds
    except Exception as e:
        print(f"[state_v2] failed to load model_state: {e}")
        return []

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
    
    v10.2改善: 
    - 完全ランダムな候補を25%含めて多様性を大幅UP
    - ボックスユニークを考慮した生成
    """
    import random
    
    df = df.copy()
    df['sum'] = df[['d1', 'd2', 'd3', 'd4']].sum(axis=1)

    # 長期間出現していない数字（コールドナンバー）を特定
    all_digits = pd.concat([df[f'd{i+1}'] for i in range(4)])
    digit_counts = Counter(all_digits)
    cold_digits = [digit for digit, count in digit_counts.items() if count <= np.percentile(list(digit_counts.values()), 25)]
    if not cold_digits:
        cold_digits = [digit_counts.most_common()[-1][0]]

    predictions = set()
    seen_boxes = set()  # ボックスユニーク用
    attempts = 0

    # 最新の当選番号
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))

    # v10.2: 完全ランダムな候補を最初に追加（多様性確保の要）
    random_count = max(5, limit // 4)  # 25%はランダム
    random_attempts = 0
    while len(predictions) < random_count and random_attempts < 1000:
        random_attempts += 1
        random_num = f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"
        box_id = "".join(sorted(random_num))
        if random_num != latest_number and box_id not in seen_boxes:
            predictions.add(random_num)
            seen_boxes.add(box_id)

    # 1. 超低合計値/超高合計値を狙う
    low_sum_target = 9
    high_sum_target = 28

    while len(predictions) < limit and attempts < 20000:
        attempts += 1
        pred = np.random.randint(0, 10000)
        num_str = f"{pred:04d}"
        box_id = "".join(sorted(num_str))
        
        # ボックスが既出の場合はスキップ
        if box_id in seen_boxes:
            continue
            
        n1, n2, n3, n4 = [int(d) for d in num_str]
        current_sum = sum([n1, n2, n3, n4])

        if np.random.rand() < 0.5:
            if current_sum <= low_sum_target:
                predictions.add(num_str)
                seen_boxes.add(box_id)
        else:
            if current_sum >= high_sum_target:
                predictions.add(num_str)
                seen_boxes.add(box_id)

    # 2. ゼロ頻度ペアとコールドナンバーを組み合わせる
    historical_pairs = set()
    for _, row in df.iterrows():
        for i in range(3):
            historical_pairs.add(tuple(sorted((row[f'd{i+1}'], row[f'd{i+2}']))))
    
    all_possible_pairs = {tuple(sorted((i, j))) for i in range(10) for j in range(10)}
    zero_freq_pairs = list(all_possible_pairs - historical_pairs)

    if zero_freq_pairs and cold_digits:
        while len(predictions) < limit * 2 and attempts < 40000:
            attempts += 1
            target_pair = list(zero_freq_pairs[np.random.randint(len(zero_freq_pairs))])
            other_digits = np.random.choice(cold_digits, 2, replace=True).tolist()
            pred_list = target_pair + other_digits
            np.random.shuffle(pred_list)
            num_str = "".join(map(str, pred_list))
            box_id = "".join(sorted(num_str))
            
            if num_str != latest_number and box_id not in seen_boxes:
                predictions.add(num_str)
                seen_boxes.add(box_id)

    # 予測数が不足している場合は、低頻度の数字を含むパターンを追加
    if len(predictions) < limit:
        all_digits = pd.concat([df[f'd{i+1}'] for i in range(4)])
        digit_counts = Counter(all_digits)
        cold_digits = [d for d, _ in digit_counts.most_common()[-5:]]
        
        attempts = 0
        while len(predictions) < limit and attempts < 10000:
            attempts += 1
            num_cold = np.random.randint(2, 5)
            cold_selected = np.random.choice(cold_digits, num_cold, replace=True)
            other_selected = np.random.choice(10, 4 - num_cold, replace=True)
            all_digits_list = np.concatenate([cold_selected, other_selected])
            np.random.shuffle(all_digits_list)
            num_str = "".join(map(str, all_digits_list))
            box_id = "".join(sorted(num_str))
            
            if num_str != latest_number and box_id not in seen_boxes:
                predictions.add(num_str)
                seen_boxes.add(box_id)

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


def apply_diversity_penalty(df: pd.DataFrame, penalty_strength: float = 0.5, similarity_threshold: int = 2):
    """
    多様性ペナルティを適用：ボックス的に類似した候補のスコアを大幅に下げる（ナンバーズ4用）
    
    v10.2改善: ボックス（順不同）での完全一致に強いペナルティ
    - 同じボックス（数字の組み合わせ）が既に上位にある場合: 90%減
    - 3桁以上の数字が共通する場合: 段階的ペナルティ
    
    Args:
        df: 予測結果のDataFrame（'prediction'と'score'列を持つ）
        penalty_strength: ペナルティの強さ（0.0-1.0、デフォルト: 0.5）
        similarity_threshold: 類似と判定する共通桁数（デフォルト: 2）
    
    Returns:
        多様性ペナルティ適用後のDataFrame
    """
    if df.empty or len(df) <= 1:
        return df
    
    df = df.copy()
    df['adjusted_score'] = df['score'].copy()
    
    seen_boxes = set()  # 既出のボックスID（ソート済み数字）を記録
    
    # 上位から順に処理
    for i in range(len(df)):
        current_pred = str(df.iloc[i]['prediction'])
        current_box = "".join(sorted(current_pred))  # ボックスID（数字をソート）
        
        # 同じボックスが既に上位にある場合、大幅ペナルティ（90%減）
        if current_box in seen_boxes:
            df.loc[df.index[i], 'adjusted_score'] *= 0.1
        else:
            seen_boxes.add(current_box)
            
            # 似たボックス（共通数字が多い）にもペナルティを適用
            current_digits = set(current_pred)
            for j in range(i + 1, len(df)):
                other_pred = str(df.iloc[j]['prediction'])
                other_digits = set(other_pred)
                
                # 共通する数字の種類を計算
                common_digits = len(current_digits & other_digits)
                
                # 類似度が閾値以上ならペナルティ
                if common_digits >= similarity_threshold:
                    penalty = penalty_strength * (common_digits / 4.0)
                    df.loc[df.index[j], 'adjusted_score'] *= (1 - penalty)
    
    # 調整後のスコアで再ソート
    df = df.sort_values(by='adjusted_score', ascending=False).reset_index(drop=True)
    df['score'] = df['adjusted_score']
    df = df.drop(columns=['adjusted_score'])
    
    return df


# --- v10.0 改善モデル（ナンバーズ3の成功を適用） ---

def predict_from_digit_repetition_model_n4(df: pd.DataFrame, limit: int = 300):
    """
    数字再出現モデル（ナンバーズ4版）
    同じ数字が複数桁に出現するパターンを重視
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    recent_30 = df.tail(30)
    all_digits = []
    for _, row in recent_30.iterrows():
        all_digits.extend([row['d1'], row['d2'], row['d3'], row['d4']])
    
    digit_freq = Counter(all_digits)
    top_digits = [d for d, _ in digit_freq.most_common(8)]
    
    # 同じ数字が2回出現するパターン
    for digit in top_digits:
        for third in range(10):
            for fourth in range(10):
                if not (third == digit and fourth == digit):
                    patterns = [
                        f"{digit}{digit}{third}{fourth}",
                        f"{digit}{third}{digit}{fourth}",
                        f"{digit}{third}{fourth}{digit}",
                        f"{third}{digit}{digit}{fourth}",
                        f"{third}{digit}{fourth}{digit}",
                        f"{third}{fourth}{digit}{digit}"
                    ]
                    for num_str in patterns:
                        if num_str != latest_number:
                            score = digit_freq.get(digit, 0) * 12
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
    
    # 1-2桁目を継続
    for d3 in range(10):
        for d4 in range(10):
            num_str = f"{latest_digits[0]}{latest_digits[1]}{d3}{d4}"
            if num_str != latest_number:
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 22.0
    
    # 3-4桁目を継続
    for d1 in range(10):
        for d2 in range(10):
            num_str = f"{d1}{d2}{latest_digits[2]}{latest_digits[3]}"
            if num_str != latest_number:
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 22.0
    
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
    
    large_deltas = [-5, -4, -3, 3, 4, 5]
    
    for delta1 in large_deltas + [0]:
        for delta2 in large_deltas + [0]:
            for delta3 in large_deltas + [0]:
                for delta4 in large_deltas + [0]:
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
    
    recent_5 = df.tail(5)
    recent_10 = df.tail(10)
    recent_20 = df.tail(20)
    
    def get_top_digits(df_subset, position, top_n=7):
        freq = Counter(df_subset[f'd{position+1}'])
        return [d for d, _ in freq.most_common(top_n)]
    
    top_digits_5 = [get_top_digits(recent_5, i, 5) for i in range(4)]
    top_digits_10 = [get_top_digits(recent_10, i, 6) for i in range(4)]
    top_digits_20 = [get_top_digits(recent_20, i, 7) for i in range(4)]
    
    all_top_digits = []
    for i in range(4):
        combined = list(set(top_digits_5[i] + top_digits_10[i] + top_digits_20[i]))
        all_top_digits.append(combined[:7])
    
    for d1, d2, d3, d4 in product(all_top_digits[0], all_top_digits[1], all_top_digits[2], all_top_digits[3]):
        num_str = f"{d1}{d2}{d3}{d4}"
        if num_str != latest_number:
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


# --- v10.3 過去パターン学習モデル（直近依存からの脱却！） ---

def apply_temperature_scaling(probs: dict, temperature: float = 1.5, min_prob: float = 0.05) -> dict:
    """
    確率分布に温度スケーリングと最低確率閾値を適用
    
    v10.4改善: 過度な偏りを軽減し、すべての数字に最低限のチャンスを与える
    
    Args:
        probs: 確率分布の辞書 {digit: probability}
        temperature: 温度パラメータ（>1で分布を平滑化、<1で尖らせる）
        min_prob: 最低確率（すべての数字がこの確率以上を持つ）
    
    Returns:
        調整後の確率分布
    """
    import math
    
    # 全ての数字が存在することを保証
    adjusted = {}
    for d in range(10):
        adjusted[d] = probs.get(d, 0.0)
    
    # 温度スケーリング（log-softmax的な変換）
    if temperature != 1.0:
        # 確率をlogオッズに変換し、温度で割って再正規化
        epsilon = 1e-10
        for d in adjusted:
            adjusted[d] = max(adjusted[d], epsilon)
        
        # べき乗で温度調整（確率^(1/T)）
        for d in adjusted:
            adjusted[d] = adjusted[d] ** (1.0 / temperature)
    
    # 最低確率を保証
    for d in adjusted:
        adjusted[d] = max(adjusted[d], min_prob)
    
    # 正規化
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {d: p / total for d, p in adjusted.items()}
    
    return adjusted


def predict_from_transition_probability_n4(df: pd.DataFrame, limit: int = 200):
    """
    遷移確率モデル（ナンバーズ4版）v10.4
    
    過去の全履歴から「前回の数字→次回の数字」の遷移確率を学習
    直近ではなく全データを使うことで、短期的な偏りを排除
    
    v10.4改善:
    - 温度スケーリングで過度な偏りを軽減
    - 最低確率閾値で稀な遷移パターンもカバー
    
    例: 1桁目が「2」だった次の回、1桁目は何が出やすい？→全履歴から学習
    """
    from collections import defaultdict
    import random
    
    predictions_dict = {}
    latest = df.iloc[-1]
    latest_digits = [latest['d1'], latest['d2'], latest['d3'], latest['d4']]
    latest_number = "".join(map(str, latest_digits))
    
    # 各桁の遷移確率を計算（全履歴から）
    transition_probs = []
    for pos in range(4):
        trans = defaultdict(lambda: defaultdict(int))
        col = f'd{pos+1}'
        for i in range(1, len(df)):
            prev_digit = df.iloc[i-1][col]
            curr_digit = df.iloc[i][col]
            trans[prev_digit][curr_digit] += 1
        
        # 正規化して確率に（温度スケーリング適用）
        prob_dict = {}
        for prev_d, next_counts in trans.items():
            total = sum(next_counts.values())
            raw_probs = {d: c/total for d, c in next_counts.items()}
            # v10.4: 温度スケーリングと最低確率を適用
            prob_dict[prev_d] = apply_temperature_scaling(raw_probs, temperature=1.5, min_prob=0.03)
        transition_probs.append(prob_dict)
    
    # 遷移確率に基づいて予測を生成
    seen_boxes = set()
    attempts = 0
    while len(predictions_dict) < limit and attempts < limit * 50:
        attempts += 1
        new_digits = []
        score = 1.0
        
        for pos in range(4):
            prev_d = latest_digits[pos]
            probs = transition_probs[pos].get(prev_d, {})
            
            if probs:
                # 確率に基づいてサンプリング
                digits = list(probs.keys())
                weights = list(probs.values())
                chosen = random.choices(digits, weights=weights, k=1)[0]
                new_digits.append(chosen)
                score *= probs.get(chosen, 0.1)
            else:
                # データがない場合はランダム（最低確率適用）
                new_digits.append(random.randint(0, 9))
                score *= 0.1
        
        num_str = "".join(map(str, new_digits))
        box_id = "".join(sorted(num_str))
        
        if num_str != latest_number and box_id not in seen_boxes:
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score * 100
            seen_boxes.add(box_id)
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_global_frequency_n4(df: pd.DataFrame, limit: int = 150):
    """
    全体頻度モデル（ナンバーズ4版）v10.7
    
    全履歴から各桁の出現頻度を計算（直近バイアスなし）
    長期的な統計パターンを反映し、直近の偏りに左右されない予測を生成
    
    v10.7改善:
    - 温度スケーリングをさらに強化（1.3→1.5）
    - 最低確率を引き上げ（0.05→0.07）
    - 均等分布に近づけて多様性を確保
    - 「理論的には全数字が10%ずつ」に近い分布を目指す
    """
    import random
    
    predictions = set()
    seen_boxes = set()
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # 全履歴から各桁の出現確率を計算（温度スケーリング適用）
    digit_probs = []
    for pos in range(4):
        col = f'd{pos+1}'
        freq = Counter(df[col])
        total = sum(freq.values())
        raw_probs = {d: freq.get(d, 0) / total for d in range(10)}
        # v10.7: 温度スケーリングと最低確率を強化
        adjusted_probs = apply_temperature_scaling(raw_probs, temperature=1.5, min_prob=0.07)
        digit_probs.append(adjusted_probs)
    
    # === 戦略1: 全体確率に基づいて予測を生成 ===
    attempts = 0
    while len(predictions) < limit * 0.7 and attempts < limit * 50:
        attempts += 1
        new_digits = []
        
        for pos in range(4):
            probs = digit_probs[pos]
            digits = list(probs.keys())
            weights = list(probs.values())
            chosen = random.choices(digits, weights=weights, k=1)[0]
            new_digits.append(chosen)
        
        num_str = "".join(map(str, new_digits))
        box_id = "".join(sorted(num_str))
        
        if num_str != latest_number and box_id not in seen_boxes:
            predictions.add(num_str)
            seen_boxes.add(box_id)
    
    # === 戦略2: 完全均等分布からも生成（多様性確保） ===
    # 理論的には各数字が10%ずつ出るはずなので、均等分布も混ぜる
    attempts = 0
    while len(predictions) < limit and attempts < limit * 30:
        attempts += 1
        new_digits = [random.randint(0, 9) for _ in range(4)]
        
        num_str = "".join(map(str, new_digits))
        box_id = "".join(sorted(num_str))
        
        if num_str != latest_number and box_id not in seen_boxes:
            predictions.add(num_str)
            seen_boxes.add(box_id)
    
    return list(predictions)[:limit]


def predict_from_box_pattern_analysis_n4(df: pd.DataFrame, limit: int = 100):
    """
    ボックスパターン分析モデル（ナンバーズ4版）v10.5.1
    
    ボックス/セット狙いに特化した予測モデル
    - 頻出ペア（隣接2桁の組み合わせ）を重視
    - ABCD型・AABC型・AABB型をバランスよくカバー
    - 過去リピートボックスを含める
    """
    import random
    from itertools import combinations
    
    predictions_dict = {}  # {box_id: score}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    latest_box = "".join(sorted(latest_number))
    
    # === 1. ペア分析（頻出する2桁の組み合わせ） ===
    recent = df.tail(50)
    pair_freq = Counter()
    for _, row in recent.iterrows():
        num = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        pair_freq[tuple(sorted([num[0], num[1]]))] += 1
        pair_freq[tuple(sorted([num[1], num[2]]))] += 1
        pair_freq[tuple(sorted([num[2], num[3]]))] += 1
    
    top_pairs = [pair for pair, _ in pair_freq.most_common(15)]
    
    # === 2. 頻出数字を取得 ===
    all_digits = []
    for _, row in recent.iterrows():
        all_digits.extend([str(row['d1']), str(row['d2']), str(row['d3']), str(row['d4'])])
    digit_freq = Counter(all_digits)
    hot_digits = [d for d, _ in digit_freq.most_common(8)]
    
    # === 3. ABCD型ボックスを生成（頻出ペア + 頻出数字） ===
    for pair in top_pairs:
        pair_score = pair_freq[pair]
        remaining_candidates = [d for d in hot_digits if d not in pair]
        
        for combo in combinations(remaining_candidates, 2):
            box_digits = list(pair) + list(combo)
            box_id = "".join(sorted(box_digits))
            
            if box_id == latest_box:
                continue
            
            score = pair_score * 5
            for d in box_digits:
                score += digit_freq.get(d, 0)
            
            if len(set(box_digits)) == 4:
                score *= 1.3  # ABCD型ボーナス
            
            predictions_dict[box_id] = predictions_dict.get(box_id, 0) + score
    
    # === 4. AABC型ボックスを生成（頻出数字が2回出現） ===
    for d in hot_digits[:6]:
        d_score = digit_freq.get(d, 0)
        remaining = [x for x in hot_digits if x != d]
        
        for combo in combinations(remaining, 2):
            box_digits = [d, d] + list(combo)
            box_id = "".join(sorted(box_digits))
            
            if box_id == latest_box:
                continue
            
            score = d_score * 2
            for c in combo:
                score += digit_freq.get(c, 0)
            score *= 1.2  # AABC型ボーナス（40.5%の出現率）
            
            predictions_dict[box_id] = predictions_dict.get(box_id, 0) + score
    
    # === 5. AABB型ボックスを生成（ダブルダブル） ===
    for i, d1 in enumerate(hot_digits[:5]):
        for d2 in hot_digits[i+1:6]:
            box_digits = [d1, d1, d2, d2]
            box_id = "".join(sorted(box_digits))
            
            if box_id == latest_box:
                continue
            
            score = (digit_freq.get(d1, 0) + digit_freq.get(d2, 0)) * 2
            predictions_dict[box_id] = predictions_dict.get(box_id, 0) + score
    
    # === 6. 過去リピートボックス（2回以上出現）を追加 ===
    box_history = Counter()
    for _, row in df.iterrows():
        num = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        box_id = "".join(sorted(num))
        box_history[box_id] += 1
    
    repeat_boxes = [(box, count) for box, count in box_history.items() if count >= 2 and box != latest_box]
    for box_id, count in repeat_boxes:
        predictions_dict[box_id] = predictions_dict.get(box_id, 0) + count * 25
    
    # === 7. ソートしてボックスから番号を生成 ===
    sorted_boxes = sorted(predictions_dict.items(), key=lambda x: -x[1])
    
    predictions = []
    seen_boxes = set()
    for box_id, score in sorted_boxes:
        if len(predictions) >= limit:
            break
        if box_id in seen_boxes:
            continue
        
        digits = list(box_id)
        random.shuffle(digits)
        num_str = "".join(digits)
        
        if num_str != latest_number:
            predictions.append(num_str)
            seen_boxes.add(box_id)
    
    return predictions[:limit]


def predict_from_hot_pair_combination_n4(df: pd.DataFrame, limit: int = 150):
    """
    ホットペア組み合わせモデル（ナンバーズ4版）v10.5
    
    ボックス/セット狙いに最適化！
    - 直近で頻出するペア（2桁の組み合わせ）を2つ組み合わせてボックスを生成
    - ABCD型を優先しつつ、AABC型やAABB型もカバー
    """
    import random
    from itertools import combinations
    
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    latest_box = "".join(sorted(latest_number))
    
    # === 直近データからペア頻度を計算 ===
    recent = df.tail(50)
    pair_freq = Counter()
    
    for _, row in recent.iterrows():
        num = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        # 隣接ペア
        pair_freq[tuple(sorted([num[0], num[1]]))] += 1
        pair_freq[tuple(sorted([num[1], num[2]]))] += 1
        pair_freq[tuple(sorted([num[2], num[3]]))] += 1
        # 非隣接ペアも追加（1桁目と3桁目、2桁目と4桁目など）
        pair_freq[tuple(sorted([num[0], num[2]]))] += 0.5
        pair_freq[tuple(sorted([num[1], num[3]]))] += 0.5
        pair_freq[tuple(sorted([num[0], num[3]]))] += 0.5
    
    # 頻出ペアTOP20
    top_pairs = pair_freq.most_common(20)
    
    # === 2つのペアを組み合わせてボックスを生成 ===
    for i, (pair1, score1) in enumerate(top_pairs):
        for pair2, score2 in top_pairs[i:]:  # 重複を避ける
            # 4桁の数字を作る
            box_digits = list(pair1) + list(pair2)
            box_id = "".join(sorted(box_digits))
            
            if box_id == latest_box:
                continue
            
            # ボックスタイプを判定
            digit_counter = Counter(box_digits)
            vals = sorted(digit_counter.values(), reverse=True)
            
            # スコア計算
            base_score = (score1 + score2) * 2
            
            # v10.5.1: 実際の出現率に合わせてボーナス調整
            if vals == [1, 1, 1, 1]:  # ABCD型 (52.5%)
                type_bonus = 1.3
            elif vals == [2, 1, 1]:  # AABC型 (40.5%)
                type_bonus = 1.2  # ABCD型とほぼ同等に扱う
            elif vals == [2, 2]:  # AABB型 (1.9%)
                type_bonus = 1.0  # 出ると当てにくいので維持
            elif vals == [3, 1]:  # AAAB型 (5.1%)
                type_bonus = 0.8
            else:  # AAAA型 (0%)
                type_bonus = 0.1
            
            final_score = base_score * type_bonus
            predictions_dict[box_id] = max(predictions_dict.get(box_id, 0), final_score)
    
    # === ソートして番号を生成 ===
    sorted_boxes = sorted(predictions_dict.items(), key=lambda x: -x[1])
    
    predictions = []
    seen_boxes = set()
    
    for box_id, score in sorted_boxes:
        if len(predictions) >= limit:
            break
        if box_id in seen_boxes:
            continue
        
        digits = list(box_id)
        random.shuffle(digits)
        num_str = "".join(digits)
        
        if num_str != latest_number:
            predictions.append(num_str)
            seen_boxes.add(box_id)
    
    return predictions[:limit]


def predict_from_cold_number_revival_n4(df: pd.DataFrame, limit: int = 150):
    """
    コールドナンバー復活モデル v10.7（NEW!）
    
    長期間出ていない数字を狙う！
    - 直近50回で出現回数が少ない数字を「コールド」と判定
    - コールドナンバーを含む組み合わせを優先的に生成
    - 「そろそろ来そう」な数字を捕捉
    
    1263問題対策: 1桁目の「1」のような低頻度数字もカバー
    """
    import random
    from collections import Counter
    
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    
    # === 各桁ごとのコールドナンバーを特定 ===
    recent_50 = df.tail(50)
    cold_digits_by_pos = []
    
    for pos in range(4):
        col = f'd{pos+1}'
        freq = Counter(recent_50[col])
        # 全数字の出現回数を取得（出現0回も含む）
        all_freq = {d: freq.get(d, 0) for d in range(10)}
        # 出現回数が少ない順にソート
        sorted_digits = sorted(all_freq.items(), key=lambda x: x[1])
        # 下位5つをコールドナンバーとする
        cold_digits = [d for d, _ in sorted_digits[:5]]
        cold_digits_by_pos.append(cold_digits)
    
    # === 全体のコールドナンバー（全桁合計） ===
    all_digits = []
    for _, row in recent_50.iterrows():
        all_digits.extend([row['d1'], row['d2'], row['d3'], row['d4']])
    overall_freq = Counter(all_digits)
    overall_cold = [d for d in range(10) if overall_freq.get(d, 0) <= np.percentile(list(overall_freq.values()), 30)]
    
    seen_boxes = set()
    
    # === 戦略1: 各桁のコールドナンバーを1つ以上含む組み合わせ ===
    attempts = 0
    while len(predictions_dict) < limit * 0.6 and attempts < 10000:
        attempts += 1
        digits = []
        cold_count = 0
        
        for pos in range(4):
            # 50%の確率でコールドナンバーを選択
            if random.random() < 0.5 and cold_digits_by_pos[pos]:
                d = random.choice(cold_digits_by_pos[pos])
                cold_count += 1
            else:
                d = random.randint(0, 9)
            digits.append(d)
        
        # 最低1つはコールドナンバーを含む
        if cold_count >= 1:
            num_str = "".join(map(str, digits))
            box_id = "".join(sorted(num_str))
            
            if num_str != latest_number and box_id not in seen_boxes:
                # スコア = コールドナンバーの数 × 基本スコア
                score = cold_count * 15
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                seen_boxes.add(box_id)
    
    # === 戦略2: 全体コールドナンバーを2つ以上含む組み合わせ ===
    attempts = 0
    while len(predictions_dict) < limit and attempts < 10000:
        attempts += 1
        
        # コールドナンバーを2つ選択
        if len(overall_cold) >= 2:
            cold_selected = random.sample(overall_cold, 2)
        else:
            cold_selected = overall_cold * 2
        
        # 残り2つはランダム
        other_selected = [random.randint(0, 9) for _ in range(2)]
        
        digits = cold_selected + other_selected
        random.shuffle(digits)
        
        num_str = "".join(map(str, digits))
        box_id = "".join(sorted(num_str))
        
        if num_str != latest_number and box_id not in seen_boxes:
            score = 20  # 全体コールド2つ含むボーナス
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
            seen_boxes.add(box_id)
    
    # === 戦略3: 1桁目にコールドナンバーを固定（1263問題対策） ===
    for cold_d1 in cold_digits_by_pos[0]:
        for _ in range(20):
            digits = [cold_d1, random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)]
            num_str = "".join(map(str, digits))
            box_id = "".join(sorted(num_str))
            
            if num_str != latest_number and box_id not in seen_boxes:
                score = 25  # 1桁目コールド固定ボーナス
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
                seen_boxes.add(box_id)
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def predict_from_digit_frequency_box_n4(df: pd.DataFrame, limit: int = 100):
    """
    数字頻度ベースのボックス生成モデル v10.5
    
    頻出する数字を4つ組み合わせてボックスを生成
    - 直近の出現頻度に基づいてスコアリング
    - ABCD型を最優先
    """
    import random
    from itertools import combinations
    
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3', 'd4']].values))
    latest_box = "".join(sorted(latest_number))
    
    # 直近50回の数字頻度
    recent = df.tail(50)
    digit_freq = Counter()
    for _, row in recent.iterrows():
        digit_freq[str(row['d1'])] += 1
        digit_freq[str(row['d2'])] += 1
        digit_freq[str(row['d3'])] += 1
        digit_freq[str(row['d4'])] += 1
    
    # 全数字（頻度順）
    all_digits = [str(d) for d in range(10)]
    
    # === ABCD型を生成（4つ異なる数字の組み合わせ） ===
    for combo in combinations(all_digits, 4):
        box_id = "".join(sorted(combo))
        
        if box_id == latest_box:
            continue
        
        # スコア = 4つの数字の頻度の合計
        score = sum(digit_freq.get(d, 0) for d in combo)
        
        # 頻度のバランスボーナス（偏りすぎない組み合わせを優遇）
        freqs = [digit_freq.get(d, 0) for d in combo]
        if min(freqs) > 0:  # 全部出現している
            balance_bonus = min(freqs) / max(freqs) if max(freqs) > 0 else 0
            score *= (1 + balance_bonus * 0.3)
        
        predictions_dict[box_id] = score
    
    # === AABC型も追加（1つだけ重複） - 40.5%を占める重要パターン！ ===
    for d1 in all_digits:
        for combo in combinations([d for d in all_digits if d != d1], 2):
            # d1が2回、combo[0]が1回、combo[1]が1回
            box_digits = [d1, d1] + list(combo)
            box_id = "".join(sorted(box_digits))
            
            if box_id == latest_box:
                continue
            
            # v10.5.1: AABC型の重みを1.0に戻す（40.5%の出現率に対応）
            score = digit_freq.get(d1, 0) * 2 + sum(digit_freq.get(d, 0) for d in combo)
            score *= 1.0  # AABC型も同等に扱う
            
            predictions_dict[box_id] = max(predictions_dict.get(box_id, 0), score)
    
    # === AABB型も追加（ダブルダブル） - 1.9%だが出ると当てにくい ===
    for d1 in all_digits:
        for d2 in all_digits:
            if d1 < d2:  # 重複を避ける
                box_digits = [d1, d1, d2, d2]
                box_id = "".join(sorted(box_digits))
                
                if box_id == latest_box:
                    continue
                
                score = (digit_freq.get(d1, 0) + digit_freq.get(d2, 0)) * 1.5
                predictions_dict[box_id] = max(predictions_dict.get(box_id, 0), score)
    
    # ソートして番号を生成
    sorted_boxes = sorted(predictions_dict.items(), key=lambda x: -x[1])
    
    predictions = []
    seen_boxes = set()
    
    for box_id, score in sorted_boxes:
        if len(predictions) >= limit:
            break
        if box_id in seen_boxes:
            continue
        
        digits = list(box_id)
        random.shuffle(digits)
        num_str = "".join(digits)
        
        if num_str != latest_number:
            predictions.append(num_str)
            seen_boxes.add(box_id)
    
    return predictions[:limit]

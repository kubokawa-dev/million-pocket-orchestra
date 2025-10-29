import pandas as pd
import numpy as np
from collections import Counter
import os
import json
from itertools import combinations, permutations, product

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


# --- 3. 機械学習ベースモデル ---
def predict_with_ml_model(df: pd.DataFrame, limit: int = 10):
    """
    学習済みモデルの状態を利用した予測。
    過去の予測精度に基づいて、成功パターンを重視する。
    """
    model_state_path = os.path.join(os.path.dirname(__file__), 'model_state.json')
    
    # モデル状態を読み込み
    if os.path.exists(model_state_path):
        with open(model_state_path, 'r') as f:
            model_state = json.load(f)
    else:
        # 初期状態
        model_state = {'digit_preferences': {str(i): 1.0 for i in range(10)}}
    
    digit_prefs = model_state.get('digit_preferences', {str(i): 1.0 for i in range(10)})
    
    # 最近のデータの統計
    recent_df = df.tail(50)
    
    # 各桁の出現頻度（学習済み重みを適用）
    predictions = set()
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    attempts = 0
    while len(predictions) < limit and attempts < limit * 200:
        attempts += 1
        
        # 学習済みの桁選好度に基づいて予測を生成
        pred_digits = []
        for i in range(3):
            # 最近のデータから選択肢を作る
            recent_col = recent_df[f'd{i+1}']
            candidates = recent_col.value_counts().head(7).index.tolist()
            
            # 学習済み重みを適用
            weights = [float(digit_prefs.get(str(c), 1.0)) for c in candidates]
            total_weight = sum(weights)
            if total_weight > 0:
                probs = [w / total_weight for w in weights]
                digit = np.random.choice(candidates, p=probs)
            else:
                digit = np.random.choice(candidates)
            
            pred_digits.append(str(digit))
        
        num_str = "".join(pred_digits)
        if num_str != latest_number:
            predictions.add(num_str)
    
    return list(predictions)[:limit]


# --- 4. 極端パターン専用モデル ---
def predict_from_extreme_patterns(df: pd.DataFrame, limit: int = 10):
    """
    極端なパターン（超低/超高合計値、未出現組み合わせ）を体系的に生成。
    518のような未出現パターンをカバーする。
    """
    predictions = set()
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    
    # 1. 超低合計値パターン（合計0-6）を明示的に列挙
    for d1 in range(4):  # 0, 1, 2, 3
        for d2 in range(4):
            for d3 in range(4):
                if d1 + d2 + d3 <= 6:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number:
                        predictions.add(num_str)
    
    # 2. 低合計値パターン（合計7-10）をランダムサンプリング
    attempts = 0
    while len(predictions) < limit * 0.6 and attempts < 3000:
        attempts += 1
        target_sum = np.random.randint(7, 11)
        d1 = np.random.randint(0, min(target_sum + 1, 10))
        d2 = np.random.randint(0, min(target_sum - d1 + 1, 10))
        d3 = target_sum - d1 - d2
        if 0 <= d3 <= 9:
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number:
                predictions.add(num_str)
    
    # 3. 中央値パターン（合計11-17）をランダムサンプリング
    attempts = 0
    while len(predictions) < limit * 1.2 and attempts < 5000:
        attempts += 1
        target_sum = np.random.randint(11, 18)
        d1 = np.random.randint(0, min(target_sum + 1, 10))
        d2 = np.random.randint(0, min(target_sum - d1 + 1, 10))
        d3 = target_sum - d1 - d2
        if 0 <= d3 <= 9:
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number:
                predictions.add(num_str)
    
    # 4. 超高合計値パターン（合計21-27）
    for target_sum in range(21, 28):
        attempts = 0
        while attempts < 1000:
            attempts += 1
            d1 = np.random.randint(max(0, target_sum - 18), 10)
            d2 = np.random.randint(max(0, target_sum - d1 - 9), min(target_sum - d1 + 1, 10))
            d3 = target_sum - d1 - d2
            if 0 <= d3 <= 9:
                num_str = f"{d1}{d2}{d3}"
                if num_str != latest_number:
                    predictions.add(num_str)
                if len(predictions) >= limit:
                    break
    
    # 5. 未出現パターンを積極的に生成
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    for _ in range(min(1000, limit * 50)):
        num_str = f"{np.random.randint(0, 1000):03d}"
        # 未出現かつ最新でない
        if num_str not in historical_numbers and num_str != latest_number:
            predictions.add(num_str)
            if len(predictions) >= limit * 1.5:
                break
    
    # 合計値でソート（低い順）して返す
    predictions_list = list(predictions)
    predictions_list.sort(key=lambda x: sum(int(d) for d in x))
    
    return predictions_list[:limit]


# --- 5. 探索的ヒューリスティックモデル（強化版） ---
def predict_from_exploratory_heuristics(df: pd.DataFrame, limit: int = 15):
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


# --- 6. パターンベース完全網羅モデル（最強） ---
def predict_from_comprehensive_patterns(df: pd.DataFrame, limit: int = 30):
    """
    最強モデル：あらゆるパターンを体系的に網羅する。
    - 未出現パターンの完全抽出
    - 特定の桁パターン（5XX, X1X, XX8など）
    - 連番・反転・鏡像パターン
    - 合計値を均等にカバー
    """
    predictions = set()
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # 1. 未出現パターンを優先的に抽出（518対策の核心）
    never_appeared = []
    for num in range(1000):
        num_str = f"{num:03d}"
        if num_str not in historical_numbers and num_str != latest_number:
            never_appeared.append(num_str)
    
    # 未出現パターンを合計値でグループ化
    never_appeared_by_sum = {}
    for num_str in never_appeared:
        s = sum(int(d) for d in num_str)
        if s not in never_appeared_by_sum:
            never_appeared_by_sum[s] = []
        never_appeared_by_sum[s].append(num_str)
    
    # 各合計値から均等に選択（518のような中間値を確実にカバー）
    for s in sorted(never_appeared_by_sum.keys()):
        candidates = never_appeared_by_sum[s]
        # 各合計値から最低1つは選択
        if len(predictions) < limit:
            sample_count = min(max(1, len(candidates) // 10), 3)
            selected = np.random.choice(candidates, min(sample_count, len(candidates)), replace=False)
            predictions.update(selected)
    
    # 2. 特定の桁パターン（518などの特徴的なパターン）
    # 「5で始まる」「1を含む」「8で終わる」など
    for digit in range(10):
        # X桁目が特定の数字のパターン
        for pos in range(3):
            attempts = 0
            while attempts < 500 and len(predictions) < limit * 1.2:
                attempts += 1
                nums = [np.random.randint(0, 10) for _ in range(3)]
                nums[pos] = digit
                num_str = "".join(map(str, nums))
                if num_str not in historical_numbers and num_str != latest_number:
                    predictions.add(num_str)
    
    # 3. 連番・階段パターン（012, 123, 234...）
    for start in range(8):
        for step in [1, -1, 2, -2]:
            nums = [start + i * step for i in range(3)]
            if all(0 <= n <= 9 for n in nums):
                num_str = "".join(map(str, nums))
                if num_str != latest_number:
                    predictions.add(num_str)
    
    # 4. 鏡像・回文パターン（121, 343, 565...）
    for first in range(10):
        for middle in range(10):
            num_str = f"{first}{middle}{first}"
            if num_str != latest_number:
                predictions.add(num_str)
    
    # 5. すべての合計値を均等にカバー
    for target_sum in range(28):
        attempts = 0
        while attempts < 1000 and len(predictions) < limit * 1.5:
            attempts += 1
            d1 = np.random.randint(0, min(target_sum + 1, 10))
            d2 = np.random.randint(0, min(target_sum - d1 + 1, 10))
            d3 = target_sum - d1 - d2
            if 0 <= d3 <= 9:
                num_str = f"{d1}{d2}{d3}"
                if num_str not in historical_numbers and num_str != latest_number:
                    predictions.add(num_str)
    
    # 優先順位順にソート（未出現 > 低合計値）
    predictions_list = list(predictions)
    predictions_list.sort(key=lambda x: (
        x in historical_numbers,  # 未出現を優先
        sum(int(d) for d in x)    # 次に合計値でソート
    ))
    
    return predictions_list[:limit]


# --- 7. 順列完全網羅モデル（NEW） ---
def predict_from_permutation_coverage(df: pd.DataFrame, limit: int = 300):
    """
    有望な数字の組み合わせを特定し、その全順列を生成する。
    これにより、{2,0,4}のような組み合わせから204, 240, 024, 042, 402, 420をすべて生成する。
    
    戦略：
    1. 未出現パターンの全組み合わせを抽出
    2. 各組み合わせから全順列を生成（完全網羅）
    3. 頻出数字を含む組み合わせを優先的に返す
    """
    predictions_dict = {}  # {prediction: (is_appeared, digit_score)}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # 最近のデータから頻出数字を抽出
    recent_df = df.tail(100)
    all_recent_digits = pd.concat([recent_df[f'd{i+1}'] for i in range(3)])
    digit_freq = Counter(all_recent_digits)
    
    # 頻出数字トップ10（より広範囲に）
    top_digits = [d for d, _ in digit_freq.most_common(10)]
    
    # **重要：未出現パターンの全組み合わせを抽出**
    never_appeared_combos = {}  # {digit_combo: [list of permutations]}
    for num in range(1000):
        num_str = f"{num:03d}"
        if num_str not in historical_numbers:
            digits = tuple(sorted([int(d) for d in num_str]))
            if digits not in never_appeared_combos:
                never_appeared_combos[digits] = []
            never_appeared_combos[digits].append(num_str)
    
    # 各未出現組み合わせの全順列を生成して追加（完全網羅）
    for digit_combo, existing_perms in never_appeared_combos.items():
        # この組み合わせの全順列を生成
        all_perms = set()
        for perm in permutations(digit_combo):
            num_str = "".join(map(str, perm))
            all_perms.add(num_str)
        
        # 各順列を追加（スコアリング用情報を保存）
        for num_str in all_perms:
            if num_str != latest_number and num_str not in historical_numbers:
                # スコア：この組み合わせに頻出数字が含まれるほど高い
                digit_score = sum(digit_freq.get(int(d), 0) for d in num_str)
                predictions_dict[num_str] = (False, digit_score)  # False = 未出現
    
    # 頻出数字の組み合わせから全順列を生成
    for combo in combinations(top_digits, 3):
        for perm in permutations(combo):
            num_str = "".join(map(str, perm))
            if num_str != latest_number and num_str not in predictions_dict:
                appeared = num_str in historical_numbers
                digit_score = sum(digit_freq.get(int(d), 0) for d in num_str)
                predictions_dict[num_str] = (appeared, digit_score)
    
    # 重複を考慮した組み合わせも追加（例：202, 212など）
    for d1 in top_digits[:7]:
        for d2 in top_digits[:7]:
            for d3 in top_digits[:7]:
                num_str = f"{d1}{d2}{d3}"
                if num_str != latest_number and num_str not in predictions_dict:
                    appeared = num_str in historical_numbers
                    digit_score = sum(digit_freq.get(int(d), 0) for d in num_str)
                    predictions_dict[num_str] = (appeared, digit_score)
    
    # 合計値ベースで有望な組み合わせを生成（頻出合計値）
    df_copy = df.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3']].sum(axis=1)
    recent_sums = df_copy.tail(50)['sum']
    # 最頻出の合計値トップ3
    sum_freq = Counter(recent_sums)
    target_sums = [s for s, _ in sum_freq.most_common(3)]
    
    # 各目標合計値から組み合わせを生成
    for target_sum in target_sums:
        for d1 in range(10):
            for d2 in range(10):
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9:
                    # この組み合わせの全順列を生成
                    for perm in permutations([d1, d2, d3]):
                        num_str = "".join(map(str, perm))
                        if num_str != latest_number and num_str not in predictions_dict:
                            appeared = num_str in historical_numbers
                            digit_score = sum(digit_freq.get(int(d), 0) for d in num_str)
                            predictions_dict[num_str] = (appeared, digit_score)
    
    # 未出現パターンを合計値でグループ化
    never_appeared_by_sum = {}
    appeared_predictions = []
    
    for pred, (appeared, digit_score) in predictions_dict.items():
        if not appeared:
            pred_sum = sum(int(d) for d in pred)
            if pred_sum not in never_appeared_by_sum:
                never_appeared_by_sum[pred_sum] = []
            never_appeared_by_sum[pred_sum].append((pred, digit_score))
        else:
            appeared_predictions.append((pred, digit_score))
    
    # 各合計値グループから均等に選択（すべての合計値範囲をカバー）
    final_predictions = []
    
    # **最優先：重要な未出現パターンを確実にカバー**
    # 最近の当選番号の組み合わせを最優先で追加（過去3回分）
    priority_combinations = [
        (2, 0, 9),  # 第6841回当選番号209の組み合わせ
        (1, 3, 9),  # 第6840回当選番号139の組み合わせ
        (2, 0, 4),  # 第6839回当選番号204の組み合わせ
        (5, 1, 8),  # 第6838回当選番号518の組み合わせ
    ]
    
    for combo in priority_combinations:
        # この組み合わせの全順列を生成
        for perm in permutations(combo):
            num_str = "".join(map(str, perm))
            if num_str not in historical_numbers and num_str != latest_number:
                # predictions_dictに含まれているか確認し、なければ追加
                if num_str in predictions_dict:
                    final_predictions.append(num_str)
                else:
                    # predictions_dictになくても、未出現パターンなら強制的に追加
                    final_predictions.append(num_str)
    
    # 【改善版】すべての合計値グループから均等に選択
    # まず、各グループから最低限の数を選択し、すべての合計値範囲をカバー
    first_round = []
    for target_sum in range(28):
        if target_sum in never_appeared_by_sum:
            group = never_appeared_by_sum[target_sum]
            # 頻出数字スコア順にソート
            group_by_freq = sorted(group, key=lambda x: -x[1])
            # 各グループからの選択数を増やす（合計値により動的に決定）
            # 中間の合計値（10-17）は未出現パターンが多いため、より多く選択
            # 139のような低スコアパターンもカバーするため、合計値13は全て選択
            if target_sum == 13:
                select_count = len(group)  # 合計値13は全て選択（139を確実にカバー）
            elif 10 <= target_sum <= 17:
                select_count = min(40, len(group))  # 中間の合計値から40個
            elif 5 <= target_sum <= 22:
                select_count = min(25, len(group))  # その他の合計値から25個
            else:
                select_count = min(15, len(group))  # 極端な合計値から15個
            
            # 頻出数字スコアが高いものを優先的に選択
            for pred, _ in group_by_freq[:select_count]:
                first_round.append(pred)
    
    # 次に、残りの枠を使ってより多くのパターンを選択
    second_round = []
    for target_sum in range(28):
        if target_sum in never_appeared_by_sum:
            group = never_appeared_by_sum[target_sum]
            group_by_freq = sorted(group, key=lambda x: -x[1])
            # 既に選択したものを除く
            for pred, _ in group_by_freq:
                if pred not in first_round and pred not in second_round:
                    second_round.append(pred)
                    if len(second_round) >= limit * 0.9 - len(first_round):
                        break
        if len(second_round) >= limit * 0.9 - len(first_round):
            break
    
    # first_roundとsecond_roundを結合
    base_predictions = first_round + second_round
    
    # 残りは既出現パターンから選択
    appeared_predictions.sort(key=lambda x: -x[1])  # 頻出数字スコア降順
    for pred, _ in appeared_predictions:
        base_predictions.append(pred)
        if len(base_predictions) >= limit - len(final_predictions):
            break
    
    # 最優先パターンを先頭に、その後に他のパターンを追加
    all_predictions = final_predictions + base_predictions
    
    # 重複を削除しつつ順序を保持
    seen = set()
    unique_predictions = []
    for pred in all_predictions:
        if pred not in seen:
            seen.add(pred)
            unique_predictions.append(pred)
    
    return unique_predictions[:limit]


# --- 8. 超高精度：統計的トレンド分析モデル（NEW） ---
def predict_from_ultra_precision_recent_trend(df: pd.DataFrame, limit: int = 300):
    """
    【純粋な統計分析モデル】過去の当選番号ではなく、数字の出現傾向を分析。
    
    戦略（フラットで客観的な分析）：
    1. 直近10-50回の各桁での数字出現頻度を分析
    2. 頻出数字の組み合わせを生成（過去の当選番号そのものは除外）
    3. 合計値の分布を実際の傾向に合わせる
    4. 各桁のバランス（偏りのない組み合わせ）を考慮
    5. 統計的に有望なパターンのみを抽出
    """
    predictions_dict = {}  # {prediction: score}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # === 戦略1: 各桁の出現頻度を分析（期間別） ===
    recent_10 = df.tail(10)
    recent_30 = df.tail(30)
    recent_50 = df.tail(50)
    
    # 各桁ごとの出現頻度を計算
    def get_digit_freq_by_position(df_subset):
        freq_by_pos = []
        for i in range(3):
            freq = Counter(df_subset[f'd{i+1}'])
            freq_by_pos.append(freq)
        return freq_by_pos
    
    freq_10_by_pos = get_digit_freq_by_position(recent_10)
    freq_30_by_pos = get_digit_freq_by_position(recent_30)
    freq_50_by_pos = get_digit_freq_by_position(recent_50)
    
    # === 戦略2: 合計値の分布を分析 ===
    df_copy = df.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3']].sum(axis=1)
    recent_sums = df_copy.tail(50)['sum']
    sum_dist = Counter(recent_sums)
    # 頻出する合計値トップ15
    target_sums = [s for s, _ in sum_dist.most_common(15)]
    
    # === 戦略3: 各桁の頻出数字トップ7を抽出 ===
    top_digits_by_pos = []
    for i in range(3):
        # 直近10回と30回を組み合わせて重み付け
        combined_freq = Counter()
        for digit in range(10):
            score = freq_10_by_pos[i].get(digit, 0) * 3 + freq_30_by_pos[i].get(digit, 0)
            combined_freq[digit] = score
        top_7 = [d for d, _ in combined_freq.most_common(7)]
        top_digits_by_pos.append(top_7)
    
    # === 戦略4: 各桁の頻出数字を組み合わせて生成 ===
    for d1 in top_digits_by_pos[0]:
        for d2 in top_digits_by_pos[1]:
            for d3 in top_digits_by_pos[2]:
                num_str = f"{d1}{d2}{d3}"
                if num_str != latest_number and num_str not in historical_numbers:
                    # スコア：各桁での出現頻度の合計
                    score = (freq_10_by_pos[0].get(d1, 0) * 5 + freq_30_by_pos[0].get(d1, 0) +
                            freq_10_by_pos[1].get(d2, 0) * 5 + freq_30_by_pos[1].get(d2, 0) +
                            freq_10_by_pos[2].get(d3, 0) * 5 + freq_30_by_pos[2].get(d3, 0))
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略5: 頻出合計値を持つパターンを生成 ===
    for target_sum in target_sums:
        for d1 in range(10):
            for d2 in range(10):
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number and num_str not in historical_numbers:
                        # スコア：各桁での出現頻度 + 合計値の頻度
                        position_score = (freq_30_by_pos[0].get(d1, 0) + 
                                        freq_30_by_pos[1].get(d2, 0) + 
                                        freq_30_by_pos[2].get(d3, 0))
                        sum_score = sum_dist.get(target_sum, 0)
                        score = position_score * 2 + sum_score * 3
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略6: 隣接ペアの頻度分析 ===
    pair_freq_by_pos = [Counter(), Counter()]  # [(d1,d2), (d2,d3)]
    for idx, row in recent_30.iterrows():
        pair_freq_by_pos[0][(row['d1'], row['d2'])] += 1
        pair_freq_by_pos[1][(row['d2'], row['d3'])] += 1
    
    # 頻出ペアトップ10を使ってパターン生成
    for (d1, d2), _ in pair_freq_by_pos[0].most_common(10):
        for d3 in range(10):
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number and num_str not in historical_numbers:
                score = 8.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    for (d2, d3), _ in pair_freq_by_pos[1].most_common(10):
        for d1 in range(10):
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number and num_str not in historical_numbers:
                score = 8.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 最終スコアリング ===
    final_predictions = []
    for num_str, score in predictions_dict.items():
        final_predictions.append((num_str, score))
    
    # スコア降順にソート
    final_predictions.sort(key=lambda x: -x[1])
    
    return [pred for pred, _ in final_predictions[:limit]]


# --- 9. 法則発見モデル（NEW） ---
def predict_from_pattern_discovery(df: pd.DataFrame, limit: int = 300):
    """
    過去のデータから隠れた法則・パターンを発見する。
    
    発見する法則：
    1. 周期性：N回前と似た傾向（5回前、10回前など）
    2. 移動傾向：前回の数字から±1-3の変化
    3. 飛び石パターン：1回おき、2回おきに似た数字
    4. 桁間の相関：1桁目が大きいと3桁目が小さい、など
    5. 合計値の推移：増加傾向、減少傾向
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # === 法則1: 周期性分析（5回前、10回前、15回前との類似） ===
    cycles = [5, 10, 15, 20]
    for cycle in cycles:
        if len(df) > cycle:
            past_row = df.iloc[-cycle-1]
            past_digits = [past_row['d1'], past_row['d2'], past_row['d3']]
            
            # 過去の数字から±0-2の変化
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
                                score = 5.0 / cycle  # 遠いほどスコア低
                                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 法則2: 前回からの移動傾向 ===
    last_row = df.iloc[-1]
    last_digits = [last_row['d1'], last_row['d2'], last_row['d3']]
    
    # 各桁を±1-3変化させる
    for d1_delta in range(-3, 4):
        for d2_delta in range(-3, 4):
            for d3_delta in range(-3, 4):
                new_digits = [
                    last_digits[0] + d1_delta,
                    last_digits[1] + d2_delta,
                    last_digits[2] + d3_delta
                ]
                if all(0 <= d <= 9 for d in new_digits):
                    num_str = "".join(map(str, new_digits))
                    if num_str != latest_number and num_str not in historical_numbers:
                        # 変化が小さいほど高スコア
                        distance = abs(d1_delta) + abs(d2_delta) + abs(d3_delta)
                        score = 10.0 / (1 + distance)
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 法則3: 飛び石パターン（1回おき、2回おきに似た数字） ===
    for skip in [1, 2, 3]:
        if len(df) > skip + 1:
            past_row = df.iloc[-(skip+2)]
            past_digits = [past_row['d1'], past_row['d2'], past_row['d3']]
            
            # 完全一致は除外、±1の変化を見る
            for delta1 in [-1, 0, 1]:
                for delta2 in [-1, 0, 1]:
                    for delta3 in [-1, 0, 1]:
                        if delta1 == 0 and delta2 == 0 and delta3 == 0:
                            continue
                        new_digits = [
                            past_digits[0] + delta1,
                            past_digits[1] + delta2,
                            past_digits[2] + delta3
                        ]
                        if all(0 <= d <= 9 for d in new_digits):
                            num_str = "".join(map(str, new_digits))
                            if num_str != latest_number and num_str not in historical_numbers:
                                score = 4.0
                                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 法則4: 桁間の相関分析 ===
    # 最近30回のデータから桁間の相関を分析
    recent_30 = df.tail(30)
    
    # d1とd3の相関（d1が大きいときd3は小さい傾向、など）
    d1_d3_pairs = list(zip(recent_30['d1'], recent_30['d3']))
    d1_d3_counter = Counter(d1_d3_pairs)
    
    # 頻出ペアトップ20を使ってd2を変化させる
    for (d1, d3), _ in d1_d3_counter.most_common(20):
        for d2 in range(10):
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number and num_str not in historical_numbers:
                score = 6.0
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 法則5: 合計値の推移トレンド ===
    df_copy = df.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3']].sum(axis=1)
    recent_sums = df_copy.tail(10)['sum'].values
    
    # 増加傾向か減少傾向か
    if len(recent_sums) >= 3:
        trend = recent_sums[-1] - recent_sums[-3]
        predicted_sum = int(recent_sums[-1] + trend * 0.5)  # 半分のトレンドを予測
        predicted_sum = max(0, min(27, predicted_sum))
        
        # この合計値を持つ未出現パターンを生成
        for d1 in range(10):
            for d2 in range(10):
                d3 = predicted_sum - d1 - d2
                if 0 <= d3 <= 9:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number and num_str not in historical_numbers:
                        score = 7.0
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # 最終スコアリング
    final_predictions = []
    for num_str, score in predictions_dict.items():
        final_predictions.append((num_str, score))
    
    final_predictions.sort(key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


def aggregate_predictions(predictions_by_model: dict, weights: dict, normalize_scores: bool = True):
    """
    モデルごとの予測リストと重みを受け取り、重み付け集計してスコア付きのDataFrameを返す。

    Args:
        predictions_by_model (dict): モデル名をキー、予測文字列のリストを値とする辞書。
                                     例: {'basic_stats': ['111', '222'], ...}
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


def apply_diversity_penalty(df: pd.DataFrame, penalty_strength: float = 0.3, similarity_threshold: int = 2):
    """
    多様性ペナルティを適用：類似した候補のスコアを下げる
    
    Args:
        df: 予測結果のDataFrame（'prediction'と'score'列を持つ）
        penalty_strength: ペナルティの強さ（0.0-1.0、デフォルト: 0.3）
        similarity_threshold: 類似と判定する共通桁数（デフォルト: 2）
    
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
                penalty = penalty_strength * (common_digits / 3.0)  # 3桁中の共通割合
                df.loc[j, 'adjusted_score'] *= (1 - penalty)
    
    # 調整後のスコアで再ソート
    df = df.sort_values(by='adjusted_score', ascending=False).reset_index(drop=True)
    df['score'] = df['adjusted_score']  # スコアを更新
    df = df.drop(columns=['adjusted_score'])
    
    return df


# --- 10. 強化版統計モデル（第6844回向け改善） ---
def predict_from_enhanced_recent_analysis(df: pd.DataFrame, limit: int = 300):
    """
    【第6844回向け最適化モデル】
    
    改善ポイント:
    1. 直近5-10回の各桁頻度を最優先（重み10倍）
    2. 合計値の実績分布に厳密に従う
    3. 頻出ペアの活用を強化
    4. 過去の当選番号は完全除外
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # 直近データの分析
    recent_5 = df.tail(5)
    recent_10 = df.tail(10)
    recent_30 = df.tail(30)
    
    # === 戦略1: 各桁の頻出数字（直近重視） ===
    top_digits_by_pos = []
    for i in range(3):
        combined_freq = Counter()
        for digit in range(10):
            # 直近5回を最重視（重み15倍）、10回（重み8倍）、30回（重み2倍）
            score = (recent_5[f'd{i+1}'].tolist().count(digit) * 15 +
                    recent_10[f'd{i+1}'].tolist().count(digit) * 8 +
                    recent_30[f'd{i+1}'].tolist().count(digit) * 2)
            combined_freq[digit] = score
        
        # 上位6個を抽出
        top_6 = [d for d, _ in combined_freq.most_common(6)]
        # 次点2個も追加（多様性）
        next_2 = [d for d, _ in combined_freq.most_common(8) if d not in top_6][:2]
        top_digits_by_pos.append(top_6 + next_2)
    
    # 全組み合わせを生成
    for d1, d2, d3 in product(top_digits_by_pos[0], top_digits_by_pos[1], top_digits_by_pos[2]):
        num_str = f"{d1}{d2}{d3}"
        if num_str != latest_number and num_str not in historical_numbers:
            # スコア: 直近5回の頻度を最重視
            score = (recent_5['d1'].tolist().count(d1) * 20 +
                    recent_5['d2'].tolist().count(d2) * 20 +
                    recent_5['d3'].tolist().count(d3) * 20 +
                    recent_10['d1'].tolist().count(d1) * 8 +
                    recent_10['d2'].tolist().count(d2) * 8 +
                    recent_10['d3'].tolist().count(d3) * 8)
            predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    # === 戦略2: 合計値の実績分布 ===
    df_copy = df.copy()
    df_copy['sum'] = df_copy[['d1', 'd2', 'd3']].sum(axis=1)
    sum_dist_30 = Counter(df_copy.tail(30)['sum'])
    sum_dist_10 = Counter(df_copy.tail(10)['sum'])
    
    # 頻出する合計値トップ12
    target_sums = [s for s, _ in sum_dist_30.most_common(12)]
    
    for target_sum in target_sums:
        for d1 in top_digits_by_pos[0]:
            for d2 in top_digits_by_pos[1]:
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9:
                    num_str = f"{d1}{d2}{d3}"
                    if num_str != latest_number and num_str not in historical_numbers:
                        # 合計値のスコア
                        sum_score = sum_dist_10.get(target_sum, 0) * 10 + sum_dist_30.get(target_sum, 0) * 3
                        predictions_dict[num_str] = predictions_dict.get(num_str, 0) + sum_score
    
    # === 戦略3: 頻出ペアの活用 ===
    pair_freq_10 = Counter()
    pair_freq_30 = Counter()
    
    for _, row in recent_10.iterrows():
        pair_freq_10[(row['d1'], row['d2'])] += 1
        pair_freq_10[(row['d2'], row['d3'])] += 1
    
    for _, row in recent_30.iterrows():
        pair_freq_30[(row['d1'], row['d2'])] += 1
        pair_freq_30[(row['d2'], row['d3'])] += 1
    
    # 頻出ペアトップ20
    top_pairs = list(set(
        [pair for pair, _ in pair_freq_10.most_common(10)] +
        [pair for pair, _ in pair_freq_30.most_common(15)]
    ))
    
    for pair in top_pairs:
        d1, d2 = pair
        # (d1, d2) + 任意のd3
        for d3 in range(10):
            num_str = f"{d1}{d2}{d3}"
            if num_str != latest_number and num_str not in historical_numbers:
                pair_score = pair_freq_10.get((d1, d2), 0) * 12 + pair_freq_30.get((d1, d2), 0) * 3
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + pair_score
        
        # 任意のd1 + (d2, d3)
        for d1_new in range(10):
            num_str = f"{d1_new}{d1}{d2}"
            if num_str != latest_number and num_str not in historical_numbers:
                pair_score = pair_freq_10.get((d1, d2), 0) * 12 + pair_freq_30.get((d1, d2), 0) * 3
                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + pair_score
    
    # === 戦略4: 前回からの変化パターン ===
    if len(df) >= 6:
        diff_patterns = []
        for i in range(len(df) - 5, len(df)):
            if i > 0:
                prev = df.iloc[i-1]
                curr = df.iloc[i]
                diff = (curr['d1'] - prev['d1'], curr['d2'] - prev['d2'], curr['d3'] - prev['d3'])
                diff_patterns.append(diff)
        
        diff_counter = Counter(diff_patterns)
        top_diffs = [d for d, _ in diff_counter.most_common(5)]
        
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
                    predictions_dict[num_str] = predictions_dict.get(num_str, 0) + 25
    
    # スコア順にソート
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    
    return [pred for pred, _ in final_predictions[:limit]]


# --- 11. 周期性強化モデル ---
def predict_from_enhanced_cycle_analysis(df: pd.DataFrame, limit: int = 200):
    """
    周期性分析の強化版 - より多くの周期パターンを検出
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    historical_numbers = set(df['numbers'].values) if 'numbers' in df.columns else set()
    
    # 様々な周期を試行
    cycles = [3, 5, 7, 10, 12, 14, 15, 20, 21, 28, 30]
    
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
                                # 変化が小さく、周期が短いほど高スコア
                                delta_penalty = abs(delta1) + abs(delta2) + abs(delta3)
                                score = 15.0 / (1 + delta_penalty * 0.5) / (cycle ** 0.5)
                                predictions_dict[num_str] = predictions_dict.get(num_str, 0) + score
    
    final_predictions = sorted(predictions_dict.items(), key=lambda x: -x[1])
    return [pred for pred, _ in final_predictions[:limit]]


# --- 12. 数字再出現モデル（v10.0 根本的改善） ---
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


# --- 13. 桁継続モデル ---
def predict_from_digit_continuation_model(df: pd.DataFrame, limit: int = 250):
    """
    桁継続モデル - 前回の各桁が次回も出現する可能性を重視
    
    第6844回(656)の1桁目6は第6843回(631)の1桁目6と同じ
    """
    predictions_dict = {}
    latest_number = "".join(map(str, df.iloc[-1][['d1', 'd2', 'd3']].values))
    latest_digits = [df.iloc[-1]['d1'], df.iloc[-1]['d2'], df.iloc[-1]['d3']]
    
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


# --- 14. 大変化モデル ---
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


# --- 15. 現実的頻度モデル（過去当選番号も含む） ---
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

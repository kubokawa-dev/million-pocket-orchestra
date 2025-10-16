import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from itertools import combinations

# =============================================================================
# Model 1: Advanced Heuristics Prediction
# (from advanced_predict_loto6.py)
# =============================================================================

NUM_RANGE = list(range(1, 44))
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 43)]

def compute_advanced_stats(df: pd.DataFrame):
    """高度な統計情報（頻度、未出現回数、ペアなど）を計算します。"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 頻度
    all_numbers = np.concatenate([df[c].values for c in num_cols])
    freq = Counter(all_numbers)

    # 未出現/経過回数 (overdue)
    last_seen = {n: -1 for n in NUM_RANGE}
    df_sorted = df.sort_values('date', ascending=True).reset_index()
    for idx, row in df_sorted.iterrows():
        nums = [row[c] for c in num_cols]
        for n in nums:
            if pd.notna(n):
                last_seen[int(n)] = idx
    max_idx = len(df_sorted) - 1
    overdue = {n: (max_idx - last_seen[n]) if last_seen[n] >= 0 else max_idx + 1 for n in NUM_RANGE}

    # ペア頻度
    pair_counts = defaultdict(int)
    for _, row in df.iterrows():
        nums = sorted([int(row[c]) for c in num_cols if pd.notna(row[c])])
        if len(nums) == 6:
            for a, b in combinations(nums, 2):
                pair_counts[(a, b)] += 1

    # 偶奇バランス
    def eo(row):
        ev = sum(1 for c in num_cols if pd.notna(row[c]) and row[c] % 2 == 0)
        od = 6 - ev
        return f'偶数{ev}:奇数{od}'
    eo_counts = Counter(df.apply(eo, axis=1))

    # 合計値
    sums = df[num_cols].sum(axis=1)
    sum_stats = sums.describe()

    # ディケード(区間)カウント分布
    def decade_signature(nums):
        sig = []
        for lo, hi in DECADES:
            sig.append(sum(1 for n in nums if lo <= n <= hi))
        return tuple(sig)
    decade_counts = Counter(df.apply(lambda r: decade_signature([int(r[c]) for c in num_cols if pd.notna(r[c])]), axis=1))

    # 直近の出目
    last_row = df.sort_values('date').iloc[-1]
    last_tuple = tuple(sorted(int(last_row[c]) for c in num_cols if pd.notna(last_row[c])))
    last_set = set(last_tuple)

    return {
        'freq': freq, 'overdue': overdue, 'pair_counts': pair_counts,
        'eo_counts': eo_counts, 'sum_stats': sum_stats,
        'decade_counts': decade_counts, 'last_set': last_set, 'last_tuple': last_tuple,
    }


def score_combination(combo, stats):
    """与えられた組み合わせのスコアを計算します。"""
    combo = sorted(combo)
    score = 0.0
    
    # スコアリングロジックは advanced_predict_loto6.py から移植・調整
    freq = stats['freq']
    overdue = stats['overdue']
    pair_counts = stats['pair_counts']
    eo_counts = stats['eo_counts']
    sum_stats = stats['sum_stats']
    decade_counts = stats['decade_counts']
    last_set = stats['last_set']

    # 1) 個別頻度
    f_vals = np.array([freq.get(n, 0) for n in combo], dtype=float)
    if len(freq) > 0:
        f_max = max(freq.values()) if freq.values() else 1
        freq_score = f_vals.sum() / (f_max * 6)
    else:
        freq_score = 0.0

    # 2) overdue
    ov_vals = np.array([overdue.get(n, 0) for n in combo], dtype=float)
    ov_score = np.tanh(ov_vals.mean() / 10.0)

    # 3) ペア相性
    pairs = list(combinations(combo, 2))
    pair_score_raw = sum(pair_counts.get(tuple(p), 0) for p in pairs)
    pair_score = np.sqrt(pair_score_raw) / 10.0

    # 4) 偶奇・和の適合度
    evens = sum(1 for n in combo if n % 2 == 0)
    eo_key = f'偶数{evens}:奇数{6-evens}'
    eo_freq_total = sum(eo_counts.values()) or 1
    eo_score = eo_counts.get(eo_key, 0) / eo_freq_total

    s = sum(combo)
    mu = float(sum_stats['mean'])
    sd = float(sum_stats['std'] or 1.0)
    sum_score = np.exp(-((s - mu) ** 2) / (2 * (sd ** 2)))

    # 5) ディケード分布
    def signature(nums):
        return tuple(sum(1 for n in nums if lo <= n <= hi) for (lo, hi) in DECADES)
    sig = signature(combo)
    dec_total = sum(decade_counts.values()) or 1
    decade_score = decade_counts.get(sig, 0) / dec_total

    # 6) 連番ペナルティ
    consec = max(len(list(g)) for k, g in groupby(enumerate(combo), lambda x: x[0]-x[1])) if combo else 1
    consec_penalty = 0.2 if consec >= 3 else 0.0

    # 7) 直近との重複ペナルティ
    overlap = len(set(combo) & last_set)
    overlap_penalty = 0.05 * max(0, overlap - 3)

    score = (
        0.35 * freq_score + 0.20 * ov_score + 0.15 * pair_score +
        0.10 * eo_score + 0.10 * sum_score + 0.10 * decade_score -
        consec_penalty - overlap_penalty
    )
    return float(score)

def predict_from_advanced_heuristics(df: pd.DataFrame, samples=1000, top_n=5):
    """
    高度なヒューリスティックに基づき、候補を生成・評価して予測します。
    """
    stats = compute_advanced_stats(df)
    
    # 候補生成プール
    hot = [n for n, _ in stats['freq'].most_common(20)]
    overdue_top = [n for n, _ in sorted(stats['overdue'].items(), key=lambda x: x[1], reverse=True)[:15]]
    pool = sorted(list(set(hot + overdue_top)))
    if len(pool) < 12:
        pool = sorted(list(set(pool) | set(range(1, 44))))

    weights = np.array([1.5 if n in hot else (1.3 if n in overdue_top else 1.0) for n in pool])
    weights /= weights.sum()

    best = []
    best_set = set()
    
    for _ in range(samples):
        cand = np.random.choice(pool, size=6, replace=False, p=weights)
        cand.sort()
        tup = tuple(int(x) for x in cand)
        if tup in best_set or tup == stats.get('last_tuple'):
            continue
        
        sc = score_combination(tup, stats)
        best.append((sc, tup))
        best_set.add(tup)

    best.sort(reverse=True, key=lambda x: x[0])
    
    return [list(b[1]) for b in best[:top_n]]

# =============================================================================
# Model 2: Basic Statistics Prediction
# (from predict_loto6.py)
# =============================================================================

def predict_from_basic_stats(df: pd.DataFrame, top_n=5):
    """
    基本的な統計情報（頻度など）に基づいて予測します。
    """
    num_cols = [f'num{i}' for i in range(1, 7)]
    all_numbers = np.concatenate([df[col].dropna().values for col in num_cols])
    number_counts = Counter(all_numbers.astype(int))
    
    # 1. 頻出数字 (ホットナンバー)
    hot_numbers = [n[0] for n in number_counts.most_common(6)]
    
    # 2. 低頻度数字 (コールドナンバー)
    cold_numbers = [n[0] for n in number_counts.most_common()[-6:]]

    # 3. 直近の数字と被らないように、中程度の頻度の数字を選ぶ
    last_nums = set(df.sort_values('date', ascending=False).iloc[0][num_cols].astype(int))
    
    mid_freq_candidates = [
        num for num, count in number_counts.items() 
        if num not in last_nums and count > np.median(list(number_counts.values()))
    ]
    
    np.random.seed(len(df)) # 再現性のためのシード
    if len(mid_freq_candidates) >= 6:
        recent_avoid_pred = sorted(np.random.choice(mid_freq_candidates, 6, replace=False).tolist())
    else:
        # 足りない場合はホットナンバーで補う
        filler = [n for n in hot_numbers if n not in mid_freq_candidates]
        needed = 6 - len(mid_freq_candidates)
        combined = mid_freq_candidates + filler[:needed]
        recent_avoid_pred = sorted(combined)


    predictions = [
        sorted(hot_numbers),
        sorted(cold_numbers),
        recent_avoid_pred
    ]
    
    # 重複を除き、top_n個を返す
    unique_preds = []
    for p in predictions:
        if p not in unique_preds:
            unique_preds.append(p)
            
    return unique_preds[:top_n]


# =============================================================================
# Model 3: ML-based Prediction
# (newly created, similar to Numbers4)
# =============================================================================

def predict_with_model(model_weights, top_n=12, exclude_last_draw=None):
    """
    学習済みモデルの重みに基づいて、確率的に有望な組み合わせを予測します。
    """
    if model_weights is None:
        return []

    all_predictions = set()
    
    # 各桁の確率分布を取得
    number_probs = model_weights['number_probabilities']
    
    # 確率の高い数字をプールする
    # Loto6では桁の区別がないため、全数字の確率を一つのリストにまとめる
    prob_df = pd.DataFrame(number_probs, index=[0]).T
    prob_df['avg_prob'] = prob_df.mean(axis=1)
    
    # 平均確率上位20件を候補とする
    candidate_pool = prob_df.nlargest(20, 'avg_prob').index.astype(int).tolist()

    if len(candidate_pool) < 6:
        # プールが小さすぎる場合は、全数字を対象にする
        candidate_pool = list(range(1, 44))

    # 候補の中からランダムに6個選ぶことを繰り返す
    # exclude_last_draw があれば、それと完全一致する組み合わせは除外
    
    # 再現性のためシードを設定
    np.random.seed(len(candidate_pool))

    while len(all_predictions) < top_n * 50: # 十分な候補を生成
        pred = tuple(sorted(np.random.choice(candidate_pool, 6, replace=False)))
        if exclude_last_draw and pred == tuple(sorted(exclude_last_draw)):
            continue
        all_predictions.add(pred)
        if len(all_predictions) >= top_n * 2: # ある程度の数で打ち切り
            break

    # スコアリングは単純化し、ここでは省略。ランダム選択したものを返す。
    final_predictions = [list(p) for p in all_predictions]
    
    return final_predictions[:top_n]

# groupbyのインポート
from itertools import groupby

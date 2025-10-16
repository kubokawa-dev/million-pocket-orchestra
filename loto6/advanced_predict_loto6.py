import os
import pandas as pd
import numpy as np
import glob
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime

RANDOM_SEED = 2042  # 再現性のため固定
np.random.seed(RANDOM_SEED)

NUM_RANGE = list(range(1, 44))  # 1..43
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 43)]

COLS = [
    'kai', 'date', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus',
    '1st_winners', '1st_prize', '2nd_winners', '2nd_prize',
    '3rd_winners', '3rd_prize', '4th_winners', '4th_prize',
    '5th_winners', '5th_prize', 'carryover'
]


ROOT = os.path.dirname(os.path.dirname(__file__))


def load_data(pattern=None) -> pd.DataFrame:
    if pattern is None:
        pattern = os.path.join(ROOT, 'loto6', '*.csv')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError('loto6 CSVが見つかりませんでした。')
    df_list = []
    for f in files:
        tmp = pd.read_csv(f, header=None, names=COLS, dtype=str)
        df_list.append(tmp)
    df = pd.concat(df_list, ignore_index=True)
    # 数値化
    num_cols = [f'num{i}' for i in range(1, 7)]
    for c in num_cols + ['bonus']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    # 日付
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
    df.dropna(subset=num_cols, inplace=True)
    for c in num_cols:
        df[c] = df[c].astype(int)
    return df


def compute_stats(df: pd.DataFrame):
    num_cols = [f'num{i}' for i in range(1, 7)]
    # 頻度
    all_numbers = np.concatenate([df[c].values for c in num_cols])
    freq = Counter(all_numbers)

    # 未出現/経過回数 (overdue): 最新からの未出現回数
    last_seen = {n: -1 for n in NUM_RANGE}
    for idx, row in enumerate(df.sort_values('date_dt')[[*num_cols, 'date_dt']].itertuples(index=False)):
        nums = [getattr(row, c) for c in num_cols]
        for n in nums:
            last_seen[n] = idx
    max_idx = len(df) - 1
    overdue = {n: (max_idx - last_seen[n]) if last_seen[n] >= 0 else max_idx + 1 for n in NUM_RANGE}

    # ペア頻度
    pair_counts = defaultdict(int)
    for _, row in df.iterrows():
        nums = sorted([int(row[c]) for c in num_cols])
        for a, b in combinations(nums, 2):
            pair_counts[(a, b)] += 1

    # 偶奇バランス
    def eo(row):
        ev = sum(1 for c in num_cols if row[c] % 2 == 0)
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
    decade_counts = Counter(df.apply(lambda r: decade_signature([int(r[c]) for c in num_cols]), axis=1))

    # 直近の出目
    last_row = df.sort_values('date_dt').iloc[-1]
    last_tuple = tuple(sorted(int(last_row[c]) for c in num_cols))
    last_set = set(last_tuple)

    return {
        'freq': freq,
        'overdue': overdue,
        'pair_counts': pair_counts,
        'eo_counts': eo_counts,
        'sum_stats': sum_stats,
        'decade_counts': decade_counts,
        'last_set': last_set,
        'last_tuple': last_tuple,
    }


def score_combination(combo, stats):
    combo = sorted(combo)
    freq = stats['freq']
    overdue = stats['overdue']
    pair_counts = stats['pair_counts']
    eo_counts = stats['eo_counts']
    sum_stats = stats['sum_stats']
    decade_counts = stats['decade_counts']
    last_set = stats['last_set']

    # スコア要素
    # 1) 個別頻度 (標準化)
    f_vals = np.array([freq.get(n, 0) for n in combo], dtype=float)
    if len(freq) > 0:
        f_max = max(freq.values())
        freq_score = f_vals.sum() / (f_max * 6)
    else:
        freq_score = 0.0

    # 2) overdue: 適度に未出現が長いほど少し加点 (上限クリップ)
    ov_vals = np.array([overdue.get(n, 0) for n in combo], dtype=float)
    ov_score = np.tanh(ov_vals.mean() / 10.0)  # 0..~1 に収束

    # 3) ペア相性: 組内のペア頻度合計
    pairs = list(combinations(combo, 2))
    pair_score_raw = sum(pair_counts.get(tuple(p), 0) for p in pairs)
    # 過度な依存を避けるため sqrt 正規化
    pair_score = np.sqrt(pair_score_raw) / 10.0

    # 4) 偶奇・和の制約に対する適合度
    evens = sum(1 for n in combo if n % 2 == 0)
    odds = 6 - evens
    eo_key = f'偶数{evens}:奇数{odds}'
    eo_freq_total = sum(eo_counts.values()) or 1
    eo_score = eo_counts.get(eo_key, 0) / eo_freq_total

    s = sum(combo)
    mu = float(sum_stats['mean'])
    sd = float(sum_stats['std'] or 1.0)
    # 平均±1σに近いほど良い (ガウス評価)
    sum_score = np.exp(-((s - mu) ** 2) / (2 * (sd ** 2)))

    # 5) ディケード分布の適合
    def signature(nums):
        return tuple(sum(1 for n in nums if lo <= n <= hi) for (lo, hi) in DECADES)
    sig = signature(combo)
    dec_total = sum(decade_counts.values()) or 1
    decade_score = decade_counts.get(sig, 0) / dec_total

    # 6) 連番ペナルティ (連続数が3以上で減点)
    consec = 1
    max_consec = 1
    for i in range(1, 6):
        if combo[i] == combo[i - 1] + 1:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 1
    consec_penalty = 0.2 if max_consec >= 3 else 0.0

    # 7) 直近と過剰に被る組み合わせを軽く減点
    overlap = len(set(combo) & last_set)
    overlap_penalty = 0.05 * max(0, overlap - 3)  # 4個以上被るとペナルティ加算

    # 総合スコア（重みは経験則）
    score = (
        0.35 * freq_score
        + 0.20 * ov_score
        + 0.15 * pair_score
        + 0.10 * eo_score
        + 0.10 * sum_score
        + 0.10 * decade_score
        - consec_penalty
        - overlap_penalty
    )
    return float(score)


def generate_candidates(stats, mode='balanced', samples=3000):
    freq = stats['freq']
    overdue = stats['overdue']

    # プール構成
    hot = [n for n, _ in freq.most_common(20)]
    cold = [n for n, _ in sorted(freq.items(), key=lambda x: x[1])[:15]]
    overdue_top = [n for n, _ in sorted(overdue.items(), key=lambda x: x[1], reverse=True)[:15]]

    pool = set(hot + cold + overdue_top)
    pool = sorted([n for n in pool if 1 <= n <= 43])
    if len(pool) < 12:
        pool = sorted(list(set(pool) | set(range(1, 44))))

    # モード別の比率
    if mode == 'hot':
        weights = np.array([2.0 if n in hot else 1.0 for n in pool])
    elif mode == 'overdue':
        weights = np.array([2.0 if n in overdue_top else 1.0 for n in pool])
    elif mode == 'pair':
        # ペア向けは一旦均等だが後のスコアで最適化
        weights = np.ones(len(pool))
    else:  # balanced
        weights = np.array([1.5 if n in hot else (1.3 if n in overdue_top else 1.0) for n in pool])

    weights = weights / weights.sum()

    best = []
    best_set = set()

    for _ in range(samples):
        # 候補生成（重複なし）
        cand = np.random.choice(pool, size=6, replace=False, p=weights)
        cand.sort()
        tup = tuple(int(x) for x in cand)
        if tup in best_set:
            continue
        # exclude exactly the latest winning set
        if tup == stats.get('last_tuple'):
            continue
        sc = score_combination(tup, stats)
        best.append((sc, tup))
        best_set.add(tup)

    # 上位を返す
    best.sort(reverse=True, key=lambda x: x[0])
    return best[:50]


def format_combo(combo):
    return ' '.join(f"{n:02d}" for n in combo)


def predict():
    df = load_data()
    stats = compute_stats(df)

    # 4つの視点で候補生成
    hot_best = generate_candidates(stats, mode='hot', samples=3000)[0][1]
    bal_best = generate_candidates(stats, mode='balanced', samples=3000)[0][1]
    overdue_best = generate_candidates(stats, mode='overdue', samples=3000)[0][1]
    pair_best = generate_candidates(stats, mode='pair', samples=3000)[0][1]

    print('--- ロト6 高度予想 (第2042回) ---')
    print('視点: 頻出/ホット')
    print('  →', format_combo(hot_best))
    print('視点: バランス')
    print('  →', format_combo(bal_best))
    print('視点: 未出現/オーバーデュ')
    print('  →', format_combo(overdue_best))
    print('視点: ペア相性')
    print('  →', format_combo(pair_best))

    # 参考: 統計サマリー
    eo_summary = ', '.join([f"{k}:{v}" for k, v in stats['eo_counts'].most_common(3)])
    mu = float(stats['sum_stats']['mean'])
    smin = int(stats['sum_stats']['min'])
    smax = int(stats['sum_stats']['max'])
    print('\n傾向メモ:')
    print(f"  偶奇バランスTop: {eo_summary}")
    print(f"  合計値レンジ: {smin}〜{smax} (平均≈{mu:.1f})")

    return {
        'hot': hot_best,
        'balanced': bal_best,
        'overdue': overdue_best,
        'pair': pair_best,
        'eo_summary': eo_summary,
        'sum_range': (smin, smax, mu),
    }


if __name__ == '__main__':
    predict()

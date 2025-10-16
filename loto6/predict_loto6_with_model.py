import os
import json
import psycopg2
import itertools
import random
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_GLOB = os.path.join(ROOT, 'loto6', '*.csv')
STATE_PATH = os.path.join(ROOT, 'loto6', 'model_state.json')
RANDOM_SEED = 2042
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

NUM_RANGE = list(range(1, 44))
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 43)]


def get_latest_from_db():
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS loto6_draws (
              draw_number INTEGER PRIMARY KEY,
              draw_date TEXT NOT NULL,
              numbers TEXT NOT NULL,
              bonus_number INTEGER
            );
        ''')
        cur.execute('SELECT draw_number, draw_date, numbers, bonus_number FROM loto6_draws ORDER BY draw_number DESC LIMIT 1')
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        nums = tuple(sorted(int(x) for x in row[2].split(',')))
        return {
            'draw_number': int(row[0]),
            'draw_date': row[1],
            'numbers_tuple': nums,
            'bonus': int(row[3]) if row[3] is not None else None,
        }
    except Exception:
        return None


def load_state():
    if not os.path.exists(STATE_PATH):
        return None
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def compute_stats_from_state(state):
    # Convert learned state into a scoring-friendly structure
    freq_weights = {int(k): float(v) for k, v in state.get('weights_num', {}).items()}
    pair_weights = {}
    for k, v in state.get('weights_pair', {}).items():
        try:
            a, b = k.split('-')
            pair_weights[(int(a), int(b))] = float(v)
        except Exception:
            continue
    eo_probs = state.get('eo_probs', {})
    dec_probs = state.get('decade_probs', {})
    last_tuple = tuple(state.get('last_numbers', []))
    last_set = set(last_tuple)
    sum_mu = float(state.get('sum', {}).get('mean', 130.0))
    sum_sd = float(state.get('sum', {}).get('std', 15.0) or 15.0)

    return {
        'freq_weights': freq_weights,
        'pair_weights': pair_weights,
        'eo_probs': eo_probs,
        'dec_probs': dec_probs,
        'last_tuple': last_tuple,
        'last_set': last_set,
        'sum_mu': sum_mu,
        'sum_sd': sum_sd,
    }


def score_combo(combo, stats):
    combo = tuple(sorted(combo))
    freq_w = stats['freq_weights']
    pair_w = stats['pair_weights']
    eo_probs = stats['eo_probs']
    dec_probs = stats['dec_probs']
    last_set = stats['last_set']
    mu = stats['sum_mu']
    sd = stats['sum_sd']

    # frequency component (normalized)
    fw_vals = [freq_w.get(n, 1.0) for n in combo]
    freq_score = (np.mean(fw_vals) - 1.0) / 1.0  # center around 0

    # pair component
    pairs = list(itertools.combinations(combo, 2))
    pw_vals = [pair_w.get(tuple(sorted(p)), 1.0) for p in pairs]
    pair_score = (np.mean(pw_vals) - 1.0) / 1.0

    # eo component
    evens = sum(1 for n in combo if n % 2 == 0)
    odds = 6 - evens
    eo_key = f'偶数{evens}:奇数{odds}'
    eo_score = float(eo_probs.get(eo_key, 1.0 / 7.0))

    # sum component (Gaussian)
    s = sum(combo)
    sum_score = float(np.exp(-((s - mu) ** 2) / (2 * (sd ** 2))))

    # decade component
    def signature(nums):
        return ','.join(str(sum(1 for n in nums if lo <= n <= hi)) for (lo, hi) in DECADES)
    dec = signature(combo)
    decade_score = float(dec_probs.get(dec, 0.0))

    consec = 1
    max_consec = 1
    for i in range(1, 6):
        if combo[i] == combo[i - 1] + 1:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 1
    consec_penalty = 0.2 if max_consec >= 3 else 0.0

    overlap = len(set(combo) & last_set)
    overlap_penalty = 0.05 * max(0, overlap - 3)

    score = (
        0.35 * freq_score
        + 0.20 * pair_score
        + 0.15 * eo_score
        + 0.15 * sum_score
        + 0.15 * decade_score
        - consec_penalty
        - overlap_penalty
    )
    return float(score)


def generate(stats, mode='balanced', samples=5000):
    # Build a sampling pool guided by learned per-number weights
    freq_w = stats['freq_weights']
    # Rank by weight to define hot/cold
    hot = sorted(NUM_RANGE, key=lambda n: freq_w.get(n, 1.0), reverse=True)[:20]
    cold = sorted(NUM_RANGE, key=lambda n: freq_w.get(n, 1.0))[:15]

    pool = sorted(set(hot + cold) | set(NUM_RANGE))

    base = []
    for n in pool:
        if mode == 'hot':
            v = 2.0 if n in hot else 1.0
        elif mode == 'overdue':
            # approximate overdue by inverse of weight
            v = 2.0 if n in cold else 1.0
        else:
            v = 1.5 if n in hot else 1.0
        v *= freq_w.get(n, 1.0)
        base.append(v)
    weights = np.array(base, dtype=float)
    weights = weights / weights.sum()

    best = []
    best_set = set()
    for _ in range(samples):
        cand = np.random.choice(pool, size=6, replace=False, p=weights)
        cand.sort()
        tup = tuple(int(x) for x in cand)
        if tup in best_set:
            continue
        if tup == stats.get('last_tuple'):
            continue
        sc = score_combo(tup, stats)
        best.append((sc, tup))
        best_set.add(tup)
    best.sort(reverse=True, key=lambda x: x[0])
    return best[:50]


def main():
    state = load_state()
    if state is None:
        print('[loto6-model] No learned state found. Run update_loto6_model_from_sqlite.py first.')
        return
    stats = compute_stats_from_state(state)
    hot = generate(stats, 'hot', samples=6000)[0][1]
    bal = generate(stats, 'balanced', samples=6000)[0][1]
    ov = generate(stats, 'overdue', samples=6000)[0][1]
    pair = generate(stats, 'balanced', samples=6000)[1][1]

    def fmt(t):
        return ' '.join(f'{n:02d}' for n in t)

    print('--- ロト6 モデルベース予測 ---')
    print('視点: 頻出/ホット ->', fmt(hot))
    print('視点: バランス     ->', fmt(bal))
    print('視点: 未出現       ->', fmt(ov))
    print('視点: ペア相性     ->', fmt(pair))


if __name__ == '__main__':
    main()

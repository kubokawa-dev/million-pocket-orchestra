import json
import os
import sqlite3
from datetime import datetime
from collections import Counter, defaultdict
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'millions.sqlite')
STATE_PATH = os.path.join(ROOT, 'loto6', 'model_state.json')


def fetch_all_draws():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS loto6_draws (
               draw_number INTEGER PRIMARY KEY,
               draw_date TEXT NOT NULL,
               numbers TEXT NOT NULL,
               bonus_number INTEGER
           );'''
    )
    cur.execute('SELECT draw_number, draw_date, numbers, bonus_number FROM loto6_draws ORDER BY draw_number ASC')
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        try:
            nums = [int(x) for x in str(r[2]).split(',') if x.strip().isdigit()]
            if len(nums) != 6:
                continue
            out.append({
                'draw_number': int(r[0]),
                'draw_date': r[1],
                'nums': sorted(nums),
                'bonus': int(r[3]) if r[3] is not None else None,
            })
        except Exception:
            continue
    return out


def compute_model(draws):
    # Learned distributions from full history
    num_counts = Counter()
    pair_counts = Counter()
    eo_counts = Counter()
    decade_counts = Counter()
    sums = []

    def decade_sig(nums):
        bands = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 43)]
        return tuple(sum(1 for n in nums if lo <= n <= hi) for lo, hi in bands)

    for d in draws:
        nums = d['nums']
        num_counts.update(nums)
        for a, b in combinations(sorted(nums), 2):
            pair_counts[(a, b)] += 1
        evens = sum(1 for n in nums if n % 2 == 0)
        odds = 6 - evens
        eo_counts[(evens, odds)] += 1
        decade_counts[decade_sig(nums)] += 1
        sums.append(sum(nums))

    # Normalize to weights/probs
    eps = 1e-6
    total_draws = max(1, len(draws))
    mean_sum = float(sum(sums) / total_draws) if sums else 120.0
    var_sum = float(sum((s - mean_sum) ** 2 for s in sums) / total_draws) if sums else 400.0

    # Per-number weights: 1.0 + freq / avg_freq
    avg_freq = (6 * total_draws) / 43.0 if total_draws else 1.0
    weights_num = {str(n): float(1.0 + (num_counts.get(n, 0) / max(eps, avg_freq))) for n in range(1, 44)}

    # Pair weights: 1.0 + freq / avg_pair_freq
    total_pairs = 15 * total_draws
    avg_pair_freq = total_pairs / (43 * 42 / 2.0) if total_draws else 1.0
    weights_pair = {f"{a}-{b}": float(1.0 + (pair_counts.get((a, b), 0) / max(eps, avg_pair_freq)))
                    for a in range(1, 44) for b in range(a + 1, 44)}

    # EO probabilities
    eo_total = sum(eo_counts.values()) or 1
    eo_probs = {f"偶数{e}:奇数{o}": float((eo_counts.get((e, o), 0) + 0.1) / (eo_total + 0.1 * 7))
                for e in range(0, 7) for o in range(0, 7) if e + o == 6}

    # Decade probabilities
    dec_total = sum(decade_counts.values()) or 1
    # Only store seen signatures to keep size reasonable
    decade_probs = {','.join(map(str, sig)): float((cnt + 0.1) / (dec_total + 0.1 * len(decade_counts)))
                    for sig, cnt in decade_counts.items()}

    # Compose state
    last = draws[-1] if draws else None
    state = {
        'version': 2,
        'updated_at': datetime.utcnow().isoformat(),
        'last_learned_draw': int(last['draw_number']) if last else 0,
        'last_numbers': last['nums'] if last else [],
        'sum': {
            'mean': mean_sum,
            'std': float(var_sum ** 0.5),
        },
        'weights_num': weights_num,
        'weights_pair': weights_pair,
        'eo_probs': eo_probs,
        'decade_probs': decade_probs,
    }
    return state


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    draws = fetch_all_draws()
    if not draws:
        print('[loto6-learn] No draws found in SQLite.')
        return
    state = compute_model(draws)
    save_state(state)
    print(f"[loto6-learn] Rebuilt model from {len(draws)} draws. last={state['last_learned_draw']} mean={state['sum']['mean']:.1f} std={state['sum']['std']:.1f}")


if __name__ == '__main__':
    main()

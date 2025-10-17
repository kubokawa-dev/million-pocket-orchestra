import pandas as pd
import numpy as np
import glob
import os
import json
import psycopg2
from collections import Counter, defaultdict
from itertools import combinations

RANDOM_SEED = 4649  # 再現性のため固定（しごろ）
np.random.seed(RANDOM_SEED)

DIGITS = list(range(10))
COLS = [
    'kai', 'date', 'number', 's_kuchi', 's_kingaku', 'b_kuchi', 'b_kingaku',
    'set_s_kuchi', 'set_s_kingaku', 'set_b_kuchi', 'set_b_kingaku'
]


ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(ROOT, 'numbers4', 'model_state.json')


def load_data(pattern=None) -> pd.DataFrame:
    if pattern is None:
        pattern = os.path.join(ROOT, 'numbers4', '*.csv')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError('numbers4 CSVが見つかりませんでした。')
    df_list = []
    for f in files:
        tmp = pd.read_csv(f, header=None, names=COLS, dtype=str)
        df_list.append(tmp)
    df = pd.concat(df_list, ignore_index=True)
    # number -> 4桁文字列
    df['number_str'] = df['number'].astype(str).str.zfill(4)
    # 各桁
    for i in range(4):
        df[f'd{i+1}'] = df['number_str'].str[i].astype(int)
    return df


def load_model_prior():
    try:
        with open(MODEL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            pos = data.get('pos_probs')
            if isinstance(pos, list) and len(pos) == 4 and all(len(row) == 10 for row in pos):
                return [list(map(float, row)) for row in pos]
    except Exception:
        pass
    return [[0.1] * 10 for _ in range(4)]


from dotenv import load_dotenv

load_dotenv()

def get_latest_numbers4():
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        con = psycopg2.connect(db_url)
        cur = con.cursor()
        cur.execute("SELECT numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1")
        row = cur.fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None


def pattern_class(digs):
    # 例: [1,2,3,4] -> (1,1,1,1), [1,1,2,3] -> (2,1,1), [1,1,2,2] -> (2,2), [1,1,1,2] -> (3,1), [1,1,1,1] -> (4)
    cnt = Counter(digs)
    parts = tuple(sorted(cnt.values(), reverse=True))
    return parts


def compute_stats(df: pd.DataFrame):
    # 全体頻度
    overall = Counter(''.join(df['number_str']))  # 文字でカウント
    overall_freq = {int(k): v for k, v in overall.items()}
    for d in DIGITS:
        overall_freq.setdefault(d, 0)

    # 位置別頻度
    pos_freq = [Counter(df[f'd{i+1}']) for i in range(4)]
    for i in range(4):
        for d in DIGITS:
            pos_freq[i].setdefault(d, 0)

    # overdue（最新からの未出現回数）: 全体 + 各桁位置
    # インデックス順を時系列とみなす（ファイルは月単位、concat順で概ね時系列）
    last_seen_overall = {d: -1 for d in DIGITS}
    last_seen_pos = [{d: -1 for d in DIGITS} for _ in range(4)]
    for idx, row in enumerate(df.itertuples(index=False)):
        digs = [getattr(row, f'd{i+1}') for i in range(4)]
        for d in digs:
            last_seen_overall[d] = idx
        for i, d in enumerate(digs):
            last_seen_pos[i][d] = idx
    max_idx = len(df) - 1
    overdue_overall = {d: (max_idx - last_seen_overall[d]) if last_seen_overall[d] >= 0 else max_idx + 1 for d in DIGITS}
    overdue_pos = [
        {d: (max_idx - last_seen_pos[i][d]) if last_seen_pos[i][d] >= 0 else max_idx + 1 for d in DIGITS}
        for i in range(4)
    ]

    # 隣接ペア頻度（同一番号内の隣接）
    adj_pair = Counter()
    for _, row in df.iterrows():
        digs = [int(row[f'd{i+1}']) for i in range(4)]
        for i in range(3):
            adj_pair[(digs[i], digs[i+1])] += 1

    # 偶奇バランス
    def eo(digs):
        ev = sum(1 for x in digs if x % 2 == 0)
        od = 4 - ev
        return f'偶数{ev}:奇数{od}'
    eo_counts = Counter(df.apply(lambda r: eo([int(r['d1']), int(r['d2']), int(r['d3']), int(r['d4'])]), axis=1))

    # 合計値
    sums = df[[f'd{i+1}' for i in range(4)]].sum(axis=1)
    sum_stats = sums.describe()

    # パターン分布
    patt_counts = Counter(df.apply(lambda r: pattern_class([int(r['d1']), int(r['d2']), int(r['d3']), int(r['d4'])]), axis=1))

    # 直近セット
    last_digs = [int(df.iloc[-1][f'd{i+1}']) for i in range(4)]

    return {
        'overall_freq': overall_freq,
        'pos_freq': pos_freq,
        'overdue_overall': overdue_overall,
        'overdue_pos': overdue_pos,
        'adj_pair': adj_pair,
        'eo_counts': eo_counts,
        'sum_stats': sum_stats,
        'patt_counts': patt_counts,
        'last_digs': last_digs,
    }


def score_candidate(digs, st):
    overall = st['overall_freq']
    posf = st['pos_freq']
    over_o = st['overdue_overall']
    over_p = st['overdue_pos']
    adjp = st['adj_pair']
    eo_counts = st['eo_counts']
    sum_stats = st['sum_stats']
    patt_counts = st['patt_counts']
    last_digs = st['last_digs']

    d1, d2, d3, d4 = digs

    # 1) 位置頻度 + 全体頻度
    pf = sum(posf[i][digs[i]] for i in range(4))
    pf_max = max(sum(c.values()) for c in posf) or 1
    pos_score = pf / (pf_max * 4)

    of = sum(overall[d] for d in digs)
    of_max = max(overall.values()) or 1
    overall_score = of / (of_max * 4)

    # 2) overdue（全体 + 位置平均）
    ov_all = np.mean([over_o[d] for d in digs])
    ov_pos = np.mean([over_p[i][digs[i]] for i in range(4)])
    overdue_score = 0.5 * np.tanh(ov_all / 10.0) + 0.5 * np.tanh(ov_pos / 10.0)

    # 3) 隣接ペア相性
    adj_raw = adjp.get((d1, d2), 0) + adjp.get((d2, d3), 0) + adjp.get((d3, d4), 0)
    adj_score = np.sqrt(adj_raw) / 5.0

    # 4) 偶奇・合計・パターン適合
    ev = sum(1 for x in digs if x % 2 == 0)
    eo_key = f'偶数{ev}:奇数{4-ev}'
    eo_total = sum(eo_counts.values()) or 1
    eo_score = eo_counts.get(eo_key, 0) / eo_total

    s = sum(digs)
    mu = float(sum_stats['mean'])
    sd = float(sum_stats['std'] or 1.0)
    sum_score = np.exp(-((s - mu) ** 2) / (2 * (sd ** 2)))

    patt = pattern_class(digs)
    patt_total = sum(patt_counts.values()) or 1
    patt_score = patt_counts.get(patt, 0) / patt_total

    # 5) 連番ペナルティ（連続3以上で減点）
    consec = 1
    maxc = 1
    for a, b in zip(digs, digs[1:]):
        if b == a + 1 or b == a - 1:
            consec += 1
            maxc = max(maxc, consec)
        else:
            consec = 1
    consec_penalty = 0.15 if maxc >= 3 else 0.0

    # 6) 直近被りペナルティ（3個以上一致で軽減）
    overlap = sum(1 for a, b in zip(digs, last_digs) if a == b)
    overlap_penalty = 0.05 * max(0, overlap - 2)

    score = (
        0.30 * pos_score
        + 0.15 * overall_score
        + 0.20 * overdue_score
        + 0.15 * adj_score
        + 0.10 * eo_score
        + 0.05 * sum_score
        + 0.05 * patt_score
        - consec_penalty
        - overlap_penalty
    )
    return float(score)


def sample_candidates(st, mode='balanced', samples=40000):
    posf = st['pos_freq']
    overp = st['overdue_pos']
    prior = load_model_prior()

    # 位置ごとの重み設定
    weights = []
    for i in range(4):
        pf = np.array([posf[i][d] for d in DIGITS], dtype=float)
        pf = pf / (pf.sum() or 1)
        ov = np.array([overp[i][d] for d in DIGITS], dtype=float)
        ov = ov / (ov.sum() or 1)
        # blend with learned prior
        pri = np.array(prior[i], dtype=float)
        pri = pri / (pri.sum() or 1)
        if mode == 'hot':
            w = 0.7 * pf + 0.3 * pri
        elif mode == 'overdue':
            w = 0.6 * ov + 0.4 * pri
        elif mode == 'cold':
            # 低頻度を重視（逆数）
            w = 0.6 * (1.0 - pf) + 0.4 * pri
            w = w / (w.sum() or 1)
        else:  # balanced
            w = 0.5 * pf + 0.3 * ov + 0.2 * pri
        weights.append(w)

    best = []
    seen = set()

    for _ in range(samples):
        digs = [
            int(np.random.choice(DIGITS, p=weights[i])) for i in range(4)
        ]
        tup = tuple(digs)
        if tup in seen:
            continue
        seen.add(tup)
        sc = score_candidate(digs, st)
        best.append((sc, tup))

    best.sort(reverse=True, key=lambda x: x[0])
    return best[:300]


def fmt(digs):
    return ''.join(str(d) for d in digs)


def predict():
    df = load_data()
    st = compute_stats(df)
    latest = get_latest_numbers4()

    # まず各モードで上位候補リストを取得
    hot_list = [t[1] for t in sample_candidates(st, 'hot', samples=25000)]
    bal_list = [t[1] for t in sample_candidates(st, 'balanced', samples=40000)]
    ovd_list = [t[1] for t in sample_candidates(st, 'overdue', samples=25000)]
    cold_list = [t[1] for t in sample_candidates(st, 'cold', samples=25000)]

    # 可能な限り異なる特徴の組み合わせを選ぶ
    used = set()
    picks = {}

    def pick_distinct(cands, label):
        for digs in cands:
            if digs in used:
                continue
            # すでに選んだものとパターン/偶奇が極端に被る場合はスキップして次を検討
            patt = pattern_class(digs)
            ev = sum(1 for x in digs if x % 2 == 0)
            eo_key = f'偶数{ev}:奇数{4-ev}'
            conflict = False
            for _, prev in picks.items():
                if pattern_class(prev) == patt and sum(1 for x in prev if x % 2 == 0) == ev:
                    conflict = True
                    break
            if conflict:
                continue
            used.add(digs)
            picks[label] = digs
            return digs
        # すべて被るなら最上位を許容
        digs = cands[0]
        used.add(digs)
        picks[label] = digs
        return digs

    def not_latest(d):
        s = fmt(d)
        return (latest is None) or (s != latest)

    hot = next((d for d in hot_list if not_latest(d)), hot_list[0])
    used.add(hot)
    picks['hot'] = hot

    bal = next((d for d in bal_list if not_latest(d) and d not in used), bal_list[0])
    used.add(bal)
    picks['balanced'] = bal

    ovd = next((d for d in ovd_list if not_latest(d) and d not in used), ovd_list[0])
    used.add(ovd)
    picks['overdue'] = ovd

    cold = next((d for d in cold_list if not_latest(d) and d not in used), cold_list[0])
    used.add(cold)
    picks['cold'] = cold

    print('--- ナンバーズ4 高度予想 ---')
    print('視点: 頻出/ホット  →', fmt(hot))
    print('視点: バランス      →', fmt(bal))
    print('視点: 未出現/オーバーデュ →', fmt(ovd))
    print('視点: 低頻度/コールド →', fmt(cold))

    # 参照: 分布サマリ
    eo_top = ', '.join([f"{k}:{v}" for k, v in st['eo_counts'].most_common(3)])
    mu = float(st['sum_stats']['mean'])
    smin = int(st['sum_stats']['min'])
    smax = int(st['sum_stats']['max'])
    print('\n傾向メモ:')
    print(f'  偶奇Top: {eo_top}')
    print(f'  合計レンジ: {smin}〜{smax} (平均≈{mu:.1f})')

    return {
        'hot': hot,
        'balanced': bal,
        'overdue': ovd,
        'cold': cold,
        'eo_top': eo_top,
        'sum_range': (smin, smax, mu),
    }


if __name__ == '__main__':
    predict()

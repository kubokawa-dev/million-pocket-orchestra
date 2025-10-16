import json
import os
import random
from typing import List, Tuple
import psycopg2
import glob
import pandas as pd
import numpy as np
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(ROOT_DIR, 'numbers4', 'model_state.json')
CSV_PATTERN = os.path.join(ROOT_DIR, 'numbers4', '*.csv')

random.seed(4649)


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError('model_state.json not found. Run learn_from_predictions.py first.')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_latest_numbers4() -> str | None:
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


def load_history_stats():
    files = sorted(glob.glob(CSV_PATTERN))
    if not files:
        return None
    COLS = [
        'kai', 'date', 'number', 's_kuchi', 's_kingaku', 'b_kuchi', 'b_kingaku',
        'set_s_kuchi', 'set_s_kingaku', 'set_b_kuchi', 'set_b_kingaku'
    ]
    df_list = []
    for f in files:
        try:
            tmp = pd.read_csv(f, header=None, names=COLS, dtype=str)
            df_list.append(tmp)
        except Exception:
            continue
    if not df_list:
        return None
    df = pd.concat(df_list, ignore_index=True)
    df['number_str'] = df['number'].astype(str).str.zfill(4)
    for i in range(4):
        df[f'd{i+1}'] = df['number_str'].str[i].astype(int)

    # 偶奇カウント
    def eo(digs):
        ev = sum(1 for x in digs if x % 2 == 0)
        return f'偶数{ev}:奇数{4-ev}'
    eo_counts = Counter(df.apply(lambda r: eo([int(r['d1']), int(r['d2']), int(r['d3']), int(r['d4'])]), axis=1))

    # 合計値の統計
    sums = df[[f'd{i+1}' for i in range(4)]].sum(axis=1)
    sum_stats = sums.describe()

    # 隣接ペア頻度
    adj_pair = Counter()
    for _, row in df.iterrows():
        digs = [int(row[f'd{i+1}']) for i in range(4)]
        for i in range(3):
            adj_pair[(digs[i], digs[i+1])] += 1

    # 直近番号
    last_digs = [int(df.iloc[-1][f'd{i+1}']) for i in range(4)]

    # パターン（重複構成）
    def pattern_class(digs):
        cnt = Counter(digs)
        parts = tuple(sorted(cnt.values(), reverse=True))
        return parts
    patt_counts = Counter(df.apply(lambda r: pattern_class([int(r['d1']), int(r['d2']), int(r['d3']), int(r['d4'])]), axis=1))

    return {
        'eo_counts': eo_counts,
        'sum_stats': sum_stats,
        'adj_pair': adj_pair,
        'last_digs': last_digs,
        'patt_counts': patt_counts,
    }


def sample_from_probs(probs: List[float]) -> int:
    # simple categorical sampling
    r = random.random()
    cum = 0.0
    for i, p in enumerate(probs):
        cum += p
        if r <= cum:
            return i
    return len(probs) - 1


def predict_top_k(k: int = 10) -> List[str]:
    st = load_model(MODEL_PATH)
    pos_probs = st['pos_probs']
    hist = load_history_stats()
    latest = get_latest_numbers4()

    candidates: List[Tuple[float, str]] = []

    # generate many samples and keep the highest joint probability ones
    for _ in range(50000):
        digs = [sample_from_probs(pos_probs[i]) for i in range(4)]
        # base prob (joint)
        prob = 1.0
        for i in range(4):
            prob *= pos_probs[i][digs[i]]

        score = prob

        if hist is not None:
            # 偶奇スコア
            ev = sum(1 for x in digs if x % 2 == 0)
            eo_key = f'偶数{ev}:奇数{4-ev}'
            eo_total = sum(hist['eo_counts'].values()) or 1
            eo_score = hist['eo_counts'].get(eo_key, 0) / eo_total

            # 合計スコア（正規形）
            s = sum(digs)
            mu = float(hist['sum_stats']['mean'])
            sd = float(hist['sum_stats']['std'] or 1.0)
            sum_score = np.exp(-((s - mu) ** 2) / (2 * (sd ** 2)))

            # パターンスコア
            cnt = Counter(digs)
            patt = tuple(sorted(cnt.values(), reverse=True))
            patt_total = sum(hist['patt_counts'].values()) or 1
            patt_score = hist['patt_counts'].get(patt, 0) / patt_total

            # 隣接スコア
            ap = hist['adj_pair']
            adj_raw = ap.get((digs[0], digs[1]), 0) + ap.get((digs[1], digs[2]), 0) + ap.get((digs[2], digs[3]), 0)
            adj_score = np.sqrt(adj_raw) / 5.0

            # 直近被りペナルティ
            last_digs = hist['last_digs']
            overlap = sum(1 for a, b in zip(digs, last_digs) if a == b)
            overlap_penalty = 0.05 * max(0, overlap - 2)

            # 総合スコア（重みは高度版に近い配分）
            score = (
                0.50 * score +         # モデルの結合確率を主軸
                0.12 * eo_score +
                0.08 * sum_score +
                0.05 * patt_score +
                0.10 * adj_score -
                overlap_penalty
            )

        num = ''.join(str(d) for d in digs)
        candidates.append((float(score), num))

    # select top-k unique
    candidates.sort(reverse=True, key=lambda x: x[0])
    seen = set()
    result: List[str] = []
    for _, num in candidates:
        if num in seen:
            continue
        if latest and num == latest:
            # exclude latest exact match
            continue
        seen.add(num)
        result.append(num)
        if len(result) >= k:
            break
    return result


if __name__ == '__main__':
    nums = predict_top_k(12)
    print('Numbers4 model-based predictions:')
    print(', '.join(nums))

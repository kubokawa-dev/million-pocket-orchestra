"""
予測結果から学習するスクリプト（SQLite版）
"""
import json
import os
import re
import sys
import math
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Optional

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from tools.utils import get_db_connection

ADV_PATH = os.path.join(ROOT_DIR, 'numbers4', 'advanced_numbers4_prediction_result.md')
BASIC_PATH = os.path.join(ROOT_DIR, 'numbers4', 'prediction_result.md')
MODEL_PATH = os.path.join(ROOT_DIR, 'numbers4', 'model_state.json')

# 新機能のデフォルト設定（桁間相関・キャリブレーション・平滑化など）
# v10.7改善: 低確率数字にもチャンスを与える（1263問題対策）
CALIBRATION_DEFAULT = 1.20  # 1.15→1.20 分布をより平滑化
SMOOTH_MIN_PROB = 0.06      # 0.04→0.06 最低確率を6%に引き上げ（どの数字も6%以上）
SMOOTH_TEMPERATURE = 1.6    # 1.4→1.6 温度を上げて分布を平滑化
RECENCY_DECAY = 0.975       # 0.985→0.975 古いデータをより忘れる（新しいパターンに適応）
ROLLING_METRICS_WINDOW = 30

# -----------------------------
# Utilities
# -----------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


# -----------------------------
# SQLite Setup
# -----------------------------

def ensure_tables(conn):
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS numbers4_model_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_ts TEXT NOT NULL,
            actual_number TEXT NOT NULL,
            predictions TEXT NOT NULL,
            hit_exact INTEGER NOT NULL DEFAULT 0,
            top_match TEXT,
            max_position_hits INTEGER NOT NULL,
            notes TEXT
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS numbers4_predictions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL,
            label TEXT,
            number TEXT NOT NULL,
            target_draw_number INTEGER
        );
        '''
    )
    conn.commit()


# -----------------------------
# Parse prediction markdowns
# -----------------------------

def parse_advanced_md(path: str) -> List[Tuple[str, str, str]]:
    """Return list of (source, label, number) from advanced report."""
    out: List[Tuple[str, str, str]] = []
    if not os.path.exists(path):
        return out
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Find lines like: - `9660` under each viewpoint
    for label in ['頻出/ホット', 'バランス', '未出現/オーバーデュ', '低頻度/コールド']:
        # Collect the first 4-digit code block after the label line
        pattern = rf"{re.escape(label)}[\s\S]*?`(\d{{4}})`"
        m = re.search(pattern, text)
        if m:
            out.append(('advanced', label, m.group(1)))
    # Also catch any stray 4-digit numbers in backticks in the '予測結果' section
    for m in re.finditer(r"`(\d{4})`", text):
        tup = ('advanced', 'unlabeled', m.group(1))
        if tup not in out:
            out.append(tup)
    return out


def parse_basic_md(path: str) -> List[Tuple[str, str, str]]:
    out: List[Tuple[str, str, str]] = []
    if not os.path.exists(path):
        return out
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Format examples: `6185` or 「2039」 next to 【予想X】
    for m in re.finditer(r"【予想\s*([0-9一二三四五六七八九十]+)】[\s\S]*?[`「]?(\d{4})[`」]?", text):
        label = f"予想{m.group(1)}"
        out.append(('basic', label, m.group(2)))
    # Any backticked 4-digit values
    for m in re.finditer(r"`(\d{4})`", text):
        tup = ('basic', 'unlabeled', m.group(1))
        if tup not in out:
            out.append(tup)
    return out


def collect_predictions() -> List[Tuple[str, str, str]]:
    preds = []
    preds.extend(parse_advanced_md(ADV_PATH))
    preds.extend(parse_basic_md(BASIC_PATH))
    # Deduplicate by (source,label,number)
    seen = set()
    uniq = []
    for p in preds:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq


# -----------------------------
# Model state (per-position probabilities)
# -----------------------------

def load_model_state(path: str) -> Dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {}
    return ensure_state_schema(state)


def save_model_state(path: str, state: Dict):
    state['updated_at'] = now_iso()
    ensure_dirs(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def normalize(vec: List[float]) -> List[float]:
    s = sum(vec)
    if s <= 0:
        return [1.0/len(vec) for _ in vec]
    return [v / s for v in vec]


def apply_smoothing(vec: List[float], min_prob: float = 0.02, temperature: float = 1.3) -> List[float]:
    """
    確率分布に平滑化を適用（v10.4改善）
    
    問題: 学習の過程で特定の数字の確率が極端に高くなり、
          他の数字がほぼ0%になってしまう → 多様性が失われる
    
    解決策:
    1. 最低確率を保証（どの数字も min_prob 以上）
    2. 温度スケーリングで分布を平滑化
    
    Args:
        vec: 確率分布 (長さ10のリスト)
        min_prob: 最低確率（デフォルト: 0.02 = 2%）
        temperature: 温度パラメータ（>1で平滑化、デフォルト: 1.3）
    
    Returns:
        平滑化後の確率分布
    """
    import math
    
    # 最低確率を保証
    smoothed = [max(v, min_prob) for v in vec]
    
    # 温度スケーリング（p^(1/T)）
    if temperature != 1.0:
        smoothed = [v ** (1.0 / temperature) for v in smoothed]
    
    # 正規化
    total = sum(smoothed)
    if total > 0:
        smoothed = [v / total for v in smoothed]
    
    return smoothed


def init_pair_probs() -> List[List[List[float]]]:
    """桁間相関（隣接2桁の条件付き確率）を初期化"""
    return [
        [[0.1 for _ in range(10)] for _ in range(10)],  # pos0 -> pos1
        [[0.1 for _ in range(10)] for _ in range(10)],  # pos1 -> pos2
        [[0.1 for _ in range(10)] for _ in range(10)],  # pos2 -> pos3
    ]


def ensure_state_schema(state: Dict) -> Dict:
    """既存の状態に新しいキーを後方互換で追加"""
    if not state:
        state = {}
    state.setdefault('version', 2)
    state.setdefault('updated_at', None)
    state.setdefault('events', 0)
    state.setdefault('pos_probs', [[0.1 for _ in range(10)] for _ in range(4)])
    state.setdefault('pair_probs', init_pair_probs())
    state.setdefault('metadata', {})
    meta = state['metadata']
    meta.setdefault('calibration_temperature', CALIBRATION_DEFAULT)
    meta.setdefault('recent_metrics', [])
    meta.setdefault('pos_entropy', [])
    meta.setdefault('pair_entropy', [])
    meta.setdefault('top_boxes', [])
    meta.setdefault('top_numbers', [])
    return state


def calibrate_distribution(vec: List[float], temperature: float) -> List[float]:
    """温度スケーリングでキャリブレーション"""
    if temperature is None or abs(temperature - 1.0) < 1e-6:
        return vec
    return normalize([v ** (1.0 / temperature) for v in vec])


def apply_recency_decay(vec: List[float], decay: float) -> List[float]:
    """古い分布を薄める（忘却因子）"""
    base = (1.0 - decay) / len(vec)
    return normalize([v * decay + base for v in vec])


def apply_recency_decay_matrix(mat: List[List[float]], decay: float) -> List[List[float]]:
    return [apply_recency_decay(row, decay) for row in mat]


def entropy(vec: List[float]) -> float:
    """正規化エントロピー（0〜1）"""
    eps = 1e-12
    h = -sum(p * math.log(p + eps) for p in vec if p > 0)
    max_h = math.log(len(vec))
    return h / max_h if max_h > 0 else 0.0


def normalize_matrix(mat: List[List[float]]) -> List[List[float]]:
    return [normalize(row) for row in mat]


def rank_numbers_from_state(state: Dict, top_n: int = 50) -> List[Tuple[str, float]]:
    """
    桁間相関（pair_probs）を活用して4桁のjoint確率を計算し、上位を返す
    P(d0) * P(d1|d0) * P(d2|d1) * P(d3|d2)
    """
    pos = state['pos_probs']
    pair = state['pair_probs']
    results: List[Tuple[str, float]] = []
    for d0 in range(10):
        p0 = pos[0][d0]
        if p0 == 0:
            continue
        for d1 in range(10):
            p1 = pair[0][d0][d1]
            if p1 == 0:
                continue
            for d2 in range(10):
                p2 = pair[1][d1][d2]
                if p2 == 0:
                    continue
                for d3 in range(10):
                    p3 = pair[2][d2][d3]
                    if p3 == 0:
                        continue
                    prob = p0 * p1 * p2 * p3
                    results.append((''.join(map(str, [d0, d1, d2, d3])), prob))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def aggregate_boxes(top_numbers: List[Tuple[str, float]], top_k: int = 20) -> List[Tuple[str, float]]:
    """ボックス（順不同）で確率を集約し、上位を返す"""
    box_scores = {}
    for num, score in top_numbers:
        box_id = ''.join(sorted(num))
        box_scores[box_id] = box_scores.get(box_id, 0.0) + score
    ranked = sorted(box_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def update_state_with_event(state: Dict, actual: str, predictions: List[Tuple[str, str, str]]) -> Dict:
    """
    pos_probs: 桁ごとの事前分布
    pair_probs: 桁間の条件付き分布（d_i -> d_{i+1}）
    
    v11.1 改善: 中位候補（ML近傍探索など）を見逃さないように、
    予測候補を広めに反映させる
    """
    state = ensure_state_schema(state)
    temp = state['metadata'].get('calibration_temperature', CALIBRATION_DEFAULT)

    # 直近重視のため、既存分布を軽く減衰
    state['pos_probs'] = [apply_recency_decay(vec, RECENCY_DECAY) for vec in state['pos_probs']]
    state['pair_probs'] = [apply_recency_decay_matrix(mat, RECENCY_DECAY) for mat in state['pair_probs']]

    # 重み（v11.1: 予測候補の重みを強化 - 中位候補も反映）
    w_actual = 1.0
    # 改善: 上位100位まで重みを付与（従来は数件のみ）
    pred_weights = [0.5 * (0.95 ** i) for i in range(min(len(predictions), 100))]  # 減衰を緩やかに

    # per-position / pair targets
    targets = [[1e-3 for _ in range(10)] for _ in range(4)]
    pair_targets = [
        [[1e-3 for _ in range(10)] for _ in range(10)],
        [[1e-3 for _ in range(10)] for _ in range(10)],
        [[1e-3 for _ in range(10)] for _ in range(10)],
    ]

    # 予測を広めに反映（v11.1: 重みを増強）
    for rank, (_, _label, num) in enumerate(predictions[:100]):  # 上位100件まで
        w = pred_weights[rank] if rank < len(pred_weights) else 0.05
        digits = [int(ch) for ch in num[:4]]
        for i, d in enumerate(digits):
            targets[i][d] += 0.3 * w  # 0.2 → 0.3 に増強
        for i in range(3):
            a, b = digits[i], digits[i + 1]
            pair_targets[i][a][b] += 0.08 * w  # 0.05 → 0.08 に増強

    # 実際の当選を強く反映
    actual_digits = [int(ch) for ch in actual[:4]]
    for i, d in enumerate(actual_digits):
        targets[i][d] += w_actual
    for i in range(3):
        a, b = actual_digits[i], actual_digits[i + 1]
        pair_targets[i][a][b] += w_actual

    # pos_probs を更新（v11.1: 学習率を上げる）
    beta_pos = 0.20  # 0.15 → 0.20 に強化
    for i in range(4):
        tgt = normalize(targets[i])
        old = state['pos_probs'][i]
        mixed = [(1.0 - beta_pos) * old[d] + beta_pos * tgt[d] for d in range(10)]
        mixed = calibrate_distribution(mixed, temp)
        state['pos_probs'][i] = apply_smoothing(normalize(mixed), min_prob=SMOOTH_MIN_PROB, temperature=SMOOTH_TEMPERATURE)

    # pair_probs を更新（v11.1: 学習率を上げる）
    beta_pair = 0.15  # 0.12 → 0.15 に強化
    for i in range(3):
        tgt_mat = normalize_matrix(pair_targets[i])
        old_mat = state['pair_probs'][i]
        new_mat = []
        for a in range(10):
            row = [(1.0 - beta_pair) * old_mat[a][b] + beta_pair * tgt_mat[a][b] for b in range(10)]
            row = calibrate_distribution(row, temp)
            row = apply_smoothing(normalize(row), min_prob=SMOOTH_MIN_PROB / 2, temperature=SMOOTH_TEMPERATURE)
            new_mat.append(row)
        state['pair_probs'][i] = new_mat

    # 診断情報を更新（不確実性＋トップ候補）
    pos_entropy = [entropy(vec) for vec in state['pos_probs']]
    pair_entropy = [entropy([sum(row) / 10 for row in mat]) for mat in state['pair_probs']]
    top_numbers = rank_numbers_from_state(state, top_n=30)
    top_boxes = aggregate_boxes(top_numbers, top_k=15)

    metrics_entry = {
        'ts': now_iso(),
        'actual': actual,
        'top_hit': any(num == actual for _, _, num in predictions),
        'pos_entropy': pos_entropy,
        'pair_entropy': pair_entropy,
        'best_number': top_numbers[0][0] if top_numbers else None,
    }

    meta = state['metadata']
    meta['pos_entropy'] = pos_entropy
    meta['pair_entropy'] = pair_entropy
    meta['top_numbers'] = top_numbers[:10]
    meta['top_boxes'] = top_boxes
    # ローリングメトリクスを保持
    recent = meta.get('recent_metrics', [])
    recent.append(metrics_entry)
    meta['recent_metrics'] = recent[-ROLLING_METRICS_WINDOW:]

    state['events'] = int(state.get('events', 0)) + 1
    return state


# -----------------------------
# Evaluation helpers
# -----------------------------

def position_hits(actual: str, pred: str) -> int:
    return sum(1 for a, b in zip(actual[:4], pred[:4]) if a == b)


# -----------------------------
# Main entry
# -----------------------------

def learn(actual_number: str, actual_draw_number: int = None):
    actual_number = actual_number.strip()
    if not re.fullmatch(r"\d{4}", actual_number):
        raise ValueError("actual_number must be a 4-digit string like '6896'")

    preds = collect_predictions()

    # Load/update model
    state = load_model_state(MODEL_PATH)
    state = update_state_with_event(state, actual_number, preds)
    save_model_state(MODEL_PATH, state)

    # Evaluate predictions
    max_hit = -1
    top_match = None
    for _src, _label, num in preds:
        h = position_hits(actual_number, num)
        if h > max_hit:
            max_hit = h
            top_match = num

    # Log into SQLite
    conn = get_db_connection()
    ensure_tables(conn)
    cur = conn.cursor()
    
    # Get actual draw number if not provided
    if actual_draw_number is None:
        cur.execute("SELECT MAX(draw_number) FROM numbers4_draws")
        row = cur.fetchone()
        actual_draw_number = row[0] if row and row[0] else None

    preds_json = json.dumps([
        {'source': s, 'label': l, 'number': n} for (s, l, n) in preds
    ], ensure_ascii=False)

    cur.execute(
        '''
        INSERT INTO numbers4_model_events(
            event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            now_iso(),
            actual_number,
            preds_json,
            1 if any(n == actual_number for (_, _, n) in preds) else 0,
            top_match,
            int(max_hit if max_hit >= 0 else 0),
            'learn_from_predictions v1'
        )
    )

    # Also record predictions individually (optional)
    ts = now_iso()
    for s, l, n in preds:
        cur.execute(
            'INSERT INTO numbers4_predictions_log(created_at, source, label, number, target_draw_number) VALUES (?, ?, ?, ?, ?)',
            (ts, s, l, n, actual_draw_number)
        )

    conn.commit()
    conn.close()

    print('[learn] Updated model_state.json and logged training event.')
    print(f"[learn] Actual: {actual_number} | Predictions: {len(preds)} | Max position hits: {max_hit} (top: {top_match})")


if __name__ == '__main__':
    # Example usage: hard-coded actual for quick run; edit or call from CLI.
    # You can also integrate argparse if needed.
    if len(sys.argv) > 1:
        learn(sys.argv[1])
    else:
        learn('6896')

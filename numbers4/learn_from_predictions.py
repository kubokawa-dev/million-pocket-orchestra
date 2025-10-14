import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import List, Tuple, Dict

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT_DIR, 'millions.sqlite')
ADV_PATH = os.path.join(ROOT_DIR, 'numbers4', 'advanced_numbers4_prediction_result.md')
BASIC_PATH = os.path.join(ROOT_DIR, 'numbers4', 'prediction_result.md')
MODEL_PATH = os.path.join(ROOT_DIR, 'numbers4', 'model_state.json')

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

def get_conn(db_path: str):
    ensure_dirs(db_path)
    return sqlite3.connect(db_path)


def ensure_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS numbers4_model_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_ts TEXT NOT NULL,
            actual_number TEXT NOT NULL,
            predictions TEXT NOT NULL, -- JSON array of {source,label,number}
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
            number TEXT NOT NULL
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
            return json.load(f)
    # Initialize uniform probabilities
    return {
        'version': 1,
        'updated_at': None,
        'events': 0,
        'pos_probs': [[0.1 for _ in range(10)] for _ in range(4)],
    }


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


def update_state_with_event(state: Dict, actual: str, predictions: List[Tuple[str, str, str]]) -> Dict:
    # weights
    beta = 0.3  # update strength for new evidence
    w_actual = 1.0
    # predictions ranked by appearance: earlier is stronger
    pred_weights = [0.5 * (0.7 ** i) for i in range(len(predictions))]  # decaying

    # per-position target distributions
    targets = [[1e-3 for _ in range(10)] for _ in range(4)]  # smoothing

    # reinforce predictions (small)
    for rank, (_, _label, num) in enumerate(predictions):
        w = pred_weights[rank] if rank < len(pred_weights) else 0.1
        for i, ch in enumerate(num[:4]):
            d = ord(ch) - 48
            if 0 <= d <= 9:
                targets[i][d] += 0.2 * w  # small impact

    # reinforce actual (strong)
    for i, ch in enumerate(actual[:4]):
        d = ord(ch) - 48
        if 0 <= d <= 9:
            targets[i][d] += w_actual

    # blend with existing state
    for i in range(4):
        tgt = normalize(targets[i])
        old = state['pos_probs'][i]
        new = [ (1.0 - beta) * old[d] + beta * tgt[d] for d in range(10) ]
        state['pos_probs'][i] = normalize(new)

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

def learn(actual_number: str):
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
    conn = get_conn(DB_PATH)
    ensure_tables(conn)
    cur = conn.cursor()

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
            'INSERT INTO numbers4_predictions_log(created_at, source, label, number) VALUES (?,?,?,?)',
            (ts, s, l, n)
        )

    conn.commit()
    conn.close()

    print('[learn] Updated model_state.json and logged training event.')
    print(f"[learn] Actual: {actual_number} | Predictions: {len(preds)} | Max position hits: {max_hit} (top: {top_match})")


if __name__ == '__main__':
    # Example usage: hard-coded actual for quick run; edit or call from CLI.
    # You can also integrate argparse if needed.
    learn('6896')

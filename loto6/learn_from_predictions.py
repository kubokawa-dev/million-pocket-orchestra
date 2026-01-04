"""
Loto6 予測結果から学習するスクリプト（SQLite版）
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import List, Dict

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from tools.utils import get_db_connection

MODEL_PATH = os.path.join(ROOT_DIR, 'loto6', 'model_state.json')

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
        CREATE TABLE IF NOT EXISTS loto6_model_events (
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
        CREATE TABLE IF NOT EXISTS loto6_predictions_log (
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
# Model state
# -----------------------------

def load_model_state(path: str) -> Dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'version': 1,
        'updated_at': None,
        'events': 0,
        'number_frequencies': {}
    }


def save_model_state(path: str, state: Dict):
    state['updated_at'] = now_iso()
    ensure_dirs(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_state_with_event(state: Dict, actual: str, predictions: List[str]) -> Dict:
    """
    Update model state based on actual result and predictions.
    
    Args:
        state: Current model state
        actual: Actual numbers (e.g., '061317213536')
        predictions: List of predicted number combinations
    """
    # Update number frequencies
    actual_numbers = [actual[i:i+2] for i in range(0, len(actual), 2)]
    
    if 'number_frequencies' not in state:
        state['number_frequencies'] = {}
    
    for num in actual_numbers:
        num_int = int(num)
        state['number_frequencies'][num_int] = state['number_frequencies'].get(num_int, 0) + 1
    
    state['events'] = int(state.get('events', 0)) + 1
    return state


# -----------------------------
# Evaluation helpers
# -----------------------------

def count_matches(actual: str, pred: str) -> int:
    """Count how many numbers match between actual and predicted."""
    actual_numbers = set([actual[i:i+2] for i in range(0, len(actual), 2)])
    pred_numbers = set([pred[i:i+2] for i in range(0, len(pred), 2)])
    return len(actual_numbers & pred_numbers)


# -----------------------------
# Get predictions from database
# -----------------------------

def get_latest_predictions(conn, actual_number_normalized: str, actual_number_with_comma: str) -> tuple:
    """
    Get the most recent ensemble predictions from the database.
    Returns (prediction_id, list of predicted numbers).
    """
    cur = conn.cursor()
    
    # Try both formats: with comma and without comma
    cur.execute("""
        SELECT id, top_predictions, target_draw_number
        FROM loto6_ensemble_predictions 
        WHERE actual_numbers IN (?, ?)
        ORDER BY created_at DESC 
        LIMIT 1
    """, (actual_number_with_comma, actual_number_normalized))
    
    row = cur.fetchone()
    if not row:
        # If not found, try to get the latest prediction without actual_numbers set
        cur.execute("""
            SELECT id, top_predictions, target_draw_number
            FROM loto6_ensemble_predictions 
            WHERE actual_numbers IS NULL
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
    
    if not row:
        print("[learn] No predictions found in database.")
        return None, []
    
    pred_id, top_preds_json, target_draw = row
    top_preds = json.loads(top_preds_json) if top_preds_json else []
    
    # Extract numbers from predictions
    predictions = [pred['number'] for pred in top_preds if 'number' in pred]
    
    print(f"[learn] Loaded {len(predictions)} predictions from database (ID: {pred_id}, Draw: {target_draw})")
    return pred_id, predictions


# -----------------------------
# Main entry
# -----------------------------

def learn(actual_numbers: str, actual_bonus_number: int = None, actual_draw_number: int = None):
    """
    Learn from actual result and update model.
    
    Args:
        actual_numbers: Actual numbers (e.g., '061317213536' or '06,13,17,21,35,36')
        actual_bonus_number: Bonus number (optional)
        actual_draw_number: Draw number (optional, will fetch latest if not provided)
    """
    # Keep original format for database search
    actual_numbers_with_comma = actual_numbers
    
    # Normalize input (remove commas and spaces)
    actual_numbers_normalized = actual_numbers.replace(',', '').replace(' ', '').strip()
    
    if not re.fullmatch(r"\d{12}", actual_numbers_normalized):
        raise ValueError("actual_numbers must be 12 digits like '061317213536' or '06,13,17,21,35,36'")

    conn = get_db_connection()
    
    # Get predictions from database
    pred_id, predictions = get_latest_predictions(conn, actual_numbers_normalized, actual_numbers_with_comma)
    
    if not predictions:
        print("[learn] No predictions to learn from. Please run predict_ensemble.py first.")
        conn.close()
        return

    # Load/update model
    state = load_model_state(MODEL_PATH)
    state = update_state_with_event(state, actual_numbers_normalized, predictions)
    save_model_state(MODEL_PATH, state)

    # Evaluate predictions
    max_hit = -1
    top_match = None
    for num in predictions:
        h = count_matches(actual_numbers_normalized, num)
        if h > max_hit:
            max_hit = h
            top_match = num

    # Log into SQLite
    ensure_tables(conn)
    cur = conn.cursor()
    
    # Get actual draw number if not provided
    if actual_draw_number is None:
        cur.execute("SELECT MAX(draw_number) FROM loto6_draws")
        row = cur.fetchone()
        actual_draw_number = row[0] if row and row[0] else None

    preds_json = json.dumps(predictions, ensure_ascii=False)

    cur.execute(
        '''
        INSERT INTO loto6_model_events(
            event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            now_iso(),
            actual_numbers_normalized,
            preds_json,
            1 if actual_numbers_normalized in predictions else 0,
            top_match,
            int(max_hit if max_hit >= 0 else 0),
            'learn_from_predictions v1'
        )
    )

    # Also record predictions individually
    ts = now_iso()
    for n in predictions[:10]:  # Top 10 predictions
        cur.execute(
            'INSERT INTO loto6_predictions_log(created_at, source, label, number, target_draw_number) VALUES (?, ?, ?, ?, ?)',
            (ts, 'ensemble', 'prediction', n, actual_draw_number)
        )

    conn.commit()
    conn.close()

    print('[learn] ✅ Updated model_state.json and logged training event.')
    print(f"[learn] Actual: {actual_numbers_normalized} | Predictions: {len(predictions)} | Max matches: {max_hit} (top: {top_match})")
    if actual_bonus_number:
        print(f"[learn] Bonus number: {actual_bonus_number}")
    print(f"[learn] Model events: {state['events']} | Updated: {state['updated_at']}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        actual = sys.argv[1]
        bonus = int(sys.argv[2]) if len(sys.argv) > 2 else None
        draw_num = int(sys.argv[3]) if len(sys.argv) > 3 else None
        learn(actual, bonus, draw_num)
    else:
        print("Usage: python loto6/learn_from_predictions.py <actual_numbers> [bonus_number] [draw_number]")
        print("Example: python loto6/learn_from_predictions.py 061317213536 7")
        print("   or  : python loto6/learn_from_predictions.py 06,13,17,21,35,36 7")

import os
import sqlite3
from importlib import import_module

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, 'millions.sqlite')


def get_latest_numbers4(db_path: str):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1")
    row = cur.fetchone()
    con.close()
    return row  # (draw_number, draw_date, numbers) or None


def was_learned(db_path: str, actual_number: str) -> bool:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='numbers4_model_events'")
    if not cur.fetchone():
        con.close()
        return False
    cur.execute("SELECT 1 FROM numbers4_model_events WHERE actual_number = ? LIMIT 1", (actual_number,))
    ok = cur.fetchone() is not None
    con.close()
    return ok


def main():
    latest = get_latest_numbers4(DB)
    if latest is None:
        print('[update] numbers4_draws has no rows yet.')
        return
    draw_number, draw_date, actual = latest
    if was_learned(DB, actual):
        print(f"[update] Model already learned for latest draw {draw_number} ({draw_date}) = {actual}.")
        return

    # Dynamically import learn function
    lm = import_module('numbers4.learn_from_predictions')
    print(f"[update] Learning with latest draw {draw_number} ({draw_date}) = {actual} ...")
    lm.learn(actual)


if __name__ == '__main__':
    main()

import os
import psycopg2
import sys
from importlib import import_module
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(__file__))

def get_latest_numbers4(db_url: str):
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    con = psycopg2.connect(db_url)
    cur = con.cursor()
    cur.execute("SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1")
    row = cur.fetchone()
    con.close()
    return row  # (draw_number, draw_date, numbers) or None


def was_learned(db_url: str, actual_number: str) -> bool:
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    con = psycopg2.connect(db_url)
    cur = con.cursor()
    cur.execute("SELECT to_regclass('numbers4_model_events')")
    if not cur.fetchone()[0]:
        con.close()
        return False
    cur.execute("SELECT 1 FROM numbers4_model_events WHERE actual_number = %s LIMIT 1", (actual_number,))
    ok = cur.fetchone() is not None
    con.close()
    return ok


def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[update] DATABASE_URL not found in .env file")
        return

    # Ensure project root is on sys.path so 'numbers4' package is importable
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    latest = get_latest_numbers4(db_url)
    if latest is None:
        print('[update] numbers4_draws has no rows yet.')
        return
    draw_number, draw_date, actual = latest
    if was_learned(db_url, actual):
        print(f"[update] Model already learned for latest draw {draw_number} ({draw_date}) = {actual}.")
        return

    # Dynamically import learn function
    lm = import_module('numbers4.learn_from_predictions')
    print(f"[update] Learning with latest draw {draw_number} ({draw_date}) = {actual} ...")
    lm.learn(actual)


if __name__ == '__main__':
    main()

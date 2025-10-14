import sqlite3
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, 'millions.sqlite')


def main():
    if not os.path.exists(DB):
        print(f"DB not found: {DB}")
        return

    con = sqlite3.connect(DB)
    cur = con.cursor()

    # Check table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='numbers4_draws'")
    if not cur.fetchone():
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print('[Error] Table numbers4_draws not found. Existing tables:', [r[0] for r in cur.fetchall()])
        con.close()
        return

    # Query latest 10 by date then draw_number desc
    q = """
        SELECT draw_number, draw_date, numbers
        FROM numbers4_draws
        ORDER BY draw_date DESC, draw_number DESC
        LIMIT 10
    """
    cur.execute(q)
    rows = cur.fetchall()
    con.close()

    print('numbers4_draws: latest 10 rows')
    print('draw_number | draw_date   | numbers')
    print('----------- | ----------- | -------')
    for r in rows:
        print(f"{r[0]:>10} | {r[1]:<11} | {r[2]}")


if __name__ == '__main__':
    main()

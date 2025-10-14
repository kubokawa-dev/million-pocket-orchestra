import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, 'millions.sqlite')


def check_tables():
    if not os.path.exists(DB):
        print('[fail] DB not found:', DB)
        return False
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names = {r[0] for r in cur.fetchall()}
    need = {'numbers4_draws'}
    miss = need - names
    if miss:
        print('[fail] Missing tables:', miss)
        con.close()
        return False
    cur.execute('SELECT COUNT(*) FROM numbers4_draws')
    cnt = cur.fetchone()[0]
    con.close()
    if cnt <= 0:
        print('[fail] numbers4_draws is empty')
        return False
    print('[ok] tables exist, numbers4_draws rows =', cnt)
    return True


if __name__ == '__main__':
    ok = check_tables()
    raise SystemExit(0 if ok else 1)

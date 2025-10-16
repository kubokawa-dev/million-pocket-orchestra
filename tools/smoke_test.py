import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_tables():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[fail] DATABASE_URL not found in .env file")
        return False
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    con = psycopg2.connect(db_url)
    cur = con.cursor()
    cur.execute("SELECT to_regclass('numbers4_draws')")
    if not cur.fetchone()[0]:
        print('[fail] Missing table: numbers4_draws')
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

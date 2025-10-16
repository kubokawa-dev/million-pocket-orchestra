import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in .env file")
        return

    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    con = psycopg2.connect(db_url)
    cur = con.cursor()

    # Check table
    cur.execute("SELECT to_regclass('numbers4_draws')")
    if not cur.fetchone()[0]:
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
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

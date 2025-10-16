import os
import sys
import psycopg2
import psycopg2.extras
import argparse
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(__file__))

def connect(db_url: str):
    if not db_url:
        print("[dump] DATABASE_URL not found in .env file")
        sys.exit(1)
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    conn = psycopg2.connect(db_url)
    return conn


def list_tables(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    return [r[0] for r in cur.fetchall()]


def get_schema(conn):
    # This is a simplified version for PostgreSQL as it doesn't have a direct equivalent of sqlite_master's sql column
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, 'schema not easily available in this script' FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    return cur.fetchall()


def print_schema(conn):
    print('== Schema ==')
    for name, sql in get_schema(conn):
        print(f"-- {name}")
        print(sql or '(no sql)')
        print()


def table_info(conn, table):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table}'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    return cols


def table_count(conn, table):
    cur = conn.cursor()
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    return cur.fetchone()[0]


def print_table_head(conn, table, limit=10):
    cols = table_info(conn, table)
    order = ''
    # Nice ordering if draw_number present, else by rowid
    if 'draw_number' in cols:
        order = 'ORDER BY draw_number DESC'
    elif 'date' in cols:
        order = 'ORDER BY date DESC'
    else:
        order = 'ORDER BY rowid DESC'
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table} {order} LIMIT {int(limit)}')
    rows = cur.fetchall()
    print(f"-- {table} (head {limit})")
    print(','.join(cols))
    for r in rows:
        vals = [str(r[c]) if r[c] is not None else '' for c in cols]
        print(','.join(vals))
    print()


def export_sql(conn, out_path: str):
    # Ensure parent directory exists
    parent = os.path.dirname(out_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print(f"[dump] SQL export -> {out_path}")


def export_csvs(conn, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    for t in list_tables(conn):
        cols = table_info(conn, t)
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {t}')
        rows = cur.fetchall()
        path = os.path.join(out_dir, f'{t}.csv')
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for r in rows:
                w.writerow([r[c] for c in cols])
        print(f"[dump] CSV export -> {path} ({len(rows)} rows)")


def print_summary(conn):
    print('== Tables ==')
    for t in list_tables(conn):
        cnt = table_count(conn, t)
        print(f"- {t}: {cnt} rows")
    print()

    # Quick latest for known tables
    cur = conn.cursor()
    try:
        cur.execute('SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT 1')
        r = cur.fetchone()
        if r:
            print(f"Latest NUMBERS4: 第{r['draw_number']}回 {r['draw_date']} = {r['numbers']}")
    except Exception:
        pass

    try:
        cur.execute('SELECT draw_number, draw_date, numbers, bonus_number FROM loto6_draws ORDER BY draw_number DESC LIMIT 1')
        r = cur.fetchone()
        if r:
            print(f"Latest LOTO6: 第{r['draw_number']}回 {r['draw_date']} = {r['numbers']} (bonus={r['bonus_number']})")
    except Exception:
        pass
    print()


def main():
    ap = argparse.ArgumentParser(description='Dump and inspect PostgreSQL database')
    ap.add_argument('--db', default=os.environ.get('DATABASE_URL'), help='Database connection string')
    ap.add_argument('--head', type=int, default=10, help='Head rows per table to print')
    ap.add_argument('--schema-only', action='store_true', help='Print only schema')
    ap.add_argument('--no-data', action='store_true', help='Skip printing table head rows')
    ap.add_argument('--sql', help='Export full SQL dump to the given file path')
    ap.add_argument('--csv-dir', help='Export each table to CSVs in the given directory')
    args = ap.parse_args()

    conn = connect(args.db)
    try:
        print_summary(conn)
        print_schema(conn)
        if not args.schema_only and not args.no_data:
            for t in list_tables(conn):
                print_table_head(conn, t, limit=args.head)
        if args.sql:
            export_sql(conn, args.sql)
        if args.csv_dir:
            export_csvs(conn, args.csv_dir)
    finally:
        conn.close()


if __name__ == '__main__':
    main()

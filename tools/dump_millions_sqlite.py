import os
import sys
import sqlite3
import argparse
import csv
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'millions.sqlite')


def connect(db_path: str):
    if not os.path.exists(db_path):
        print(f"[dump] DB not found: {db_path}")
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def get_schema(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return cur.fetchall()


def print_schema(conn):
    print('== Schema ==')
    for name, sql in get_schema(conn):
        print(f"-- {name}")
        print(sql or '(no sql)')
        print()


def table_info(conn, table):
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info({table})')
    cols = [r[1] for r in cur.fetchall()]
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
    ap = argparse.ArgumentParser(description='Dump and inspect millions.sqlite')
    ap.add_argument('--db', default=DB_PATH, help='Path to SQLite DB (default: millions.sqlite)')
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

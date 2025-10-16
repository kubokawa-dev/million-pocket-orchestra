import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    sqlite_db_path = os.path.join(os.path.dirname(__file__), '..', 'prisma', 'millions.sqlite')
    postgres_url = os.environ.get('DATABASE_URL')
    if postgres_url and '?schema' in postgres_url:
        postgres_url = postgres_url.split('?schema')[0]

    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database not found at {sqlite_db_path}")
        return

    if not postgres_url:
        print("DATABASE_URL not found in .env file")
        return

    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    postgres_conn = psycopg2.connect(postgres_url)
    postgres_cursor = postgres_conn.cursor()

    tables = ['numbers4_draws', 'loto6_draws', 'numbers4_model_events', 'numbers4_predictions_log']

    for table in tables:
        print(f"Migrating table: {table}")
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print(f"No data to migrate for table: {table}")
            continue

        column_names = [description[0] for description in sqlite_cursor.description]
        columns = ', '.join(column_names)
        placeholders = ', '.join(['%s'] * len(column_names))

        insert_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            postgres_cursor.executemany(insert_query, rows)
            postgres_conn.commit()
            print(f"Successfully migrated {len(rows)} rows to {table}")
        except Exception as e:
            print(f"Error migrating data for table {table}: {e}")
            postgres_conn.rollback()

    sqlite_conn.close()
    postgres_conn.close()

if __name__ == '__main__':
    migrate_data()

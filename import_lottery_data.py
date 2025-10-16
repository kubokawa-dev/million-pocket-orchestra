import psycopg2
import glob
import os
import re
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """ create a database connection to a PostgreSQL database """
    conn = None
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        conn = psycopg2.connect(db_url)
        print(f"Successfully connected to PostgreSQL database")
    except Exception as e:
        print(e)
    return conn

def create_tables(conn):
    """ create tables in the PostgreSQL database """
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS loto6_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL,
            bonus_number INTEGER NOT NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS numbers4_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        );
        """)
        print("Tables 'loto6_draws' and 'numbers4_draws' created or already exist.")
    except Exception as e:
        print(e)

def import_loto6_data(conn):
    """ Import loto6 data from csv files """
    cursor = conn.cursor()
    folder_path = 'loto6'
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    for file in csv_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',')
                try:
                    draw_number = int(re.sub(r'[^0-9]', '', parts[0]))
                    draw_date = parts[1]
                    numbers = ",".join(parts[2:8])
                    bonus_number = int(re.sub(r'[^0-9]', '', parts[8]))

                    cursor.execute("SELECT 1 FROM loto6_draws WHERE draw_number = ?", (draw_number,))
                    if cursor.fetchone() is None:
                        cursor.execute("""
                        INSERT INTO loto6_draws (draw_number, draw_date, numbers, bonus_number)
                        VALUES (?, ?, ?, ?)
                        """, (draw_number, draw_date, numbers, bonus_number))
                except (ValueError, IndexError) as e:
                    print(f"Skipping malformed line in {file}: {line} - Error: {e}")

    conn.commit()
    print("Loto6 data import completed.")

def import_numbers4_data(conn):
    """ Import numbers4 data from csv files """
    cursor = conn.cursor()
    folder_path = 'numbers4'
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    for file in csv_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(',')
                try:
                    draw_number = int(re.sub(r'[^0-9]', '', parts[0]))
                    draw_date = parts[1]
                    numbers = parts[2]

                    cursor.execute("SELECT 1 FROM numbers4_draws WHERE draw_number = ?", (draw_number,))
                    if cursor.fetchone() is None:
                        cursor.execute("""
                        INSERT INTO numbers4_draws (draw_number, draw_date, numbers)
                        VALUES (?, ?, ?)
                        """, (draw_number, draw_date, numbers))
                except (ValueError, IndexError) as e:
                    print(f"Skipping malformed line in {file}: {line} - Error: {e}")

    conn.commit()
    print("Numbers4 data import completed.")


def main():
    # create a database connection
    conn = create_connection()

    if conn is not None:
        # create tables
        create_tables(conn)

        # import data
        import_loto6_data(conn)
        import_numbers4_data(conn)

        # close the connection
        conn.close()
        print("Database connection closed.")
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

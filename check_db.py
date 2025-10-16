
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def check_loto6_data():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in .env file")
        return

    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    conn = psycopg2.connect(db_url)
    try:
        print("loto6_draws テーブルの内容:")
        df = pd.read_sql_query("SELECT * FROM loto6_draws", conn)
        if df.empty:
            print("テーブルは空です。")
        else:
            print(df.to_string())
        
        print("\nnumbers4_draws テーブルの内容:")
        df_n4 = pd.read_sql_query("SELECT * FROM numbers4_draws", conn)
        if df_n4.empty:
            print("テーブルは空です。")
        else:
            print(df_n4.to_string())

    except Exception as e:
        print(f"エラー: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_loto6_data()

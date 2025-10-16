import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()
cursor.execute("""SELECT column_name, data_type FROM information_schema.columns
       WHERE table_schema = 'public' AND table_name = 'loto6_draws'""")
print("Columns in loto6_draws:")
for col in cursor.fetchall():
    print(f"- {col[0]} ({col[1]})")
conn.close()

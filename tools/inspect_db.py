import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()
cursor.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
print("Tables in database:")
for table in cursor.fetchall():
    print(f"- {table[0]}")
conn.close()

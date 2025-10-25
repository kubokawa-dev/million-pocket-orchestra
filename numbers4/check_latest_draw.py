import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute('SELECT draw_number, numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 5')
results = cur.fetchall()

print('\n最新5回の抽選番号:')
for draw_num, numbers in results:
    print(f'  第{draw_num}回: {numbers}')

conn.close()

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# 最新3件を確認
cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number DESC LIMIT 5")
results = cursor.fetchall()
print('最新5件の抽選結果:')
for r in results:
    print(f'  第{r[0]}回: {r[2]} ({r[1]})')

conn.close()

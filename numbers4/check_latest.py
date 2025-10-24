import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# 最新10件を確認
cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT 10")
results = cursor.fetchall()
print('ナンバーズ4 最新10件の抽選結果:')
for r in results:
    print(f'  第{r[0]}回: {r[2]} ({r[1]})')

print(f'\n合計データ数:')
cursor.execute("SELECT COUNT(*) FROM numbers4_draws")
count = cursor.fetchone()[0]
print(f'  {count}件')

conn.close()

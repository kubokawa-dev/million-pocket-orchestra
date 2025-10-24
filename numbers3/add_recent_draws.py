import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# 第6841回と第6842回を追加
new_draws = [
    (6841, '209', '2025-10-23'),
    (6842, '472', '2025-10-24'),
]

for draw_number, numbers, draw_date in new_draws:
    # 既に存在するか確認
    cursor.execute("SELECT draw_number FROM numbers3_draws WHERE draw_number = %s", (draw_number,))
    if cursor.fetchone():
        print(f'第{draw_number}回は既に登録されています')
    else:
        cursor.execute(
            "INSERT INTO numbers3_draws (draw_number, numbers, draw_date) VALUES (%s, %s, %s)",
            (draw_number, numbers, draw_date)
        )
        print(f'第{draw_number}回: {numbers} ({draw_date}) を追加しました')

conn.commit()

# 確認
cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number DESC LIMIT 5")
results = cursor.fetchall()
print('\n最新5件の抽選結果:')
for r in results:
    print(f'  第{r[0]}回: {r[2]} ({r[1]})')

conn.close()

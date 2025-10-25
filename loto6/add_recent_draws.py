import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# ⚠️ ここに実際の当選番号を入力してください
# ロト6は1-43から6個を選びます（カンマ区切り、昇順）
new_draws = [
    # (回号, 当選番号, 抽選日)
    # 例: (2045, '1,5,10,20,30,40', '2025-10-23'),
    # ユーザーに教えてもらった番号をここに追加
]

if not new_draws:
    print('⚠️ new_draws が空です。実際の当選番号を追加してください。')
    print('例:')
    print("new_draws = [")
    print("    (2045, '1,5,10,20,30,40', '2025-10-23'),")
    print("    (2046, '3,7,15,25,35,43', '2025-10-27'),")
    print("]")
else:
    for draw_number, numbers, draw_date in new_draws:
        # 既に存在するか確認
        cursor.execute("SELECT draw_number FROM loto6_draws WHERE draw_number = %s", (draw_number,))
        if cursor.fetchone():
            print(f'第{draw_number}回は既に登録されています')
        else:
            cursor.execute(
                "INSERT INTO loto6_draws (draw_number, numbers, draw_date) VALUES (%s, %s, %s)",
                (draw_number, numbers, draw_date)
            )
            print(f'第{draw_number}回: {numbers} ({draw_date}) を追加しました')

    conn.commit()

    # 確認
    cursor.execute("SELECT draw_number, draw_date, numbers FROM loto6_draws ORDER BY draw_number DESC LIMIT 5")
    results = cursor.fetchall()
    print('\n最新5件の抽選結果:')
    for r in results:
        print(f'  第{r[0]}回: {r[2]} ({r[1]})')

conn.close()

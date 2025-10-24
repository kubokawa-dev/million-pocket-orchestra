import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# ⚠️ ここに実際の当選番号を入力してください
new_draws = [
    # (回号, 当選番号, 抽選日)
    # 例: (6839, '1234', '2025-10-21'),
    # ユーザーに教えてもらった番号をここに追加
]

if not new_draws:
    print('⚠️ new_draws が空です。実際の当選番号を追加してください。')
    print('例:')
    print("new_draws = [")
    print("    (6839, '1234', '2025-10-21'),")
    print("    (6840, '5678', '2025-10-22'),")
    print("    (6841, '9012', '2025-10-23'),")
    print("    (6842, '3456', '2025-10-24'),")
    print("]")
else:
    for draw_number, numbers, draw_date in new_draws:
        # 既に存在するか確認
        cursor.execute("SELECT draw_number FROM numbers4_draws WHERE draw_number = %s", (draw_number,))
        if cursor.fetchone():
            print(f'第{draw_number}回は既に登録されています')
        else:
            cursor.execute(
                "INSERT INTO numbers4_draws (draw_number, numbers, draw_date) VALUES (%s, %s, %s)",
                (draw_number, numbers, draw_date)
            )
            print(f'第{draw_number}回: {numbers} ({draw_date}) を追加しました')

    conn.commit()

    # 確認
    cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT 5")
    results = cursor.fetchall()
    print('\n最新5件の抽選結果:')
    for r in results:
        print(f'  第{r[0]}回: {r[2]} ({r[1]})')

conn.close()

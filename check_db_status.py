"""
データベースの状態を確認
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("="*80)
print("📊 データベース状態確認")
print("="*80)

# 最新10回の抽選データを確認
print("\n【最新10回の抽選データ】")
cur.execute("""
    SELECT draw_number, draw_date, numbers 
    FROM numbers3_draws 
    ORDER BY draw_number DESC 
    LIMIT 10
""")
results = cur.fetchall()

for draw_num, draw_date, numbers in results:
    d1, d2, d3 = int(numbers[0]), int(numbers[1]), int(numbers[2])
    total = d1 + d2 + d3
    print(f"  第{draw_num}回: {numbers} (合計:{total:2d}) - {draw_date}")

# 第6843回と第6844回が存在するか確認
print("\n【重要な回の確認】")
for target_draw in [6843, 6844]:
    cur.execute("""
        SELECT draw_number, draw_date, numbers 
        FROM numbers3_draws 
        WHERE draw_number = %s
    """, (target_draw,))
    result = cur.fetchone()
    
    if result:
        draw_num, draw_date, numbers = result
        print(f"  ✅ 第{draw_num}回: {numbers} ({draw_date}) - 登録済み")
    else:
        print(f"  ❌ 第{target_draw}回: 未登録")

# 最新の予測履歴を確認
print("\n【最新の予測履歴】")
cur.execute("""
    SELECT id, created_at, target_draw_number, notes
    FROM numbers3_ensemble_predictions 
    ORDER BY created_at DESC 
    LIMIT 3
""")
predictions = cur.fetchall()

for pred_id, created_at, target_draw, notes in predictions:
    print(f"\n  予測ID: {pred_id}")
    print(f"  作成日時: {created_at}")
    print(f"  対象回号: 第{target_draw}回")
    if notes:
        # notesの最初の100文字のみ表示
        notes_short = notes[:100] + "..." if len(notes) > 100 else notes
        print(f"  備考: {notes_short}")

# 総データ数を確認
print("\n【データベース統計】")
cur.execute("SELECT COUNT(*) FROM numbers3_draws")
total_draws = cur.fetchone()[0]
print(f"  総抽選データ数: {total_draws}件")

cur.execute("SELECT COUNT(*) FROM numbers3_ensemble_predictions")
total_predictions = cur.fetchone()[0]
print(f"  総予測履歴数: {total_predictions}件")

cur.close()
conn.close()

print("\n" + "="*80)

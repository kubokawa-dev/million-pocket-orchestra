import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print('='*80)
print('📊 データベース状態確認')
print('='*80)

# 最新10回の抽選データを確認
print('\n【最新10回の抽選データ】')
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number DESC LIMIT 10')
results = cur.fetchall()

for draw_num, draw_date, numbers in results:
    d1, d2, d3 = int(numbers[0]), int(numbers[1]), int(numbers[2])
    total = d1 + d2 + d3
    print(f'  第{draw_num}回: {numbers} (合計:{total:2d}) - {draw_date}')

# 第6843回と第6844回が存在するか確認
print('\n【重要な回の確認】')
for target_draw in [6843, 6844]:
    cur.execute('SELECT draw_number, draw_date, numbers FROM numbers3_draws WHERE draw_number = %s', (target_draw,))
    result = cur.fetchone()
    
    if result:
        draw_num, draw_date, numbers = result
        print(f'  ✅ 第{draw_num}回: {numbers} ({draw_date}) - 登録済み')
    else:
        print(f'  ❌ 第{target_draw}回: 未登録')

# 最新の抽選情報を取得
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1')
row = cur.fetchone()

if row:
    print('\n' + '='*80)
    print('🎯 予測対象回号')
    print('='*80)
    print(f'\n最新抽選: 第{row[0]}回 ({row[1]}) - 当選番号: {row[2]}')
    print(f'予測対象: 第{row[0]+1}回')
else:
    print('データが見つかりません')

# 最新3件の予測履歴を確認
print('\n' + '='*80)
print('📝 最新の予測履歴（3件）')
print('='*80)
cur.execute('SELECT id, target_draw_number, created_at, notes FROM numbers3_ensemble_predictions ORDER BY created_at DESC LIMIT 3')
predictions = cur.fetchall()

for pred_id, target_draw, created_at, notes in predictions:
    print(f'\n予測ID: {pred_id}')
    print(f'  対象回号: 第{target_draw}回')
    print(f'  作成日時: {created_at}')
    if notes:
        # notesの最初の150文字のみ表示
        if 'v10.0' in notes:
            print(f'  バージョン: v10.0 (根本的改善版)')
        elif 'v9.0' in notes:
            print(f'  バージョン: v9.0')
        else:
            notes_short = notes[:100] + '...' if len(notes) > 100 else notes
            print(f'  備考: {notes_short}')

# 総データ数を確認
print('\n' + '='*80)
print('📈 データベース統計')
print('='*80)
cur.execute('SELECT COUNT(*) FROM numbers3_draws')
total_draws = cur.fetchone()[0]
print(f'総抽選データ数: {total_draws}件')

cur.execute('SELECT COUNT(*) FROM numbers3_ensemble_predictions')
total_predictions = cur.fetchone()[0]
print(f'総予測履歴数: {total_predictions}件')

print('='*80)

cur.close()
conn.close()

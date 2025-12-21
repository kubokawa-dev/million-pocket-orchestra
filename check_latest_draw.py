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
print('📊 最新の抽選結果と予測履歴')
print('='*80)

# ================== Numbers3 ==================
print('\n' + '🎯 ナンバーズ3'.center(78))
print('='*80)

# 最新10回の抽選データを確認
print('\n【最新10回の抽選データ】')
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number DESC LIMIT 10')
results = cur.fetchall()

for draw_num, draw_date, numbers in results:
    d1, d2, d3 = int(numbers[0]), int(numbers[1]), int(numbers[2])
    total = d1 + d2 + d3
    print(f'  第{draw_num}回: {numbers} (合計:{total:2d}) - {draw_date}')

# 最新の抽選情報を取得
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1')
row = cur.fetchone()

if row:
    print('\n【🎯 予測対象回号】')
    print(f'  最新抽選: 第{row[0]}回 ({row[1]}) - 当選番号: {row[2]}')
    print(f'  予測対象: 第{row[0]+1}回')
else:
    print('データが見つかりません')

# 最新3件の予測履歴を確認
print('\n【📝 最新の予測履歴（3件）】')
cur.execute('SELECT id, target_draw_number, created_at, notes FROM numbers3_ensemble_predictions ORDER BY created_at DESC LIMIT 3')
predictions = cur.fetchall()

if predictions:
for pred_id, target_draw, created_at, notes in predictions:
        print(f'\n  予測ID: {pred_id}')
    print(f'  対象回号: 第{target_draw}回')
    print(f'  作成日時: {created_at}')
    if notes:
        if 'v10.0' in notes:
            print(f'  バージョン: v10.0 (根本的改善版)')
        elif 'v9.0' in notes:
            print(f'  バージョン: v9.0')
        else:
            notes_short = notes[:100] + '...' if len(notes) > 100 else notes
            print(f'  備考: {notes_short}')
else:
    print('  (予測履歴なし)')

# 総データ数を確認
print('\n【📈 統計】')
cur.execute('SELECT COUNT(*) FROM numbers3_draws')
total_draws = cur.fetchone()[0]
print(f'  抽選データ: {total_draws}件')

cur.execute('SELECT COUNT(*) FROM numbers3_ensemble_predictions')
total_predictions = cur.fetchone()[0]
print(f'  予測履歴: {total_predictions}件')

# ================== Numbers4 ==================
print('\n' + '='*80)
print('🎯 ナンバーズ4'.center(78))
print('='*80)

# 最新10回の抽選データを確認
print('\n【最新10回の抽選データ】')
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT 10')
results = cur.fetchall()

for draw_num, draw_date, numbers in results:
    d1, d2, d3, d4 = int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3])
    total = d1 + d2 + d3 + d4
    print(f'  第{draw_num}回: {numbers} (合計:{total:2d}) - {draw_date}')

# 最新の抽選情報を取得
cur.execute('SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1')
row = cur.fetchone()

if row:
    print('\n【🎯 予測対象回号】')
    print(f'  最新抽選: 第{row[0]}回 ({row[1]}) - 当選番号: {row[2]}')
    print(f'  予測対象: 第{row[0]+1}回')
else:
    print('データが見つかりません')

# 最新3件の予測履歴を確認
print('\n【📝 最新の予測履歴（3件）】')
cur.execute('SELECT id, target_draw_number, created_at, notes FROM numbers4_ensemble_predictions ORDER BY created_at DESC LIMIT 3')
predictions = cur.fetchall()

if predictions:
    for pred_id, target_draw, created_at, notes in predictions:
        print(f'\n  予測ID: {pred_id}')
        print(f'  対象回号: 第{target_draw}回')
        print(f'  作成日時: {created_at}')
        if notes:
            if 'v10.0' in notes:
                print(f'  バージョン: v10.0 (根本的改善版)')
            elif 'v9.0' in notes:
                print(f'  バージョン: v9.0')
            else:
                notes_short = notes[:100] + '...' if len(notes) > 100 else notes
                print(f'  備考: {notes_short}')
else:
    print('  (予測履歴なし)')

# 総データ数を確認
print('\n【📈 統計】')
cur.execute('SELECT COUNT(*) FROM numbers4_draws')
total_draws = cur.fetchone()[0]
print(f'  抽選データ: {total_draws}件')

cur.execute('SELECT COUNT(*) FROM numbers4_ensemble_predictions')
total_predictions = cur.fetchone()[0]
print(f'  予測履歴: {total_predictions}件')

print('\n' + '='*80)

cur.close()
conn.close()

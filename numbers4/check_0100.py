import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Get the latest prediction ID
cur.execute("SELECT MAX(id) FROM numbers4_ensemble_predictions")
latest_id = cur.fetchone()[0]

# Check for 0100 in the latest prediction
cur.execute("""
    SELECT number, rank, score, contributing_models
    FROM numbers4_prediction_candidates
    WHERE ensemble_prediction_id = %s AND number = '0100'
""", (latest_id,))

result = cur.fetchone()

print('\n' + '='*80)
print(f'🔍 0100の予測状況チェック (予測ID: {latest_id})')
print('='*80)

if result:
    number, rank, score, models = result
    print(f'\n✅ ✅ ✅ 0100が予測候補に含まれています！ ✅ ✅ ✅')
    print(f'\n  順位: {rank}位')
    print(f'  スコア: {score:.2f}')
    print(f'  貢献モデル: {models}')
else:
    print(f'\n❌ 0100はまだ予測候補に含まれていません')

# Show all patterns with sum <= 3
print('\n' + '='*80)
print(f'合計値1-3のパターン（予測ID: {latest_id}）')
print('='*80 + '\n')

cur.execute("""
    SELECT number, rank, score, contributing_models
    FROM numbers4_prediction_candidates
    WHERE ensemble_prediction_id = %s
    ORDER BY rank
""", (latest_id,))

low_sum_patterns = []
for row in cur.fetchall():
    number, rank, score, models = row
    digit_sum = sum(int(d) for d in number)
    if digit_sum <= 3:
        low_sum_patterns.append((number, rank, score, digit_sum, models))

if low_sum_patterns:
    for number, rank, score, digit_sum, models in low_sum_patterns:
        print(f'{rank:3d}位: {number} (スコア: {score:.2f}, 合計: {digit_sum}) - {models}')
else:
    print('なし')

# Show patterns starting with 0
print('\n' + '='*80)
print(f'0で始まるパターン（予測ID: {latest_id}）')
print('='*80 + '\n')

cur.execute("""
    SELECT number, rank, score, contributing_models
    FROM numbers4_prediction_candidates
    WHERE ensemble_prediction_id = %s AND number LIKE '0%'
    ORDER BY rank
""", (latest_id,))

zero_patterns = cur.fetchall()
if zero_patterns:
    for number, rank, score, models in zero_patterns:
        digit_sum = sum(int(d) for d in number)
        print(f'{rank:3d}位: {number} (スコア: {score:.2f}, 合計: {digit_sum}) - {models}')
else:
    print('なし')

conn.close()

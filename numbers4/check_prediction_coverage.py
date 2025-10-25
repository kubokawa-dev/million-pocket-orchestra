import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Get the latest prediction (ID 5)
prediction_id = 5

# Check if 0100 or similar patterns are in the predictions
cur.execute("""
    SELECT number, rank, score, contributing_models
    FROM numbers4_prediction_candidates
    WHERE ensemble_prediction_id = %s
    ORDER BY rank
""", (prediction_id,))

all_candidates = cur.fetchall()

print(f"\n{'='*80}")
print(f"予測ID {prediction_id} の全候補 ({len(all_candidates)}件)")
print(f"{'='*80}\n")

# Check for low sum patterns
low_sum_patterns = []
for number, rank, score, models in all_candidates:
    digit_sum = sum(int(d) for d in number)
    if digit_sum <= 5:
        low_sum_patterns.append((number, rank, score, digit_sum))

print("【合計値5以下のパターン】")
if low_sum_patterns:
    for number, rank, score, digit_sum in low_sum_patterns:
        print(f"  {rank:2d}位: {number} (スコア: {score:.2f}, 合計: {digit_sum})")
else:
    print("  なし")

# Check for patterns starting with 0
zero_start_patterns = []
for number, rank, score, models in all_candidates:
    if number.startswith('0'):
        zero_start_patterns.append((number, rank, score))

print(f"\n【0で始まるパターン】")
if zero_start_patterns:
    for number, rank, score in zero_start_patterns:
        print(f"  {rank:2d}位: {number} (スコア: {score:.2f})")
else:
    print("  なし")

# Check specifically for 0100
cur.execute("""
    SELECT number, rank, score, contributing_models
    FROM numbers4_prediction_candidates
    WHERE ensemble_prediction_id = %s AND number = '0100'
""", (prediction_id,))

result = cur.fetchone()
print(f"\n【0100の予測状況】")
if result:
    number, rank, score, models = result
    print(f"  ✅ 含まれています！")
    print(f"  順位: {rank}位")
    print(f"  スコア: {score:.2f}")
    print(f"  貢献モデル: {models}")
else:
    print(f"  ❌ まだ含まれていません")

# Show distribution by sum
print(f"\n【合計値の分布】")
sum_distribution = {}
for number, rank, score, models in all_candidates:
    digit_sum = sum(int(d) for d in number)
    if digit_sum not in sum_distribution:
        sum_distribution[digit_sum] = []
    sum_distribution[digit_sum].append((number, rank, score))

for s in sorted(sum_distribution.keys()):
    count = len(sum_distribution[s])
    examples = ', '.join([n for n, _, _ in sum_distribution[s][:3]])
    print(f"  合計{s:2d}: {count}件 (例: {examples})")

# Show models contribution
print(f"\n【モデル別貢献度】")
cur.execute("""
    SELECT 
        ensemble_prediction_id,
        jsonb_object_keys(model_predictions) as model,
        model_predictions
    FROM numbers4_ensemble_predictions
    WHERE id = %s
""", (prediction_id,))

conn.close()

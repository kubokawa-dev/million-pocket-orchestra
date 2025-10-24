"""合計値13の未出現パターンを頻出数字スコア順に並べる"""
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

def get_db_connection():
    """データベース接続を取得する"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

# データベースからすべての抽選データを読み込む
conn = get_db_connection()
df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date ASC", conn)
conn.close()

# numbersを各桁に分割
df['d1'] = df['numbers'].str[0]
df['d2'] = df['numbers'].str[1]
df['d3'] = df['numbers'].str[2]

for col in ['d1', 'd2', 'd3']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()
for col in ['d1', 'd2', 'd3']:
    df[col] = df[col].astype(int)

# 最近100回の数字出現頻度
recent_df = df.tail(100)
all_recent_digits = pd.concat([recent_df[f'd{i+1}'] for i in range(3)])
digit_freq = Counter(all_recent_digits)

# 未出現パターン
historical_numbers = set(df['numbers'].values)

# 合計値13の未出現パターンをスコア付き
sum_13_patterns = []
for num in range(1000):
    num_str = f"{num:03d}"
    if num_str not in historical_numbers:
        if sum(int(d) for d in num_str) == 13:
            digit_score = sum(digit_freq.get(int(d), 0) for d in num_str)
            sum_13_patterns.append((num_str, digit_score))

# スコア順にソート
sum_13_patterns.sort(key=lambda x: -x[1])

print("\n" + "="*60)
print("【合計値13の未出現パターン（頻出数字スコア順）】")
print("="*60)

permutations_139 = ['139', '193', '319', '391', '913', '931']

for i, (pattern, score) in enumerate(sum_13_patterns, 1):
    marker = " ⭐" if pattern in permutations_139 else ""
    print(f"{i:2d}. {pattern} (スコア: {score:.0f}){marker}")

print("\n" + "="*60)
print("【{1,3,9}の順列の順位】")
print("="*60)
for perm in permutations_139:
    for i, (pattern, score) in enumerate(sum_13_patterns, 1):
        if pattern == perm:
            print(f"{perm}: {i}位 (スコア: {score:.0f})")
            break

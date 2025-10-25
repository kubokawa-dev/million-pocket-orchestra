"""未出現パターンの合計値分布を分析"""
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

# データベースから全データを取得
conn = get_db_connection()
df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date ASC", conn)
conn.close()

historical_numbers = set(df['numbers'].values)

# 未出現パターンを合計値でグループ化
never_appeared_by_sum = {}
for num in range(1000):
    num_str = f"{num:03d}"
    if num_str not in historical_numbers:
        num_sum = sum(int(d) for d in num_str)
        if num_sum not in never_appeared_by_sum:
            never_appeared_by_sum[num_sum] = []
        never_appeared_by_sum[num_sum].append(num_str)

print("\n" + "="*60)
print("【未出現パターンの合計値別分布】")
print("="*60)

cumulative = 0
for s in range(28):
    if s in never_appeared_by_sum:
        count = len(never_appeared_by_sum[s])
        cumulative += count
        marker = " ⭐" if s == 13 else ""
        print(f"合計値{s:2d}: {count:3d}個 (累計: {cumulative:3d}){marker}")

print(f"\n合計未出現パターン数: {cumulative}")

# 合計値13の詳細
if 13 in never_appeared_by_sum:
    print("\n" + "="*60)
    print("【合計値13の未出現パターン（全て）】")
    print("="*60)
    patterns = never_appeared_by_sum[13]
    print(f"合計: {len(patterns)}個\n")
    
    # 1,3,9を含むパターンを特定
    patterns_139 = [p for p in patterns if set(p) == {'1', '3', '9'}]
    print(f"{{1,3,9}}の順列:")
    for p in patterns_139:
        print(f"  - {p}")
    
    print(f"\nすべてのパターン:")
    for i, p in enumerate(patterns, 1):
        marker = " ⭐" if set(p) == {'1', '3', '9'} else ""
        print(f"  {i:2d}. {p}{marker}")

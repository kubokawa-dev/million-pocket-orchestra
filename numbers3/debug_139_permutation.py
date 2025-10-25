"""順列完全網羅モデルで139がなぜ生成されないか調査"""
import sys
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from numbers3.prediction_logic import predict_from_permutation_coverage

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

# numbersを各桁に分割する（Numbers3は3桁）
df['d1'] = df['numbers'].str[0]
df['d2'] = df['numbers'].str[1]
df['d3'] = df['numbers'].str[2]

# データ型を整数に変換
for col in ['d1', 'd2', 'd3']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()
for col in ['d1', 'd2', 'd3']:
    df[col] = df[col].astype(int)

# 最近100回の数字出現頻度を確認
recent_df = df.tail(100)
all_recent_digits = pd.concat([recent_df[f'd{i+1}'] for i in range(3)])
digit_freq = Counter(all_recent_digits)

print("\n" + "="*60)
print("【最近100回の数字出現頻度】")
print("="*60)
for digit, count in digit_freq.most_common():
    print(f"数字 {digit}: {count}回")

print("\n" + "="*60)
print("【1, 3, 9の出現頻度】")
print("="*60)
for digit in [1, 3, 9]:
    print(f"数字 {digit}: {digit_freq.get(digit, 0)}回")

# 順列完全網羅モデルで予測
print("\n順列完全網羅モデルで予測を生成中...")
predictions = predict_from_permutation_coverage(df, limit=300)  # limitを300に増加

print(f"\n生成された予測数: {len(predictions)}")

# 139の順列をチェック
permutations_139 = ['139', '193', '319', '391', '913', '931']

print("\n" + "="*60)
print("【{1, 3, 9}の順列チェック（順列完全網羅モデル単体）】")
print("="*60)

for perm in permutations_139:
    if perm in predictions:
        rank = predictions.index(perm) + 1
        print(f"✅ {perm}: {rank}位（モデル内順位）")
    else:
        print(f"❌ {perm}: 生成されていません（limit=200の範囲外）")

# 合計値13のパターンを確認
print("\n" + "="*60)
print("【合計値13のパターン（予測に含まれるもの）】")
print("="*60)
sum_13_patterns = [p for p in predictions if sum(int(d) for d in p) == 13]
print(f"合計値13のパターン数: {len(sum_13_patterns)}")
for i, p in enumerate(sum_13_patterns[:20], 1):
    marker = "⭐" if p in permutations_139 else "  "
    print(f"{marker} {i:2d}. {p}")

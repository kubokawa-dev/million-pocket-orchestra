"""順列完全網羅モデル単体をデバッグ"""
import sys
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

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

# 順列完全網羅モデルで予測
print("順列完全網羅モデルで予測を生成中...")
predictions = predict_from_permutation_coverage(df, limit=200)

print(f"\n生成された予測数: {len(predictions)}")

# 204の順列をチェック
permutations_204 = ['204', '240', '024', '042', '402', '420']

print("\n" + "="*60)
print("【{2, 0, 4}の順列チェック（順列完全網羅モデル単体）】")
print("="*60)

for perm in permutations_204:
    if perm in predictions:
        rank = predictions.index(perm) + 1
        print(f"✅ {perm}: {rank}位（モデル内順位）")
    else:
        print(f"❌ {perm}: 生成されていません")

# 上位50を表示
print("\n" + "="*60)
print("【順列完全網羅モデル - トップ50】")
print("="*60)
for i, pred in enumerate(predictions[:50], 1):
    marker = "⭐" if pred in permutations_204 else "  "
    print(f"{marker} {i:2d}位: {pred}")

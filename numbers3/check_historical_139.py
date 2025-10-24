"""139とその順列が過去に出現したか確認するスクリプト"""
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """データベース接続を取得する"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

# データベースから全データを取得
conn = get_db_connection()
df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date DESC", conn)
conn.close()

# 139とその順列をチェック
permutations_139 = ['139', '193', '319', '391', '913', '931']

print("\n" + "="*60)
print("【{1, 3, 9}の順列 - 過去の出現履歴】")
print("="*60)

for perm in permutations_139:
    matches = df[df['numbers'] == perm]
    if not matches.empty:
        print(f"✅ {perm}: 過去に{len(matches)}回出現")
        for _, row in matches.head(5).iterrows():
            print(f"    - {row['draw_date']}")
    else:
        print(f"❌ {perm}: 過去に出現なし（未出現パターン）")

print(f"\n総抽選回数: {len(df)}回")
print(f"ユニークな出現番号数: {df['numbers'].nunique()}個")

# 最近の当選番号トップ10
print("\n" + "="*60)
print("【最近の当選番号トップ10】")
print("="*60)
for idx, row in df.head(10).iterrows():
    print(f"{row['draw_date']}: {row['numbers']}")

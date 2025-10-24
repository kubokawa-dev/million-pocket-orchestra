"""limitと選択数の関係を確認"""
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

# データベースからすべての抽選データを読み込む
conn = get_db_connection()
df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date ASC", conn)
conn.close()

historical_numbers = set(df['numbers'].values)

# 未出現パターンを合計値でグループ化
never_appeared_by_sum = {}
for num in range(1000):
    num_str = f"{num:03d}"
    if num_str not in historical_numbers:
        pred_sum = sum(int(d) for d in num_str)
        if pred_sum not in never_appeared_by_sum:
            never_appeared_by_sum[pred_sum] = []
        never_appeared_by_sum[pred_sum].append(num_str)

print("\n" + "="*60)
print("【合計値ごとの選択数シミュレーション（limit=200）】")
print("="*60)

limit = 200
cumulative = 0

for target_sum in range(28):
    if target_sum in never_appeared_by_sum:
        group = never_appeared_by_sum[target_sum]
        
        # 選択数を計算
        if 10 <= target_sum <= 17:
            select_count = len(group)  # 全て
        elif 5 <= target_sum <= 22:
            select_count = min(30, len(group))
        else:
            select_count = min(15, len(group))
        
        cumulative += select_count
        marker = " ⭐" if target_sum == 13 else ""
        stop_marker = " ← ここで limit * 0.9 = 180 に達する" if cumulative >= limit * 0.9 and cumulative - select_count < limit * 0.9 else ""
        
        print(f"合計値{target_sum:2d}: {len(group):3d}個中 {select_count:3d}個選択 (累計: {cumulative:4d}){marker}{stop_marker}")
        
        if cumulative >= limit * 0.9:
            print(f"\n⚠️ limit * 0.9 = {limit * 0.9} に達したため、ここで第1ラウンド終了")
            print(f"   合計値{target_sum}まで到達、合計値{target_sum+1}以降は未選択")
            break

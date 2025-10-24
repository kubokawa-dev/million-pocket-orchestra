"""第6838回当選番号 518 の予測失敗分析"""
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("\n" + "="*80)
print("ナンバーズ3 第6838回 当選番号 518 の予測失敗分析")
print("="*80)

# 1. 最新の予測を取得
cur.execute("""
    SELECT id, created_at, target_draw_number
    FROM numbers3_ensemble_predictions
    ORDER BY created_at DESC
    LIMIT 1
""")
latest_prediction = cur.fetchone()

if latest_prediction:
    prediction_id, created_at, target_draw = latest_prediction
    print(f"\n【最新の予測】")
    print(f"  予測ID: {prediction_id}")
    print(f"  作成日時: {created_at}")
    print(f"  対象抽選回: 第{target_draw}回")
    
    # 予測候補を取得
    cur.execute("""
        SELECT number, rank, score, contributing_models
        FROM numbers3_prediction_candidates
        WHERE ensemble_prediction_id = %s
        ORDER BY rank
    """, (prediction_id,))
    
    candidates = cur.fetchall()
    print(f"\n【予測候補】({len(candidates)}件)")
    
    found_518 = False
    for number, rank, score, models in candidates[:20]:
        print(f"  {rank:2d}位: {number} (スコア: {score:.2f})")
        if number == '518':
            found_518 = True
            print(f"       ↑ ✅ 518を発見！")
    
    if not found_518:
        print(f"\n  ❌ 518は予測候補に含まれていません")
        
        # 全候補をチェック
        if any(n[0] == '518' for n in candidates):
            rank_518 = next(n[1] for n in candidates if n[0] == '518')
            print(f"  （518は{rank_518}位に含まれています）")

# 2. 518の特性分析
print("\n" + "="*80)
print("【518の特性分析】")
print("="*80)

digits = [5, 1, 8]
print(f"\n桁構成: {digits}")
print(f"合計値: {sum(digits)}")
print(f"偶数/奇数: {'奇数' if digits[0] % 2 == 1 else '偶数'}-{'奇数' if digits[1] % 2 == 1 else '偶数'}-{'偶数' if digits[2] % 2 == 1 else '偶数'}")
print(f"偶数の数: {sum(1 for d in digits if d % 2 == 0)}個")

# 3. 過去の出現履歴
cur.execute("""
    SELECT draw_number, draw_date, numbers
    FROM numbers3_draws
    ORDER BY draw_date DESC
    LIMIT 100
""")
recent_draws = cur.fetchall()

df_draws = pd.DataFrame(recent_draws, columns=['draw_number', 'draw_date', 'numbers'])
df_draws['d1'] = df_draws['numbers'].str[0].astype(int)
df_draws['d2'] = df_draws['numbers'].str[1].astype(int)
df_draws['d3'] = df_draws['numbers'].str[2].astype(int)
df_draws['sum'] = df_draws['d1'] + df_draws['d2'] + df_draws['d3']

print(f"\n【過去100回の統計】")

# 合計値の分布
sum_counter = Counter(df_draws['sum'])
print(f"\n合計値の分布:")
print(f"  518の合計値14: {sum_counter[14]}回 ({sum_counter[14]/len(df_draws)*100:.1f}%)")
print(f"  最頻値: {sum_counter.most_common(1)[0][0]} ({sum_counter.most_common(1)[0][1]}回)")
print(f"  平均: {df_draws['sum'].mean():.1f}")

# 各桁の出現頻度
all_digits = pd.concat([df_draws['d1'], df_draws['d2'], df_draws['d3']])
digit_counter = Counter(all_digits)

print(f"\n各桁の出現頻度:")
for digit in [5, 1, 8]:
    freq = digit_counter[digit]
    percentile = sum(1 for v in digit_counter.values() if v < freq) / len(digit_counter) * 100
    print(f"  数字{digit}: {freq}回 (下位から{percentile:.0f}%)")

# 518が過去に出現したか
cur.execute("""
    SELECT draw_number, draw_date
    FROM numbers3_draws
    WHERE numbers = '518'
    ORDER BY draw_date DESC
    LIMIT 5
""")
past_518 = cur.fetchall()

print(f"\n【518の過去の出現】")
if past_518:
    print(f"  過去{len(past_518)}回出現:")
    for draw_num, draw_date in past_518:
        print(f"    第{draw_num}回 ({draw_date})")
else:
    print(f"  過去に一度も出現していません（非常に珍しい）")

# 4. モデル別の予測傾向
print("\n" + "="*80)
print("【モデル別の予測傾向】")
print("="*80)

if latest_prediction:
    cur.execute("""
        SELECT model_predictions
        FROM numbers3_ensemble_predictions
        WHERE id = %s
    """, (prediction_id,))
    
    import json
    model_preds = json.loads(cur.fetchone()[0])
    
    for model_name, model_data in model_preds.items():
        predictions = model_data.get('predictions', [])
        print(f"\n{model_name}: {len(predictions)}件")
        
        # 各モデルの予測の合計値分布
        model_sums = [sum(int(d) for d in p) for p in predictions]
        if model_sums:
            print(f"  合計値範囲: {min(model_sums)}-{max(model_sums)}")
            print(f"  平均合計値: {sum(model_sums)/len(model_sums):.1f}")
            if 14 in model_sums:
                print(f"  ✅ 合計値14を含む")
            else:
                print(f"  ❌ 合計値14を含まない")
        
        # 518が含まれているか
        if '518' in predictions:
            print(f"  ✅ 518を予測している！")
        else:
            print(f"  ❌ 518を予測していない")

# 5. 予測カバレッジ分析
print("\n" + "="*80)
print("【予測カバレッジ分析】")
print("="*80)

if latest_prediction:
    cur.execute("""
        SELECT number
        FROM numbers3_prediction_candidates
        WHERE ensemble_prediction_id = %s
    """, (prediction_id,))
    
    all_predictions = [r[0] for r in cur.fetchall()]
    pred_sums = [sum(int(d) for d in p) for p in all_predictions]
    
    print(f"\n予測候補数: {len(all_predictions)}件")
    print(f"合計値の範囲: {min(pred_sums)}-{max(pred_sums)}")
    print(f"合計値14の予測数: {pred_sums.count(14)}件")
    
    # 合計値別の分布
    sum_dist = Counter(pred_sums)
    print(f"\n合計値の分布:")
    for s in sorted(sum_dist.keys()):
        bar = "█" * sum_dist[s]
        marker = " ← 518はここ" if s == 14 else ""
        print(f"  {s:2d}: {bar} ({sum_dist[s]}件){marker}")

conn.close()

print("\n" + "="*80)
print("分析完了")
print("="*80)

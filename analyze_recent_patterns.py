"""
最近の当選番号のパターンを詳細分析
第6843回(631)と第6844回(656)を含む直近データを分析
"""
import psycopg2
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# 最新20回を取得
cur.execute("""
    SELECT draw_number, draw_date, numbers 
    FROM numbers3_draws 
    ORDER BY draw_number DESC 
    LIMIT 20
""")
results = cur.fetchall()

print("="*80)
print("📊 最近20回の当選番号パターン分析")
print("="*80)

# 逆順にして時系列順に
results = list(reversed(results))

print("\n【最近20回の当選番号】")
for i, (draw_num, draw_date, numbers) in enumerate(results, 1):
    d1, d2, d3 = int(numbers[0]), int(numbers[1]), int(numbers[2])
    total = d1 + d2 + d3
    print(f"{i:2d}. 第{draw_num}回: {numbers} (合計:{total:2d}) - {draw_date}")

print("\n" + "="*80)
print("【パターン分析】")
print("="*80)

# 各桁の出現頻度
digit_freq = [Counter(), Counter(), Counter()]
for draw_num, draw_date, numbers in results:
    digit_freq[0][int(numbers[0])] += 1
    digit_freq[1][int(numbers[1])] += 1
    digit_freq[2][int(numbers[2])] += 1

print("\n1. 各桁の出現頻度（最近20回）")
for i in range(3):
    print(f"\n  【{i+1}桁目】")
    for digit, count in digit_freq[i].most_common():
        bar = "█" * count
        print(f"    {digit}: {bar} ({count}回)")

# 合計値の分布
sum_dist = Counter()
for draw_num, draw_date, numbers in results:
    total = sum(int(d) for d in numbers)
    sum_dist[total] += 1

print("\n2. 合計値の分布")
for total, count in sorted(sum_dist.items()):
    bar = "█" * count
    print(f"  合計{total:2d}: {bar} ({count}回)")

# 前回からの変化
print("\n3. 前回からの変化パターン（直近10回）")
recent_10 = results[-10:]
for i in range(1, len(recent_10)):
    prev = recent_10[i-1][2]
    curr = recent_10[i][2]
    prev_digits = [int(d) for d in prev]
    curr_digits = [int(d) for d in curr]
    diff = [curr_digits[j] - prev_digits[j] for j in range(3)]
    print(f"  第{recent_10[i][0]}回({curr}) ← 第{recent_10[i-1][0]}回({prev}): 変化 [{diff[0]:+2d}, {diff[1]:+2d}, {diff[2]:+2d}]")

# 同じ数字の出現
print("\n4. 同じ数字が複数桁に出現するパターン")
for draw_num, draw_date, numbers in results[-10:]:
    digits = [int(d) for d in numbers]
    if len(set(digits)) < 3:
        print(f"  第{draw_num}回: {numbers} - 重複あり")

# 連続数字のパターン
print("\n5. 連続数字のパターン")
for draw_num, draw_date, numbers in results[-10:]:
    digits = sorted([int(d) for d in numbers])
    is_consecutive = (digits[1] - digits[0] == 1 and digits[2] - digits[1] == 1)
    if is_consecutive:
        print(f"  第{draw_num}回: {numbers} - 連続数字")

# 第6843回と第6844回の詳細分析
print("\n" + "="*80)
print("【第6843回(631)と第6844回(656)の詳細分析】")
print("="*80)

if len(results) >= 2:
    r6843 = None
    r6844 = None
    for r in results:
        if r[2] == '631':
            r6843 = r
        if r[2] == '656':
            r6844 = r
    
    if r6843:
        print(f"\n第6843回: 631")
        print(f"  各桁: 6, 3, 1")
        print(f"  合計: 10")
        print(f"  特徴: 降順、数字が離れている")
    
    if r6844:
        print(f"\n第6844回: 656")
        print(f"  各桁: 6, 5, 6")
        print(f"  合計: 17")
        print(f"  特徴: 6が2回出現、5が中央")
        
    if r6843 and r6844:
        print(f"\n変化:")
        print(f"  1桁目: 6 → 6 (変化なし)")
        print(f"  2桁目: 3 → 5 (+2)")
        print(f"  3桁目: 1 → 6 (+5)")
        print(f"  合計: 10 → 17 (+7)")
        print(f"\n⚠️ 重要な気づき:")
        print(f"  - 1桁目の6が連続")
        print(f"  - 3桁目が大きく増加(+5)")
        print(f"  - 同じ数字(6)が2回出現")

cur.close()
conn.close()

print("\n" + "="*80)
print("【改善の方向性】")
print("="*80)
print("1. 同じ数字が複数回出現するパターンを考慮")
print("2. 前回の数字が連続する可能性を重視")
print("3. 大きな変化(±3以上)も考慮")
print("4. 合計値の幅を広げる（10→17のような大きな変化）")
print("="*80)

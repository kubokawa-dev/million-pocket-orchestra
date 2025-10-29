"""
ナンバーズ4 第6843回(0523)と第6844回(0017)のパターン分析
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

print("="*80)
print("📊 ナンバーズ4 パターン分析")
print("="*80)

# 最新20回を取得
cur.execute("""
    SELECT draw_number, draw_date, numbers 
    FROM numbers4_draws 
    ORDER BY draw_number DESC 
    LIMIT 20
""")
results = list(reversed(cur.fetchall()))

print("\n【最近20回の当選番号】")
for i, (draw_num, draw_date, numbers) in enumerate(results, 1):
    d1, d2, d3, d4 = int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3])
    total = d1 + d2 + d3 + d4
    # 0の個数をカウント
    zero_count = numbers.count('0')
    # 同じ数字の個数
    digit_counts = Counter(numbers)
    max_repeat = max(digit_counts.values())
    
    print(f"{i:2d}. 第{draw_num}回: {numbers} (合計:{total:2d}, 0の数:{zero_count}, 最大重複:{max_repeat}) - {draw_date}")

print("\n" + "="*80)
print("【第6843回(0523)と第6844回(0017)の詳細分析】")
print("="*80)

# 第6843回と第6844回を探す
r6843 = None
r6844 = None
for r in results:
    if r[2] == '0523':
        r6843 = r
    if r[2] == '0017':
        r6844 = r

if r6843:
    print(f"\n第6843回: 0523")
    print(f"  各桁: 0, 5, 2, 3")
    print(f"  合計: 10")
    print(f"  特徴:")
    print(f"    - 0が1個（1桁目）")
    print(f"    - 全て異なる数字")
    print(f"    - 合計値が小さい（10）")

if r6844:
    print(f"\n第6844回: 0017")
    print(f"  各桁: 0, 0, 1, 7")
    print(f"  合計: 8")
    print(f"  特徴:")
    print(f"    - 0が2個（1桁目と2桁目）⭐重要")
    print(f"    - 連続する0（00）⭐重要")
    print(f"    - 合計値が非常に小さい（8）⭐重要")
    print(f"    - 1桁目が0で連続（0523→0017）⭐重要")

if r6843 and r6844:
    print(f"\n変化:")
    print(f"  1桁目: 0 → 0 (変化なし) ⭐継続")
    print(f"  2桁目: 5 → 0 (-5)")
    print(f"  3桁目: 2 → 1 (-1)")
    print(f"  4桁目: 3 → 7 (+4)")
    print(f"  合計: 10 → 8 (-2)")
    
    print(f"\n⚠️ 重要な気づき:")
    print(f"  1. 1桁目の0が2回連続 ⭐")
    print(f"  2. 0が2個出現（00で連続）⭐")
    print(f"  3. 合計値が極端に小さい（8）⭐")
    print(f"  4. 小さい数字が多い（0,0,1,7）⭐")

# 0の出現パターンを分析
print("\n" + "="*80)
print("【0の出現パターン分析（最近20回）】")
print("="*80)

zero_patterns = []
for draw_num, draw_date, numbers in results:
    zero_count = numbers.count('0')
    zero_positions = [i+1 for i, d in enumerate(numbers) if d == '0']
    if zero_count > 0:
        zero_patterns.append((draw_num, numbers, zero_count, zero_positions))

print(f"\n0を含む当選番号: {len(zero_patterns)}件")
for draw_num, numbers, zero_count, positions in zero_patterns[-10:]:
    print(f"  第{draw_num}回: {numbers} - 0が{zero_count}個（{positions}桁目）")

# 連続する同じ数字のパターン
print("\n" + "="*80)
print("【連続する同じ数字のパターン】")
print("="*80)

consecutive_patterns = []
for draw_num, draw_date, numbers in results:
    for i in range(3):
        if numbers[i] == numbers[i+1]:
            consecutive_patterns.append((draw_num, numbers, i+1, numbers[i]))

print(f"\n連続する同じ数字を含む: {len(consecutive_patterns)}件")
for draw_num, numbers, pos, digit in consecutive_patterns[-10:]:
    print(f"  第{draw_num}回: {numbers} - {digit}が{pos}-{pos+1}桁目で連続")

# 合計値の分布
print("\n" + "="*80)
print("【合計値の分布（最近20回）】")
print("="*80)

sum_dist = Counter()
for draw_num, draw_date, numbers in results:
    total = sum(int(d) for d in numbers)
    sum_dist[total] += 1

print("\n合計値の分布:")
for total in sorted(sum_dist.keys()):
    bar = "█" * sum_dist[total]
    print(f"  合計{total:2d}: {bar} ({sum_dist[total]}回)")

print(f"\n最小合計値: {min(sum_dist.keys())}")
print(f"最大合計値: {max(sum_dist.keys())}")

cur.close()
conn.close()

print("\n" + "="*80)
print("【改善の方向性】")
print("="*80)
print("1. ⭐ 0が複数個出現するパターンを重視（特に連続する00）")
print("2. ⭐ 1桁目の数字が連続するパターンを最優先")
print("3. ⭐ 極端に小さい合計値（5-10）を考慮")
print("4. ⭐ 小さい数字（0,1,2,3）の組み合わせを重視")
print("5. 連続する同じ数字のパターンを強化")
print("="*80)

"""改善後のシステムで518が予測されるかチェック"""
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

# 最新の予測を取得
cur.execute("""
    SELECT id, created_at, target_draw_number
    FROM numbers3_ensemble_predictions
    ORDER BY created_at DESC
    LIMIT 1
""")

latest_prediction = cur.fetchone()

if latest_prediction:
    prediction_id, created_at, target_draw = latest_prediction
    print("\n" + "="*80)
    print(f"最新の予測（ID: {prediction_id}）で518が含まれているかチェック")
    print("="*80)
    
    # すべての予測候補を取得
    cur.execute("""
        SELECT number, rank, score, contributing_models
        FROM numbers3_prediction_candidates
        WHERE ensemble_prediction_id = %s
        ORDER BY rank
    """, (prediction_id,))
    
    all_candidates = cur.fetchall()
    
    print(f"\n総予測候補数: {len(all_candidates)}件")
    
    # 518を探す
    found_518 = False
    for number, rank, score, models in all_candidates:
        if number == '518':
            found_518 = True
            print(f"\n✅ ✅ ✅ 518を発見しました！ ✅ ✅ ✅")
            print(f"  順位: {rank}位")
            print(f"  スコア: {score:.2f}")
            print(f"  貢献モデル: {models}")
            break
    
    if not found_518:
        print(f"\n❌ 518は予測候補に含まれていません")
    
    # 合計値14のパターンをチェック
    print(f"\n" + "="*80)
    print("合計値14のパターン")
    print("="*80)
    
    sum14_patterns = []
    for number, rank, score, models in all_candidates:
        if sum(int(d) for d in number) == 14:
            sum14_patterns.append((number, rank, score))
    
    if sum14_patterns:
        print(f"\n合計値14のパターン: {len(sum14_patterns)}件")
        for num, rank, score in sum14_patterns[:20]:
            marker = " ← 518" if num == '518' else ""
            print(f"  {rank:3d}位: {num} (スコア: {score:.2f}){marker}")
    else:
        print(f"\n合計値14のパターンは0件です")
    
    # 合計値の分布
    print(f"\n" + "="*80)
    print("合計値の分布")
    print("="*80)
    
    sum_dist = Counter()
    for number, _, _, _ in all_candidates:
        digit_sum = sum(int(d) for d in number)
        sum_dist[digit_sum] += 1
    
    print(f"\n予測候補の合計値範囲: {min(sum_dist.keys())}-{max(sum_dist.keys())}")
    for s in sorted(sum_dist.keys()):
        bar = "█" * min(sum_dist[s], 50)
        marker = " ← 518はここ" if s == 14 else ""
        print(f"  合計{s:2d}: {bar} ({sum_dist[s]}件){marker}")
    
    # モデル別の貢献を確認
    print(f"\n" + "="*80)
    print("改善前後の比較")
    print("="*80)
    
    # 改善前（予測ID 5）と比較
    cur.execute("""
        SELECT COUNT(*)
        FROM numbers3_prediction_candidates
        WHERE ensemble_prediction_id = 5
    """)
    old_count = cur.fetchone()[0]
    
    print(f"\n改善前（予測ID 5）: {old_count}件")
    print(f"改善後（予測ID {prediction_id}）: {len(all_candidates)}件")
    print(f"増加率: {(len(all_candidates) - old_count) / old_count * 100:.1f}%")

conn.close()

print("\n" + "="*80)
print("チェック完了")
print("="*80)

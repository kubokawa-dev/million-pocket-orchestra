"""最強モデル v3.0 で518が予測されるかチェック"""
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
    SELECT id, created_at, target_draw_number, notes
    FROM numbers3_ensemble_predictions
    ORDER BY created_at DESC
    LIMIT 1
""")

latest_prediction = cur.fetchone()

if latest_prediction:
    prediction_id, created_at, target_draw, notes = latest_prediction
    print("\n" + "="*80)
    print(f"🔥 最強モデル v3.0 検証レポート")
    print("="*80)
    print(f"\n予測ID: {prediction_id}")
    print(f"バージョン: {notes}")
    print(f"対象抽選回: 第{target_draw}回")
    
    # すべての予測候補を取得
    cur.execute("""
        SELECT number, rank, score, contributing_models
        FROM numbers3_prediction_candidates
        WHERE ensemble_prediction_id = %s
        ORDER BY rank
    """, (prediction_id,))
    
    all_candidates = cur.fetchall()
    
    print(f"\n📊 基本統計")
    print(f"  総予測候補数: {len(all_candidates)}件")
    
    # 518を探す
    print(f"\n" + "="*80)
    print("🎯 518の検索結果")
    print("="*80)
    
    found_518 = False
    for number, rank, score, models in all_candidates:
        if number == '518':
            found_518 = True
            print(f"\n✅✅✅ 518を発見しました！ ✅✅✅")
            print(f"  順位: {rank}位")
            print(f"  スコア: {score:.2f}")
            print(f"  貢献モデル: {models}")
            
            # 上位何%に入っているか
            percentile = (rank / len(all_candidates)) * 100
            print(f"  パーセンタイル: 上位{percentile:.1f}%")
            break
    
    if not found_518:
        print(f"\n❌ 518は予測候補に含まれていません")
        print(f"   しかし、候補数は{len(all_candidates)}件に増加しています")
    
    # 合計値14のパターンをチェック
    print(f"\n" + "="*80)
    print("📈 合計値14のパターン（518が含まれる範囲）")
    print("="*80)
    
    sum14_patterns = []
    for number, rank, score, models in all_candidates:
        if sum(int(d) for d in number) == 14:
            sum14_patterns.append((number, rank, score, models))
    
    if sum14_patterns:
        print(f"\n合計値14のパターン: {len(sum14_patterns)}件")
        for num, rank, score, models in sum14_patterns[:30]:
            marker = " ← ★518★" if num == '518' else ""
            print(f"  {rank:3d}位: {num} (スコア: {score:.2f}){marker}")
            if len(models) > 50:
                print(f"         貢献: {models[:50]}...")
    else:
        print(f"\n合計値14のパターンは0件です")
    
    # 合計値の分布
    print(f"\n" + "="*80)
    print("📊 合計値の分布")
    print("="*80)
    
    sum_dist = Counter()
    for number, _, _, _ in all_candidates:
        digit_sum = sum(int(d) for d in number)
        sum_dist[digit_sum] += 1
    
    print(f"\n予測候補の合計値範囲: {min(sum_dist.keys())}-{max(sum_dist.keys())}")
    for s in sorted(sum_dist.keys()):
        bar = "█" * min(sum_dist[s], 60)
        marker = " ← 518はここ" if s == 14 else ""
        print(f"  合計{s:2d}: {bar} ({sum_dist[s]}件){marker}")
    
    # モデル別の貢献度
    print(f"\n" + "="*80)
    print("🤖 モデル別の貢献度")
    print("="*80)
    
    import json
    cur.execute("""
        SELECT model_predictions
        FROM numbers3_ensemble_predictions
        WHERE id = %s
    """, (prediction_id,))
    
    model_preds_json = cur.fetchone()[0]
    model_preds = json.loads(model_preds_json)
    
    print(f"\n各モデルの予測数:")
    total_predictions = 0
    for model_name, predictions in model_preds.items():
        count = len(predictions)
        total_predictions += count
        
        # 518が含まれているか
        contains_518 = '518' in predictions
        marker = " ✅ 518を含む" if contains_518 else ""
        
        print(f"  {model_name:25s}: {count:3d}件{marker}")
        
        if contains_518:
            idx = predictions.index('518')
            print(f"    → 518は{idx+1}番目の予測")
    
    print(f"\n  合計: {total_predictions}件（重複除外前）")
    
    # 改善前後の比較
    print(f"\n" + "="*80)
    print("📈 改善の軌跡")
    print("="*80)
    
    cur.execute("""
        SELECT id, created_at, predictions_count, notes
        FROM numbers3_ensemble_predictions
        ORDER BY created_at
    """)
    
    all_predictions = cur.fetchall()
    
    print(f"\n予測履歴:")
    for pid, ptime, pcount, pnotes in all_predictions:
        marker = " ← 最新（最強版）" if pid == prediction_id else ""
        print(f"  ID {pid}: {pcount}件 - {pnotes[:60]}{marker}")
    
    if len(all_predictions) > 1:
        first_count = all_predictions[0][2]
        latest_count = len(all_candidates)
        improvement = ((latest_count - first_count) / first_count) * 100
        print(f"\n  改善率: 初回{first_count}件 → 最新{latest_count}件 (+{improvement:.0f}%)")

conn.close()

print("\n" + "="*80)
print("✅ 検証完了")
print("="*80)

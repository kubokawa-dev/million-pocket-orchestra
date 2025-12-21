"""
予測履歴をテーブル形式で表示するスクリプト

使い方:
  python numbers4/show_prediction_table.py [--limit 20]
"""

import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from numbers4.save_prediction_history import get_db_connection


def get_prediction_table(limit: int = 20):
    """予測履歴をテーブル用のデータとして取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 予測履歴とモデル別の予測を取得
        cur.execute("""
            SELECT 
                p.id,
                p.created_at,
                p.target_draw_number,
                p.top_predictions,
                p.actual_draw_number,
                p.actual_numbers,
                p.hit_status,
                p.hit_count
            FROM numbers4_ensemble_predictions p
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        
        # 実際の当選番号をDBから取得
        cur.execute("""
            SELECT draw_number, numbers
            FROM numbers4_draws
            ORDER BY draw_number DESC
            LIMIT 100
        """)
        actual_draws = {row[0]: row[1] for row in cur.fetchall()}
        
        results = []
        for row in rows:
            pred_id = row[0]
            created_at = row[1]
            target_draw = row[2]
            top_predictions = eval(row[3]) if row[3] else []
            actual_draw = row[4]
            actual_numbers = row[5]
            hit_status = row[6]
            hit_count = row[7]
            
            # top_predictionsから上位5件を取得
            top5 = [p['number'] for p in top_predictions[:5]] if top_predictions else []
            
            # 実際の当選番号がDBにあるかチェック（未更新の場合）
            if not actual_numbers and target_draw in actual_draws:
                actual_numbers = actual_draws[target_draw]
                db_has_result = True
            else:
                db_has_result = False
            
            results.append({
                'id': pred_id,
                'created_at': created_at,
                'target_draw': target_draw,
                'top5': top5,
                'actual_numbers': actual_numbers,
                'hit_status': hit_status,
                'hit_count': hit_count,
                'db_has_result': db_has_result
            })
        
        return results
        
    finally:
        conn.close()


def print_table(data: List[Dict], show_all: bool = False):
    """テーブル形式で表示"""
    
    print("\n" + "="*140)
    print("📊 ナンバーズ4 予測履歴テーブル")
    print("="*140)
    
    # ヘッダー
    print(f"{'ID':<6} {'回号':<8} {'当選番号':<10} {'予測トップ5':<40} {'結果':<15} {'備考':<20}")
    print("-"*140)
    
    for row in data:
        pred_id = row['id']
        target = f"第{row['target_draw']}回" if row['target_draw'] else "未設定"
        actual = row['actual_numbers'] if row['actual_numbers'] else "-"
        top5 = ", ".join(row['top5'][:5]) if row['top5'] else "-"
        
        # 結果の表示
        if row['hit_status'] == 'exact':
            result = f"🎯 ストレート ({row['hit_count']}桁)"
        elif row['hit_status'] == 'box':
            result = f"📦 ボックス的中! (4桁)"
        elif row['hit_status'] == 'partial':
            result = f"🎲 部分一致 ({row['hit_count']}桁)"
        elif row['hit_status'] == 'miss':
            result = f"❌ 外れ ({row['hit_count']}桁)"
        else:
            result = "⏳ 未判明"
        
        # 備考
        notes = ""
        if row['db_has_result'] and not row['hit_status']:
            notes = "⚠️ 更新可能"
        
        print(f"{pred_id:<6} {target:<8} {actual:<10} {top5:<40} {result:<15} {notes:<20}")
    
    print("="*140)
    
    # 統計情報
    total = len(data)
    updated = sum(1 for r in data if r['hit_status'])
    can_update = sum(1 for r in data if r['db_has_result'] and not r['hit_status'])
    
    print(f"\n📈 統計: 総予測数={total}件 | 結果更新済み={updated}件 | 更新可能={can_update}件")
    
    if can_update > 0:
        print(f"\n💡 ヒント: {can_update}件の予測結果を更新できます！")
        print("   更新コマンド例: /prediction-update prediction_id=<ID> actual_numbers=<番号>")


def main():
    parser = argparse.ArgumentParser(
        description='予測履歴をテーブル形式で表示'
    )
    parser.add_argument('--limit', type=int, default=20, help='表示件数（デフォルト: 20）')
    parser.add_argument('--all', action='store_true', help='全ての予測を表示')
    
    args = parser.parse_args()
    
    limit = 1000 if args.all else args.limit
    
    data = get_prediction_table(limit)
    print_table(data, args.all)


if __name__ == '__main__':
    main()


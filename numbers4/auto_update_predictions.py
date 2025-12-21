"""
更新可能な予測結果を自動で一括更新するスクリプト

使い方:
  # ドライラン（更新せずに確認のみ）
  python numbers4/auto_update_predictions.py --dry-run
  
  # 実際に更新
  python numbers4/auto_update_predictions.py
  
  # 特定の件数のみ更新
  python numbers4/auto_update_predictions.py --limit 10
"""

import sys
import os
import argparse
from typing import List, Dict, Tuple

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from numbers4.save_prediction_history import (
    get_db_connection,
    update_prediction_result
)


def get_updatable_predictions() -> List[Tuple[int, int, str]]:
    """
    更新可能な予測を取得
    
    Returns:
        List[(prediction_id, target_draw_number, actual_numbers)]
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 実際の当選番号をDBから取得
        cur.execute("""
            SELECT draw_number, numbers
            FROM numbers4_draws
            ORDER BY draw_number DESC
            LIMIT 200
        """)
        actual_draws = {row[0]: row[1] for row in cur.fetchall()}
        
        # 未更新の予測で、DBに当選番号があるものを取得
        cur.execute("""
            SELECT id, target_draw_number
            FROM numbers4_ensemble_predictions
            WHERE actual_numbers IS NULL
            AND target_draw_number IS NOT NULL
            ORDER BY created_at DESC
        """)
        
        updatable = []
        for pred_id, target_draw in cur.fetchall():
            if target_draw in actual_draws:
                updatable.append((pred_id, target_draw, actual_draws[target_draw]))
        
        return updatable
        
    finally:
        conn.close()


def preview_updates(updatable: List[Tuple[int, int, str]]):
    """更新内容をプレビュー表示"""
    print("\n" + "="*80)
    print("🔍 更新可能な予測一覧")
    print("="*80)
    
    if not updatable:
        print("\n更新可能な予測はありません。")
        return
    
    print(f"\n全{len(updatable)}件の予測を更新できます：\n")
    print(f"{'予測ID':<10} {'対象回号':<15} {'当選番号':<10}")
    print("-"*80)
    
    for pred_id, target_draw, actual_numbers in updatable:
        print(f"{pred_id:<10} 第{target_draw}回{' '*5} {actual_numbers:<10}")
    
    print("="*80)


def update_all(updatable: List[Tuple[int, int, str]], limit: int = None):
    """
    予測結果を一括更新
    
    Args:
        updatable: 更新対象のリスト
        limit: 更新件数の上限
    """
    if not updatable:
        print("\n更新可能な予測はありません。")
        return
    
    to_update = updatable[:limit] if limit else updatable
    
    print("\n" + "="*80)
    print("🚀 予測結果を更新中...")
    print("="*80)
    
    success_count = 0
    error_count = 0
    
    for i, (pred_id, target_draw, actual_numbers) in enumerate(to_update, 1):
        try:
            print(f"\n[{i}/{len(to_update)}] 予測ID: {pred_id} (第{target_draw}回 → {actual_numbers})")
            update_prediction_result(pred_id, target_draw, actual_numbers)
            success_count += 1
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            error_count += 1
    
    print("\n" + "="*80)
    print("📊 更新結果")
    print("="*80)
    print(f"✅ 成功: {success_count}件")
    if error_count > 0:
        print(f"❌ 失敗: {error_count}件")
    print("="*80)


def show_statistics():
    """更新後の統計を表示"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 的中統計
        cur.execute("""
            SELECT 
                hit_status,
                COUNT(*) as count,
                AVG(hit_count) as avg_hits
            FROM numbers4_ensemble_predictions
            WHERE actual_numbers IS NOT NULL
            GROUP BY hit_status
            ORDER BY 
                CASE hit_status
                    WHEN 'exact' THEN 1
                    WHEN 'partial' THEN 2
                    WHEN 'miss' THEN 3
                END
        """)
        
        stats = cur.fetchall()
        
        if stats:
            print("\n" + "="*80)
            print("📈 的中統計（全期間）")
            print("="*80)
            
            total = sum(row[1] for row in stats)
            
            for hit_status, count, avg_hits in stats:
                status_emoji = {
                    'exact': '🎯',
                    'box': '📦',
                    'partial': '🎲',
                    'miss': '❌'
                }.get(hit_status, '❓')
                
                status_label = {
                    'exact': 'Straight',
                    'box': 'Box Hit!',
                    'partial': 'Partial',
                    'miss': 'Miss'
                }.get(hit_status, hit_status)
                
                percentage = (count / total * 100) if total > 0 else 0
                
                print(f"{status_emoji} {status_label:10s}: {count:3d}件 ({percentage:5.1f}%) - 平均{avg_hits:.2f}桁一致")
            
            print(f"\n総評価数: {total}件")
            print("="*80)
        
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='更新可能な予測結果を自動で一括更新',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 更新内容を確認（実際には更新しない）
  python numbers4/auto_update_predictions.py --dry-run
  
  # 全ての更新可能な予測を更新
  python numbers4/auto_update_predictions.py
  
  # 最新10件のみ更新
  python numbers4/auto_update_predictions.py --limit 10
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                       help='更新せずに確認のみ（ドライラン）')
    parser.add_argument('--limit', type=int, 
                       help='更新件数の上限')
    parser.add_argument('--stats', action='store_true',
                       help='更新後に統計を表示')
    
    args = parser.parse_args()
    
    # 更新可能な予測を取得
    updatable = get_updatable_predictions()
    
    if args.dry_run:
        # ドライラン：確認のみ
        preview_updates(updatable)
        print("\n💡 実際に更新する場合は --dry-run を外して実行してください。")
    else:
        # 実際に更新
        preview_updates(updatable)
        
        if not updatable:
            return
        
        # 確認
        if args.limit:
            print(f"\n⚠️  最新{args.limit}件の予測を更新します。")
        else:
            print(f"\n⚠️  全{len(updatable)}件の予測を更新します。")
        
        response = input("続行しますか？ [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("キャンセルしました。")
            return
        
        # 更新実行
        update_all(updatable, args.limit)
        
        # 統計表示
        if args.stats or not args.limit:
            show_statistics()


if __name__ == '__main__':
    main()


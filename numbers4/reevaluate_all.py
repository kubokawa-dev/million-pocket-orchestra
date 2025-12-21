"""
全ての予測履歴に対して、的中判定（ストレート/ボックス/部分一致）を再計算するスクリプト
"""

import sys
import os
import json

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from numbers4.save_prediction_history import (
    get_db_connection,
    update_prediction_result
)

def reevaluate_all():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("\n" + "="*80)
        print("🔄 全予測履歴の再評価を開始します...")
        print("="*80)
        
        # 結果が入っている予測を取得
        cur.execute("""
            SELECT id, target_draw_number, actual_numbers
            FROM numbers4_ensemble_predictions
            WHERE actual_numbers IS NOT NULL
        """)
        
        rows = cur.fetchall()
        total = len(rows)
        print(f"\n対象件数: {total}件")
        
        for i, (pred_id, target_draw, actual_numbers) in enumerate(rows, 1):
            if i % 10 == 0:
                print(f"進捗: {i}/{total}件...")
            
            # update_prediction_result を呼び出すことで、新しく実装したボックス判定ロジックが適用される
            update_prediction_result(pred_id, target_draw, actual_numbers)
            
        print("\n" + "="*80)
        print("✅ 再評価が完了しました！")
        print("="*80)
        
    finally:
        conn.close()

if __name__ == '__main__':
    reevaluate_all()
    # 最後に統計を表示するために auto_update_predictions の関数を流用するか、
    # 直接 manage_prediction_history stats を実行





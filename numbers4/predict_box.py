"""
ナンバーズ4 ボックス・セット的中特化型予測システム
「数字の組み合わせ」の多様性を重視し、ボックス的中率を最大化します。
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, timezone

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from numbers4.predict_ensemble import generate_ensemble_prediction, get_db_connection
from numbers4.save_prediction_history import save_ensemble_prediction

def run_box_focused_prediction():
    print("\n" + "="*60)
    print("📦 Numbers 4 ボックス特化型予測システム 🚀")
    print("="*60)
    print("作戦: 数字の組み合わせ（ボックス）の重複を排除し、的中範囲を最大化します！")

    # 1. 通常のアンサンブル予測を実行（大量の候補を生成）
    # ※内部で多様性ペナルティなどは既にかかっているが、さらにボックスレベルでフィルタリングする
    print("\n[Step 1] アンサンブルモデルで候補を生成中...")
    final_predictions_df, ensemble_weights = generate_ensemble_prediction(progress_callback=print)

    if final_predictions_df.empty:
        print("❌ 予測の生成に失敗しました。")
        return

    # 2. ボックス（数字の組み合わせ）レベルでユニークな候補を選別
    print("\n[Step 2] ボックス（順不同）のユニーク選別を実行中...")
    
    seen_boxes = set()
    box_unique_rows = []
    
    for idx, row in final_predictions_df.iterrows():
        pred_num = row['prediction']
        # 数字をソートしてボックスIDを作成
        box_id = "".join(sorted(list(pred_num)))
        
        if box_id not in seen_boxes:
            seen_boxes.add(box_id)
            box_unique_rows.append(row)
        
        # 上位50通りのユニークなボックスが見つかったら終了（購入現実的な範囲）
        if len(box_unique_rows) >= 50:
            break

    box_predictions_df = pd.DataFrame(box_unique_rows).reset_index(drop=True)

    # 3. 結果の表示
    print("\n" + "="*40)
    print("🎯 ボックス・セット推奨 50選")
    print("="*40)
    print("これらは全て「数字の組み合わせ」が異なるユニークな候補です！")
    
    for idx, row in box_predictions_df.head(20).iterrows():
        print(f"  {idx+1:2d}位: {row['prediction']} (スコア: {row['score']:.1f})")

    # 4. DBに保存
    print("\n[Step 3] 予測結果をDBに保存中...")
    try:
        # モデル状態を読み込み
        model_path = os.path.join(os.path.dirname(__file__), 'model_state.json')
        model_state = None
        if os.path.exists(model_path):
            with open(model_path, 'r') as f:
                model_state = json.load(f)
        
        # 履歴を保存（notesにボックス特化であることを明記）
        prediction_id = save_ensemble_prediction(
            predictions_df=box_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model={}, # 詳細モデルデータは省略
            model_state=model_state,
            notes="Box-Focused Prediction v1.0: Optimized for unique digit combinations (Box/Set)."
        )
        print(f"✅ 予測履歴の保存が完了しました (ID: {prediction_id})")
    except Exception as e:
        print(f"❌ 履歴の保存に失敗しました: {e}")

    print("\n" + "="*60)
    print("💡 アドバイス:")
    print("  - これらの番号は「数字の組み合わせ」が重ならないように選ばれています。")
    print("  - セット（ストレート+ボックス）や、ボックスでの購入を強く推奨します！")
    print("  - 1点集中より、このリストの中から数点選んで幅広く構えるのがコツだよ！✨")
    print("="*60)

if __name__ == "__main__":
    run_box_focused_prediction()





"""
予測履歴をデータベースに保存するユーティリティ（SQLite版）

使い方:
  from numbers4.save_prediction_history import save_ensemble_prediction
  
  # 予測実行後に呼び出す
  save_ensemble_prediction(
      predictions_df=final_predictions_df,
      ensemble_weights=ensemble_weights,
      predictions_by_model=predictions_by_model,
      model_state=model_state
  )
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection


def get_latest_draw_info(conn):
    """最新の抽選情報を取得"""
    cur = conn.cursor()
    cur.execute("""
        SELECT draw_number, draw_date, numbers 
        FROM numbers4_draws 
        ORDER BY draw_date DESC, draw_number DESC 
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        return {
            'draw_number': row[0],
            'draw_date': row[1],
            'numbers': row[2]
        }
    return None


def save_ensemble_prediction(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict[str, float],
    predictions_by_model: Dict[str, List[str]],
    model_state: Optional[Dict] = None,
    target_draw_number: Optional[int] = None,
    notes: Optional[str] = None
) -> int:
    """
    アンサンブル予測の結果をデータベースに保存
    
    Args:
        predictions_df: 予測結果のDataFrame (columns: prediction, score)
        ensemble_weights: アンサンブルの重み設定
        predictions_by_model: モデル別の予測結果
        model_state: モデルの状態（model_state.jsonの内容）
        target_draw_number: 予測対象の抽選回
        notes: メモ・備考
    
    Returns:
        保存したレコードのID
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 最新の抽選情報を取得
        latest_draw = get_latest_draw_info(conn)
        if not target_draw_number and latest_draw:
            target_draw_number = latest_draw['draw_number'] + 1
        
        # モデル情報を取得
        model_updated_at = None
        model_events_count = None
        if model_state:
            model_updated_at = model_state.get('updated_at')
            model_events_count = model_state.get('events')
        
        # 上位予測結果をJSON化（上位20件）
        top_predictions = []
        for idx, row in predictions_df.head(20).iterrows():
            top_predictions.append({
                'rank': int(idx + 1),
                'number': str(row['prediction']),
                'score': float(row['score'])
            })
        
        # モデル別予測結果をJSON化
        model_predictions_json = {}
        for model_name, predictions in predictions_by_model.items():
            model_predictions_json[model_name] = {
                'count': len(predictions),
                'predictions': predictions[:10]  # 各モデルの上位10件のみ保存
            }
        
        # アンサンブル予測レコードを挿入
        created_at = datetime.now(timezone.utc).isoformat()
        cur.execute("""
            INSERT INTO numbers4_ensemble_predictions (
                created_at, target_draw_number, model_updated_at, model_events_count,
                ensemble_weights, predictions_count, top_predictions, model_predictions, notes
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            created_at,
            target_draw_number,
            model_updated_at,
            model_events_count,
            json.dumps(ensemble_weights, ensure_ascii=False),
            len(predictions_df),
            json.dumps(top_predictions, ensure_ascii=False),
            json.dumps(model_predictions_json, ensure_ascii=False),
            notes
        ))
        
        ensemble_prediction_id = cur.lastrowid
        
        # 個別の予測候補を保存（上位50件）
        for idx, row in predictions_df.head(50).iterrows():
            # この番号を予測したモデルを特定
            contributing_models = []
            number = str(row['prediction'])
            for model_name, predictions in predictions_by_model.items():
                if number in predictions:
                    contributing_models.append(model_name)
            
            cur.execute("""
                INSERT INTO numbers4_prediction_candidates (
                    ensemble_prediction_id, rank, number, score, contributing_models, created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?
                )
            """, (
                ensemble_prediction_id,
                int(idx + 1),
                number,
                float(row['score']),
                json.dumps(contributing_models, ensure_ascii=False),
                created_at
            ))
        
        conn.commit()
        
        print(f"\n✅ 予測履歴をデータベースに保存しました")
        print(f"   📝 予測ID: {ensemble_prediction_id}")
        print(f"   🎯 対象抽選回: 第{target_draw_number}回" if target_draw_number else "   🎯 対象抽選回: 未設定")
        print(f"   📊 予測候補数: {len(predictions_df)}件")
        print(f"   💾 保存した候補: {min(50, len(predictions_df))}件")
        
        return ensemble_prediction_id
        
    except Exception as e:
        conn.rollback()
        import traceback
        print(f"\n❌ 予測履歴の保存に失敗しました")
        print(f"   エラー: {e}")
        print(f"   詳細: {traceback.format_exc()}")
        raise
    finally:
        conn.close()


def update_prediction_result(
    ensemble_prediction_id: int,
    actual_draw_number: int,
    actual_numbers: str
):
    """
    予測結果を実際の当選番号で更新
    
    Args:
        ensemble_prediction_id: アンサンブル予測のID
        actual_draw_number: 実際の抽選回
        actual_numbers: 実際の当選番号（4桁）
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 予測結果を取得
        cur.execute("""
            SELECT top_predictions 
            FROM numbers4_ensemble_predictions 
            WHERE id = ?
        """, (ensemble_prediction_id,))
        
        row = cur.fetchone()
        if not row:
            print(f"予測ID {ensemble_prediction_id} が見つかりません。")
            return
        
        top_predictions = json.loads(row[0])
        
        # 的中判定
        hit_status = 'miss'
        hit_count = 0
        is_box = False
        
        # 実際の当選番号のソート（ボックス判定用）
        actual_sorted = sorted(list(actual_numbers))
        
        # 完全一致（ストレート）チェック
        for pred in top_predictions:
            pred_num = pred['number']
            if pred_num == actual_numbers:
                hit_status = 'exact'
                hit_count = 4
                is_box = True
                break
        
        # ボックスチェック（ストレートでない場合）
        if hit_status == 'miss':
            for pred in top_predictions:
                pred_num = pred['number']
                if sorted(list(pred_num)) == actual_sorted:
                    is_box = True
                    break
        
        # 部分一致チェック
        if hit_status == 'miss':
            for pred in top_predictions:
                pred_num = pred['number']
                # 各桁の一致数をカウント
                matches = sum(1 for i in range(4) if pred_num[i] == actual_numbers[i])
                if matches > hit_count:
                    hit_count = matches
            
            # ボックスまたは部分一致の判定
            if is_box:
                hit_status = 'box'
                hit_count = 4
            elif hit_count > 0:
                hit_status = 'partial'
        
        # 結果を更新
        cur.execute("""
            UPDATE numbers4_ensemble_predictions 
            SET actual_draw_number = ?,
                actual_numbers = ?,
                hit_status = ?,
                hit_count = ?
            WHERE id = ?
        """, (
            actual_draw_number,
            actual_numbers,
            hit_status,
            hit_count,
            ensemble_prediction_id
        ))
        
        conn.commit()
        
        print(f"予測結果を更新しました (ID: {ensemble_prediction_id})")
        print(f"   実際の当選番号: {actual_numbers}")
        print(f"   的中状況: {hit_status} ({hit_count}桁一致)")
        
    except Exception as e:
        conn.rollback()
        print(f"予測結果の更新に失敗: {e}")
        raise
    finally:
        conn.close()


def get_prediction_history(limit: int = 10) -> List[Dict]:
    """
    予測履歴を取得
    
    Args:
        limit: 取得件数
    
    Returns:
        予測履歴のリスト
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                id, created_at, target_draw_number, 
                top_predictions, actual_numbers, hit_status, hit_count
            FROM numbers4_ensemble_predictions 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        history = []
        for row in cur.fetchall():
            history.append({
                'id': row[0],
                'created_at': row[1],
                'target_draw_number': row[2],
                'top_predictions': json.loads(row[3]) if row[3] else [],
                'actual_numbers': row[4],
                'hit_status': row[5],
                'hit_count': row[6]
            })
        
        return history
        
    finally:
        conn.close()


if __name__ == '__main__':
    # テスト: 最近の予測履歴を表示
    print("\n" + "="*60)
    print("📊 予測履歴（最新10件）")
    print("="*60)
    
    history = get_prediction_history(10)
    
    if not history:
        print("予測履歴がありません。")
    else:
        for h in history:
            print(f"\nID: {h['id']}")
            print(f"作成日時: {h['created_at']}")
            print(f"対象抽選回: 第{h['target_draw_number']}回" if h['target_draw_number'] else "対象抽選回: 未設定")
            
            if h['top_predictions']:
                print(f"上位3予測: ", end="")
                top3 = h['top_predictions'][:3]
                print(", ".join([f"{p['number']}({p['score']:.1f})" for p in top3]))
            
            if h['actual_numbers']:
                print(f"実際の当選番号: {h['actual_numbers']}")
                print(f"的中状況: {h['hit_status']} ({h['hit_count']}桁一致)")
            else:
                print("結果: 未判明")

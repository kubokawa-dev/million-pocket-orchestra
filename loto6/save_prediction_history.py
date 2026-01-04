"""
ロト6の予測履歴をデータベースに保存するユーティリティ（SQLite版）

使い方:
  from loto6.save_prediction_history import save_ensemble_prediction
  
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
        SELECT draw_number, draw_date, numbers, bonus_number 
        FROM loto6_draws 
        ORDER BY draw_date DESC, draw_number DESC 
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        return {
            'draw_number': row[0],
            'draw_date': row[1],
            'numbers': row[2],
            'bonus_number': row[3]
        }
    return None


def save_ensemble_prediction(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict,
    predictions_by_model: Dict,
    model_state: Optional[Dict] = None,
    notes: Optional[str] = None
):
    """
    アンサンブル予測結果をデータベースに保存
    
    Args:
        predictions_df: 予測結果のDataFrame（number, score列を含む）
        ensemble_weights: アンサンブルの重み設定
        predictions_by_model: モデル別の予測結果
        model_state: モデルの状態情報
        notes: 予測に関する追加メモ
        
    Returns:
        int: 保存された予測のID
    """
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 最新の抽選情報を取得
        latest_draw = get_latest_draw_info(conn)
        target_draw_number = latest_draw['draw_number'] + 1 if latest_draw else None
        
        # アンサンブル予測データを準備
        created_at = datetime.now(timezone.utc).isoformat()
        
        top_predictions_data = []
        for _, row in predictions_df.head(10).iterrows():
            number_val = row.get('number', row.get('prediction', row.get('numbers', '')))
            top_predictions_data.append({
                'number': number_val,
                'score': float(row['score'])
            })
        
        # アンサンブル予測を挿入
        insert_query = """
            INSERT INTO loto6_ensemble_predictions (
                created_at, target_draw_number, model_updated_at, model_events_count,
                ensemble_weights, predictions_count, top_predictions, model_predictions,
                actual_draw_number, actual_numbers, actual_bonus_number,
                hit_status, hit_count, bonus_hit, notes
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """
        
        cur.execute(insert_query, (
            created_at,
            target_draw_number,
            model_state.get('updated_at') if model_state else None,
            model_state.get('events') if model_state else None,
            json.dumps(ensemble_weights),
            len(predictions_df),
            json.dumps(top_predictions_data),
            json.dumps(predictions_by_model),
            None,  # actual_draw_number
            None,  # actual_numbers
            None,  # actual_bonus_number
            None,  # hit_status
            None,  # hit_count
            None,  # bonus_hit
            notes or f'アンサンブル予測（{len(predictions_df)}候補）'
        ))
        
        prediction_id = cur.lastrowid
        
        # 予測候補を挿入
        for rank, (_, row) in enumerate(predictions_df.head(20).iterrows(), 1):
            candidate_query = """
                INSERT INTO loto6_prediction_candidates (
                    ensemble_prediction_id, rank, number, score, contributing_models, created_at
                ) VALUES (?, ?, ?, ?, ?, ?);
            """
            
            # どのモデルがこの番号を予測したかを特定
            number_val = row.get('number', row.get('prediction', row.get('numbers', '')))
            contributing_models = []
            for model_name, model_predictions in predictions_by_model.items():
                if number_val in model_predictions:
                    contributing_models.append(model_name)
            
            cur.execute(candidate_query, (
                prediction_id,
                rank,
                number_val,
                float(row['score']),
                json.dumps(contributing_models),
                created_at
            ))
        
        # 予測ログも保存
        for rank, (_, row) in enumerate(predictions_df.head(10).iterrows(), 1):
            log_query = """
                INSERT INTO loto6_predictions_log (
                    created_at, source, label, number, target_draw_number
                ) VALUES (?, ?, ?, ?, ?);
            """
            
            log_number_val = row.get('number', row.get('prediction', row.get('numbers', '')))
            cur.execute(log_query, (
                created_at,
                'ensemble_prediction',
                f'予測{rank}位',
                log_number_val,
                target_draw_number
            ))
        
        conn.commit()
        print(f"ロト6の予測結果を保存しました。予測ID: {prediction_id}")
        return prediction_id
        
    except Exception as e:
        print(f"予測結果保存エラー: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_prediction_result(prediction_id: int, actual_numbers: str, actual_bonus_number: int):
    """
    予測結果を更新（当選番号が判明した後）
    
    Args:
        prediction_id: 予測ID
        actual_numbers: 実際の当選番号（6桁）
        actual_bonus_number: 実際のボーナス数字
    """
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 予測情報を取得
        cur.execute("""
            SELECT target_draw_number, top_predictions
            FROM loto6_ensemble_predictions
            WHERE id = ?
        """, (prediction_id,))
        
        row = cur.fetchone()
        if not row:
            raise ValueError(f"予測ID {prediction_id} が見つかりません")
        
        target_draw_number, top_predictions_json = row
        top_predictions = json.loads(top_predictions_json)
        
        # 的中状況を判定
        hit_status = 'miss'
        hit_count = 0
        top_match = None
        bonus_hit = False
        
        for pred in top_predictions:
            predicted_number = pred['number']
            # 6桁の完全一致をチェック
            if predicted_number == actual_numbers:
                hit_status = 'exact'
                hit_count = 6
                top_match = predicted_number
                break
            else:
                # 部分一致をチェック
                matches = sum(1 for i in range(min(6, len(predicted_number), len(actual_numbers))) 
                             if i < len(predicted_number) and i < len(actual_numbers) 
                             and predicted_number[i] == actual_numbers[i])
                if matches > hit_count:
                    hit_count = matches
                    top_match = predicted_number
                    hit_status = 'partial' if matches > 0 else 'miss'
        
        # ボーナス数字の的中をチェック
        for pred in top_predictions:
            predicted_number = pred['number']
            if str(actual_bonus_number) in predicted_number:
                bonus_hit = True
                break
        
        # 予測結果を更新
        update_query = """
            UPDATE loto6_ensemble_predictions
            SET actual_draw_number = ?,
                actual_numbers = ?,
                actual_bonus_number = ?,
                hit_status = ?,
                hit_count = ?,
                bonus_hit = ?,
                notes = ?
            WHERE id = ?
        """
        
        notes = f"結果更新: {actual_numbers} (的中: {hit_count}/6桁)"
        if bonus_hit:
            notes += f", ボーナス数字{actual_bonus_number}的中"
        if top_match:
            notes += f", 最良予測: {top_match}"
        
        cur.execute(update_query, (
            target_draw_number,
            actual_numbers,
            actual_bonus_number,
            hit_status,
            hit_count,
            1 if bonus_hit else 0,
            notes,
            prediction_id
        ))
        
        conn.commit()
        print(f"予測結果を更新しました。的中: {hit_count}/6桁, ボーナス: {'的中' if bonus_hit else '外れ'}")
        
    except Exception as e:
        print(f"予測結果更新エラー: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_prediction_history(limit: int = 20):
    """予測履歴を取得"""
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT id, created_at, target_draw_number, predictions_count,
                   hit_status, hit_count, bonus_hit, actual_numbers, actual_bonus_number, notes
            FROM loto6_ensemble_predictions
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        cur.execute(query, (limit,))
        columns = ['id', 'created_at', 'target_draw_number', 'predictions_count',
                   'hit_status', 'hit_count', 'bonus_hit', 'actual_numbers', 'actual_bonus_number', 'notes']
        rows = cur.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        print(f"予測履歴取得エラー: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def save_model_event(
    actual_number: str,
    predictions: List[str],
    hit_exact: bool = False,
    top_match: Optional[str] = None,
    max_position_hits: int = 0,
    notes: Optional[str] = None
):
    """モデル学習イベントを保存"""
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        insert_query = """
            INSERT INTO loto6_model_events (
                event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cur.execute(insert_query, (
            datetime.now(timezone.utc).isoformat(),
            actual_number,
            json.dumps(predictions),
            1 if hit_exact else 0,
            top_match,
            max_position_hits,
            notes
        ))
        
        conn.commit()
        print(f"モデル学習イベントを保存しました: {actual_number}")
        
    except Exception as e:
        print(f"モデルイベント保存エラー: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

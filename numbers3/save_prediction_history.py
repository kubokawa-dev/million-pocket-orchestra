"""
ナンバーズ3の予測履歴をデータベースに保存するユーティリティ

使い方:
  from numbers3.save_prediction_history import save_ensemble_prediction
  
  # 予測実行後に呼び出す
  save_ensemble_prediction(
      predictions_df=final_predictions_df,
      ensemble_weights=ensemble_weights,
      predictions_by_model=predictions_by_model,
      model_state=model_state
  )
"""

import os
import json
import psycopg2
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """データベース接続を取得"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)


def get_latest_draw_info(conn):
    """最新の抽選情報を取得"""
    cur = conn.cursor()
    cur.execute("""
        SELECT draw_number, draw_date, numbers 
        FROM numbers3_draws 
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
    """
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 最新の抽選情報を取得
        latest_draw = get_latest_draw_info(conn)
        target_draw_number = latest_draw['draw_number'] + 1 if latest_draw else None
        
        # アンサンブル予測を保存
        ensemble_data = {
            'created_at': datetime.now(timezone.utc),
            'target_draw_number': target_draw_number,
            'model_updated_at': model_state.get('updated_at') if model_state else None,
            'model_events_count': model_state.get('events') if model_state else None,
            'ensemble_weights': json.dumps(ensemble_weights),
            'predictions_count': len(predictions_df),
            'top_predictions': json.dumps([
                {'number': row['prediction'], 'score': float(row['score'])}
                for _, row in predictions_df.head(10).iterrows()
            ]),
            'model_predictions': json.dumps(predictions_by_model),
            'actual_draw_number': None,
            'actual_numbers': None,
            'hit_status': None,
            'hit_count': None,
            'notes': notes or f'アンサンブル予測（{len(predictions_df)}候補）'
        }
        
        # アンサンブル予測を挿入
        insert_query = """
            INSERT INTO numbers3_ensemble_predictions (
                created_at, target_draw_number, model_updated_at, model_events_count,
                ensemble_weights, predictions_count, top_predictions, model_predictions,
                actual_draw_number, actual_numbers, hit_status, hit_count, notes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
        """
        
        cur.execute(insert_query, (
            ensemble_data['created_at'],
            ensemble_data['target_draw_number'],
            ensemble_data['model_updated_at'],
            ensemble_data['model_events_count'],
            ensemble_data['ensemble_weights'],
            ensemble_data['predictions_count'],
            ensemble_data['top_predictions'],
            ensemble_data['model_predictions'],
            ensemble_data['actual_draw_number'],
            ensemble_data['actual_numbers'],
            ensemble_data['hit_status'],
            ensemble_data['hit_count'],
            ensemble_data['notes']
        ))
        
        prediction_id = cur.fetchone()[0]
        
        # 予測候補を挿入（最強版: 20→150に増加）
        for rank, (_, row) in enumerate(predictions_df.head(150).iterrows(), 1):
            candidate_query = """
                INSERT INTO numbers3_prediction_candidates (
                    ensemble_prediction_id, rank, number, score, contributing_models, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s);
            """
            
            # どのモデルがこの番号を予測したかを特定
            contributing_models = []
            for model_name, model_predictions in predictions_by_model.items():
                if row['prediction'] in model_predictions:
                    contributing_models.append(model_name)
            
            cur.execute(candidate_query, (
                prediction_id,
                rank,
                row['prediction'],
                float(row['score']),
                json.dumps(contributing_models),
                datetime.now(timezone.utc)
            ))
        
        # 予測ログも保存
        for rank, (_, row) in enumerate(predictions_df.head(10).iterrows(), 1):
            log_query = """
                INSERT INTO numbers3_predictions_log (
                    created_at, source, label, number, target_draw_number
                ) VALUES (%s, %s, %s, %s, %s);
            """
            
            cur.execute(log_query, (
                datetime.now(timezone.utc).isoformat(),
                'ensemble_prediction',
                f'予測{rank}位',
                row['prediction'],
                target_draw_number
            ))
        
        conn.commit()
        print(f"ナンバーズ3の予測結果を保存しました。予測ID: {prediction_id}")
        
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


def update_prediction_result(prediction_id: int, actual_numbers: str):
    """
    予測結果を更新（当選番号が判明した後）
    
    Args:
        prediction_id: 予測ID
        actual_numbers: 実際の当選番号
    """
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 予測情報を取得
        cur.execute("""
            SELECT target_draw_number, top_predictions
            FROM numbers3_ensemble_predictions
            WHERE id = %s
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
        
        for pred in top_predictions:
            predicted_number = pred['number']
            # 3桁の完全一致をチェック
            if predicted_number == actual_numbers:
                hit_status = 'exact'
                hit_count = 3
                top_match = predicted_number
                break
            else:
                # 部分一致をチェック
                matches = sum(1 for i in range(3) if predicted_number[i] == actual_numbers[i])
                if matches > hit_count:
                    hit_count = matches
                    top_match = predicted_number
                    hit_status = 'partial' if matches > 0 else 'miss'
        
        # 予測結果を更新
        update_query = """
            UPDATE numbers3_ensemble_predictions
            SET actual_draw_number = %s,
                actual_numbers = %s,
                hit_status = %s,
                hit_count = %s,
                notes = %s
            WHERE id = %s
        """
        
        notes = f"結果更新: {actual_numbers} (的中: {hit_count}/3桁)"
        if top_match:
            notes += f", 最良予測: {top_match}"
        
        cur.execute(update_query, (
            target_draw_number,
            actual_numbers,
            hit_status,
            hit_count,
            notes,
            prediction_id
        ))
        
        conn.commit()
        print(f"予測結果を更新しました。的中: {hit_count}/3桁")
        
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
                   hit_status, hit_count, actual_numbers, notes
            FROM numbers3_ensemble_predictions
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        cur.execute(query, (limit,))
        columns = [desc[0] for desc in cur.description]
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
            INSERT INTO numbers3_model_events (
                event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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



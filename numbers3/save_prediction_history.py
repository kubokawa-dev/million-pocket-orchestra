from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection


PREDICTION_SAVE_LIMIT = 150


def get_latest_draw_info(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT draw_number, draw_date, numbers
        FROM numbers3_draws
        ORDER BY draw_number DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row:
        return {"draw_number": row[0], "draw_date": row[1], "numbers": row[2]}
    return None


def save_ensemble_prediction(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict[str, float],
    predictions_by_model: Dict[str, List[str]],
    model_state: Optional[Dict] = None,
    target_draw_number: Optional[int] = None,
    notes: Optional[str] = None,
) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        latest_draw = get_latest_draw_info(conn)
        if not target_draw_number and latest_draw:
            target_draw_number = latest_draw["draw_number"] + 1

        model_updated_at = model_state.get("updated_at") if model_state else None
        model_events_count = model_state.get("events") if model_state else None

        top_predictions = []
        for idx, row in predictions_df.head(20).iterrows():
            top_predictions.append(
                {
                    "rank": int(idx + 1),
                    "number": str(row["prediction"]).zfill(3),
                    "score": float(row["score"]),
                }
            )

        model_predictions_json = {
            model_name: {"count": len(preds), "predictions": preds[:10]}
            for model_name, preds in predictions_by_model.items()
        }

        created_at = datetime.now(timezone.utc).isoformat()
        cur.execute(
            """
            INSERT INTO numbers3_ensemble_predictions (
                created_at, target_draw_number, model_updated_at, model_events_count,
                ensemble_weights, predictions_count, top_predictions, model_predictions, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                target_draw_number,
                model_updated_at,
                model_events_count,
                json.dumps(ensemble_weights, ensure_ascii=False),
                len(predictions_df),
                json.dumps(top_predictions, ensure_ascii=False),
                json.dumps(model_predictions_json, ensure_ascii=False),
                notes,
            ),
        )
        ensemble_prediction_id = cur.lastrowid

        for idx, row in predictions_df.head(PREDICTION_SAVE_LIMIT).iterrows():
            number = str(row["prediction"]).zfill(3)
            contributors = []
            for model_name, preds in predictions_by_model.items():
                if number in preds:
                    contributors.append(model_name)
            cur.execute(
                """
                INSERT INTO numbers3_prediction_candidates (
                    ensemble_prediction_id, rank, number, score, contributing_models, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ensemble_prediction_id,
                    int(idx + 1),
                    number,
                    float(row["score"]),
                    json.dumps(contributors, ensure_ascii=False),
                    created_at,
                ),
            )

        conn.commit()
        print(f"✅ 予測履歴を保存: ID={ensemble_prediction_id}")
        return ensemble_prediction_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

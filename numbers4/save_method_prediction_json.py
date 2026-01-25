"""
特化手法ごとの予測結果をJSONファイルとして保存するモジュール
"""
import os
import json
from datetime import datetime, timezone
from typing import Dict, List
import pandas as pd

from numbers4.prediction_utils import get_predictions_dir


def get_method_predictions_dir(method: str) -> str:
    """手法別の予測保存ディレクトリを取得"""
    base_dir = get_predictions_dir()
    methods_dir = os.path.join(base_dir, "methods", method)
    os.makedirs(methods_dir, exist_ok=True)
    return methods_dir


def save_method_prediction_to_json(
    predictions_df: pd.DataFrame,
    method: str,
    target_draw_number: int,
    top_n: int = 20,
    metadata: Dict | None = None,
) -> str:
    """
    手法別の予測結果をJSONファイルとして保存

    Args:
        predictions_df: 予測結果のDataFrame
        method: 手法名
        target_draw_number: 対象抽選回号
        top_n: 保存する上位予測数
        metadata: 追加メタデータ

    Returns:
        保存したファイルパス
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%Y%m%d')

    predictions_dir = get_method_predictions_dir(method)
    draw_file = os.path.join(predictions_dir, f'numbers4_{target_draw_number}.json')

    if os.path.exists(draw_file):
        with open(draw_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {
            'draw_number': target_draw_number,
            'target_draw_number': target_draw_number,
            'date': date_str,
            'method': method,
            'predictions': [],
        }

    top_predictions: List[Dict] = []
    for idx, row in predictions_df.head(top_n).iterrows():
        top_predictions.append({
            'rank': int(idx + 1),
            'number': str(row['prediction']),
            'score': round(float(row['score']), 2),
        })

    entry: Dict = {
        'time': now.isoformat(),
        'time_jst': (now.replace(tzinfo=None) + pd.Timedelta(hours=9)).strftime('%H:%M'),
        'method': method,
        'top_predictions': top_predictions,
    }
    if metadata:
        entry['metadata'] = metadata

    daily_data['predictions'].append(entry)
    daily_data['last_updated'] = now.isoformat()
    daily_data['prediction_count'] = len(daily_data['predictions'])

    with open(draw_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 手法別予測をJSONに保存しました: {draw_file}")
    print(f"   🎯 対象回号: 第{target_draw_number}回")
    print(f"   🧭 手法: {method}")
    print(f"   📊 予測回数: {len(daily_data['predictions'])}回")

    return draw_file

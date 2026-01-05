"""
予測結果をJSONファイルとして保存するモジュール

GitHub Actions で毎時実行される予測をリポジトリにコミットして蓄積するため
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd


def get_predictions_dir() -> str:
    """予測結果保存ディレクトリを取得"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    predictions_dir = os.path.join(project_root, 'predictions', 'daily')
    os.makedirs(predictions_dir, exist_ok=True)
    return predictions_dir


def save_prediction_to_json(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict[str, float],
    target_draw_number: int,
    top_n: int = 20
) -> str:
    """
    予測結果をJSONファイルとして保存
    
    Args:
        predictions_df: 予測結果のDataFrame
        ensemble_weights: アンサンブルの重み
        target_draw_number: 対象抽選回号
        top_n: 保存する上位予測数
    
    Returns:
        保存したファイルパス
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M')
    
    # 今日の予測ファイルパス
    predictions_dir = get_predictions_dir()
    daily_file = os.path.join(predictions_dir, f'{date_str}.json')
    
    # 既存のデータを読み込む（あれば）
    if os.path.exists(daily_file):
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {
            'date': date_str,
            'target_draw_number': target_draw_number,
            'predictions': []
        }
    
    # 上位予測を抽出
    top_predictions = []
    for idx, row in predictions_df.head(top_n).iterrows():
        top_predictions.append({
            'rank': int(idx + 1),
            'number': str(row['prediction']),
            'score': round(float(row['score']), 2)
        })
    
    # 新しい予測を追加
    prediction_entry = {
        'time': now.isoformat(),
        'time_jst': (now.replace(tzinfo=None) + pd.Timedelta(hours=9)).strftime('%H:%M'),
        'ensemble_weights': ensemble_weights,
        'top_predictions': top_predictions
    }
    
    daily_data['predictions'].append(prediction_entry)
    daily_data['last_updated'] = now.isoformat()
    daily_data['prediction_count'] = len(daily_data['predictions'])
    
    # ファイルに保存
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 予測結果をJSONに保存しました: {daily_file}")
    print(f"   📊 本日の予測回数: {len(daily_data['predictions'])}回")
    
    return daily_file


def load_daily_predictions(date_str: str = None) -> Optional[Dict]:
    """
    指定日の予測データを読み込む
    
    Args:
        date_str: 日付文字列（YYYYMMDD）。Noneなら今日
    
    Returns:
        予測データ辞書、またはNone
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    predictions_dir = get_predictions_dir()
    daily_file = os.path.join(predictions_dir, f'{date_str}.json')
    
    if not os.path.exists(daily_file):
        return None
    
    with open(daily_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_aggregated_predictions(date_str: str = None) -> Dict:
    """
    1日分の予測を集計して、安定して上位に来る番号を抽出
    
    Args:
        date_str: 日付文字列（YYYYMMDD）
    
    Returns:
        集計結果の辞書
    """
    daily_data = load_daily_predictions(date_str)
    
    if not daily_data or not daily_data.get('predictions'):
        return {'error': '予測データがありません'}
    
    # 番号ごとの出現回数とスコアを集計
    number_stats = {}
    total_predictions = len(daily_data['predictions'])
    
    for pred_entry in daily_data['predictions']:
        for pred in pred_entry['top_predictions']:
            number = pred['number']
            if number not in number_stats:
                number_stats[number] = {
                    'appearances': 0,
                    'total_score': 0.0,
                    'best_rank': 999,
                    'ranks': []
                }
            
            stats = number_stats[number]
            stats['appearances'] += 1
            stats['total_score'] += pred['score']
            stats['best_rank'] = min(stats['best_rank'], pred['rank'])
            stats['ranks'].append(pred['rank'])
    
    # 平均を計算
    for number, stats in number_stats.items():
        stats['avg_score'] = stats['total_score'] / stats['appearances']
        stats['avg_rank'] = sum(stats['ranks']) / len(stats['ranks'])
        stats['appearance_rate'] = stats['appearances'] / total_predictions * 100
    
    # ソート（出現回数 → 平均スコア → 最高順位）
    sorted_numbers = sorted(
        number_stats.items(),
        key=lambda x: (-x[1]['appearances'], -x[1]['avg_score'], x[1]['best_rank'])
    )
    
    return {
        'date': daily_data['date'],
        'target_draw_number': daily_data['target_draw_number'],
        'prediction_count': total_predictions,
        'aggregated': sorted_numbers[:20]
    }


if __name__ == '__main__':
    # テスト用
    result = get_aggregated_predictions()
    print(json.dumps(result, ensure_ascii=False, indent=2))


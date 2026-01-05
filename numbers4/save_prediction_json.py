"""
予測結果をJSONファイルとして保存するモジュール

GitHub Actions で毎時実行される予測をリポジトリにコミットして蓄積するため
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd

# 共通ユーティリティからインポート
from numbers4.prediction_utils import get_predictions_dir


def save_prediction_to_json(
    predictions_df: pd.DataFrame,
    ensemble_weights: Dict[str, float],
    target_draw_number: int,
    top_n: int = 20,
    similar_patterns: Optional[Dict[str, List[Dict]]] = None
) -> str:
    """
    予測結果をJSONファイルとして保存
    
    ファイル名は対象抽選回号ベース (例: numbers4_6891.json)
    
    Args:
        predictions_df: 予測結果のDataFrame
        ensemble_weights: アンサンブルの重み
        target_draw_number: 対象抽選回号
        top_n: 保存する上位予測数
        similar_patterns: 類似パターン辞書 {番号: [{number, description, score}, ...]}
    
    Returns:
        保存したファイルパス
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%Y%m%d')
    
    # 抽選回号ベースのファイルパス (例: numbers4_6891.json)
    predictions_dir = get_predictions_dir()
    draw_file = os.path.join(predictions_dir, f'numbers4_{target_draw_number}.json')
    
    # 既存のデータを読み込む (あれば)
    if os.path.exists(draw_file):
        with open(draw_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {
            'draw_number': target_draw_number,
            'target_draw_number': target_draw_number,  # 後方互換性のため残す
            'date': date_str,  # 最初の予測日
            'predictions': []
        }
    
    # 上位予測を抽出
    top_predictions = []
    for idx, row in predictions_df.head(top_n).iterrows():
        pred_data = {
            'rank': int(idx + 1),
            'number': str(row['prediction']),
            'score': round(float(row['score']), 2)
        }
        
        # 類似パターンがあれば追加
        if similar_patterns and str(row['prediction']) in similar_patterns:
            pred_data['similar_patterns'] = similar_patterns[str(row['prediction'])]
        
        top_predictions.append(pred_data)
    
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
    with open(draw_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 予測結果をJSONに保存しました: {draw_file}")
    print(f"   🎯 対象回号: 第{target_draw_number}回")
    print(f"   📊 予測回数: {len(daily_data['predictions'])}回")
    
    return draw_file


# 後方互換性のため、共通モジュールの関数を再エクスポート
from numbers4.prediction_utils import load_predictions_by_draw, load_daily_predictions


def get_aggregated_predictions(draw_number: int = None, date_str: str = None) -> Dict:
    """
    予測を集計して、安定して上位に来る番号を抽出
    
    Args:
        draw_number: 抽選回号（優先）
        date_str: 日付文字列（YYYYMMDD）- 後方互換性用
    
    Returns:
        集計結果の辞書
    """
    if draw_number:
        daily_data = load_predictions_by_draw(draw_number)
    else:
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



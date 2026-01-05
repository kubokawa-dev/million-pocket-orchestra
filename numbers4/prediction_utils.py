"""
予測データの共通ユーティリティ関数

複数のモジュール間で共有される予測データのロード/取得機能を提供
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Optional


def get_predictions_dir() -> str:
    """予測結果保存ディレクトリを取得"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    predictions_dir = os.path.join(project_root, 'predictions', 'daily')
    os.makedirs(predictions_dir, exist_ok=True)
    return predictions_dir


def get_reports_dir() -> str:
    """分析レポート保存ディレクトリを取得"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def load_predictions_by_draw(draw_number: int) -> Optional[Dict]:
    """
    指定回号の予測データを読み込む
    
    Args:
        draw_number: 抽選回号
    
    Returns:
        予測データ辞書、またはNone
    """
    predictions_dir = get_predictions_dir()
    draw_file = os.path.join(predictions_dir, f'{draw_number}.json')
    
    if not os.path.exists(draw_file):
        print(f"❌ 予測ファイルが見つかりません: {draw_file}")
        return None
    
    with open(draw_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_daily_predictions(date_str: Optional[str] = None) -> Optional[Dict]:
    """
    指定日の予測データを読み込む (後方互換性用)
    
    Args:
        date_str: 日付文字列 (YYYYMMDD)。Noneなら今日
    
    Returns:
        予測データ辞書、またはNone
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    predictions_dir = get_predictions_dir()
    
    # まず日付ベースのファイルを探す (旧形式)
    daily_file = os.path.join(predictions_dir, f'{date_str}.json')
    if os.path.exists(daily_file):
        with open(daily_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 日付ベースがなければ、回号ベースのファイルから探す (数値順でソート)
    json_files = [
        fn for fn in os.listdir(predictions_dir)
        if fn.endswith('.json') and fn[:-5].isdigit()
    ]
    json_files.sort(key=lambda fn: int(fn[:-5]), reverse=True)
    
    for filename in json_files:
        filepath = os.path.join(predictions_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('date') == date_str:
                return data
    
    print(f"❌ 予測ファイルが見つかりません: {date_str}")
    return None


def get_latest_prediction() -> Optional[Dict]:
    """
    最新の予測データを読み込む
    
    Returns:
        最新の予測データ辞書、またはNone
    """
    predictions_dir = get_predictions_dir()
    
    # 回号ベースのファイルを数値順でソート
    json_files = [
        fn for fn in os.listdir(predictions_dir)
        if fn.endswith('.json') and fn[:-5].isdigit()
    ]
    
    if not json_files:
        return None
    
    json_files.sort(key=lambda fn: int(fn[:-5]), reverse=True)
    
    latest_file = os.path.join(predictions_dir, json_files[0])
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


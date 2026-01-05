"""
予測結果と実際の当選番号を比較・分析するスクリプト

平日23:00に実行し、その日の予測精度を分析してレポートを生成
また、モデルの重みを自動調整して改善を図る

使い方:
  python numbers4/analyze_prediction_result.py
  python numbers4/analyze_prediction_result.py --date 20260105
  python numbers4/analyze_prediction_result.py --output reports/analysis_20260105.md
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection


def get_predictions_dir() -> str:
    """予測結果保存ディレクトリを取得"""
    return os.path.join(project_root, 'predictions', 'daily')


def get_reports_dir() -> str:
    """分析レポート保存ディレクトリを取得"""
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def load_daily_predictions(date_str: str) -> Optional[Dict]:
    """指定日の予測データを読み込む"""
    predictions_dir = get_predictions_dir()
    daily_file = os.path.join(predictions_dir, f'{date_str}.json')
    
    if not os.path.exists(daily_file):
        print(f"❌ 予測ファイルが見つかりません: {daily_file}")
        return None
    
    with open(daily_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_actual_result(target_draw_number: int) -> Optional[Dict]:
    """当選番号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            WHERE draw_number = ?
        """, (target_draw_number,))
        row = cur.fetchone()
        
        if row:
            return {
                'draw_number': row[0],
                'draw_date': row[1],
                'numbers': row[2]
            }
        return None
    finally:
        conn.close()


def get_latest_draw() -> Optional[Dict]:
    """最新の当選番号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            ORDER BY draw_number DESC
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
    finally:
        conn.close()


def calculate_match_type(actual: str, predicted: str) -> Dict:
    """当選番号と予測番号の一致タイプを判定"""
    # 完全一致
    exact_match = actual == predicted
    
    # ボックス一致（順序無視で数字が同じ）
    box_match = sorted(actual) == sorted(predicted)
    
    # 桁ごとの一致
    position_hits = sum(1 for a, p in zip(actual, predicted) if a == p)
    
    # 数字の一致（位置無視）
    actual_counter = Counter(actual)
    predicted_counter = Counter(predicted)
    digit_hits = sum((actual_counter & predicted_counter).values())
    
    return {
        'exact_match': exact_match,
        'box_match': box_match,
        'position_hits': position_hits,
        'digit_hits': digit_hits
    }


def analyze_predictions(daily_data: Dict, actual_result: Dict) -> Dict:
    """予測結果を分析"""
    predictions = daily_data.get('predictions', [])
    actual_numbers = actual_result['numbers']
    
    analysis = {
        'target_draw': daily_data.get('target_draw_number'),
        'actual_numbers': actual_numbers,
        'prediction_count': len(predictions),
        'best_match': None,
        'best_match_rank': None,
        'exact_hit': False,
        'box_hit': False,
        'position_hits_max': 0,
        'digit_hits_max': 0,
        'actual_in_predictions': False,
        'actual_rank': None,
        'model_performance': {},
        'digit_analysis': {},
        'improvement_suggestions': []
    }
    
    # 各予測の分析
    all_predicted_numbers = {}  # number -> best_rank
    
    for pred_entry in predictions:
        for pred in pred_entry.get('top_predictions', []):
            number = pred['number']
            rank = pred['rank']
            
            if number not in all_predicted_numbers or all_predicted_numbers[number] > rank:
                all_predicted_numbers[number] = rank
    
    # 当選番号が予測に含まれているか
    if actual_numbers in all_predicted_numbers:
        analysis['actual_in_predictions'] = True
        analysis['actual_rank'] = all_predicted_numbers[actual_numbers]
        analysis['exact_hit'] = True
    
    # 各予測番号との一致度を計算
    best_position_hits = 0
    best_digit_hits = 0
    best_match_number = None
    best_match_rank = 999
    
    for number, rank in all_predicted_numbers.items():
        match_info = calculate_match_type(actual_numbers, number)
        
        if match_info['exact_match']:
            analysis['exact_hit'] = True
            best_match_number = number
            best_match_rank = rank
        
        if match_info['box_match']:
            analysis['box_hit'] = True
        
        if match_info['position_hits'] > best_position_hits:
            best_position_hits = match_info['position_hits']
            if not analysis['exact_hit']:
                best_match_number = number
                best_match_rank = rank
        
        if match_info['digit_hits'] > best_digit_hits:
            best_digit_hits = match_info['digit_hits']
    
    analysis['position_hits_max'] = best_position_hits
    analysis['digit_hits_max'] = best_digit_hits
    analysis['best_match'] = best_match_number
    analysis['best_match_rank'] = best_match_rank if best_match_number else None
    
    # 桁別の分析
    for i, actual_digit in enumerate(actual_numbers):
        digit_predictions = Counter()
        for number in all_predicted_numbers.keys():
            if i < len(number):
                digit_predictions[number[i]] += 1
        
        top3 = digit_predictions.most_common(3)
        hit = actual_digit in [d for d, _ in top3]
        
        analysis['digit_analysis'][f'd{i+1}'] = {
            'actual': actual_digit,
            'predicted_top3': top3,
            'hit_in_top3': hit
        }
    
    # 改善提案の生成
    analysis['improvement_suggestions'] = generate_improvement_suggestions(analysis)
    
    return analysis


def generate_improvement_suggestions(analysis: Dict) -> List[str]:
    """分析結果から改善提案を生成"""
    suggestions = []
    
    # 完全一致の場合
    if analysis['exact_hit']:
        suggestions.append("🎉 完全一致！今日のモデルは最高のパフォーマンスでした！")
        return suggestions
    
    # 桁別の分析に基づく提案
    digit_analysis = analysis.get('digit_analysis', {})
    weak_digits = []
    for digit_key, info in digit_analysis.items():
        if not info.get('hit_in_top3'):
            weak_digits.append(digit_key)
    
    if weak_digits:
        suggestions.append(f"⚠️ {', '.join(weak_digits)} の予測精度が低い。該当桁のモデル重みを調整検討")
    
    # ポジション一致数に基づく提案
    position_hits = analysis.get('position_hits_max', 0)
    if position_hits == 0:
        suggestions.append("❌ 完全にハズレ。モデルの多様性を増やすことを検討")
    elif position_hits == 1:
        suggestions.append("🔍 1桁のみ一致。特定パターンへの過学習の可能性を確認")
    elif position_hits == 2:
        suggestions.append("📈 2桁一致。あと一歩！類似パターンの分析を強化")
    elif position_hits == 3:
        suggestions.append("🔥 3桁一致！惜しい！微調整で改善の余地あり")
    
    # 当選番号の特徴分析
    actual = analysis.get('actual_numbers', '')
    if len(set(actual)) == 1:
        suggestions.append("💡 ゾロ目番号。ゾロ目予測モデルの重みを検討")
    elif len(set(actual)) == 2:
        suggestions.append("💡 ダブル・ダブル番号。ペア番号予測の強化を検討")
    
    return suggestions


def calculate_weight_adjustments(analysis: Dict, current_weights: Dict) -> Dict:
    """分析結果に基づいてモデル重みの調整を計算"""
    adjustments = {}
    
    # 基本的な調整ロジック
    position_hits = analysis.get('position_hits_max', 0)
    
    # 成績が良い場合は現状維持
    if position_hits >= 3 or analysis.get('exact_hit'):
        return {}
    
    # 成績が悪い場合は探索的モデルの重みを増やす
    if position_hits <= 1:
        adjustments['exploratory'] = 1.0  # 増加
        adjustments['extreme_patterns'] = 0.5  # 増加
        adjustments['digit_repetition'] = -1.0  # 減少（過学習の可能性）
    
    return adjustments


def update_model_weights(adjustments: Dict) -> Dict:
    """モデル重みを更新"""
    weights_path = os.path.join(project_root, 'numbers4', 'model_weights.json')
    
    # デフォルトの重み
    default_weights = {
        'digit_repetition': 30.0,
        'digit_continuation': 25.0,
        'realistic_frequency': 20.0,
        'large_change': 15.0,
        'advanced_heuristics': 10.0,
        'exploratory': 8.0,
        'extreme_patterns': 3.0,
        'basic_stats': 2.0,
        'ml_model_new': 1.0,
        'lightgbm': 30.0
    }
    
    # 現在の重みを読み込む（なければデフォルト）
    if os.path.exists(weights_path):
        with open(weights_path, 'r') as f:
            data = json.load(f)
        # 既存のフォーマットに対応（weightsキーがある場合）
        if 'weights' in data:
            weights = data['weights']
        else:
            weights = data
    else:
        weights = default_weights.copy()
    
    # デフォルトにない新しいモデルを追加
    for key, value in default_weights.items():
        if key not in weights:
            weights[key] = value
    
    # 調整を適用
    updated = False
    for model, delta in adjustments.items():
        if model in weights:
            old_value = weights[model]
            new_value = max(1.0, min(50.0, old_value + delta))  # 1.0〜50.0の範囲に制限
            if new_value != old_value:
                weights[model] = new_value
                updated = True
    
    # 更新があれば保存（新しいフォーマットで）
    if updated:
        save_data = {
            'weights': weights,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'adjustments_history': adjustments
        }
        with open(weights_path, 'w') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    return weights


def generate_report_markdown(analysis: Dict, weight_adjustments: Dict) -> str:
    """分析レポートをMarkdown形式で生成"""
    md = []
    
    # ヘッダー
    md.append(f"# 📊 Numbers4 第{analysis['target_draw']}回 結果分析レポート")
    md.append("")
    md.append(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md.append("")
    
    # 結果サマリー
    md.append("## 🎯 結果サマリー")
    md.append("")
    md.append("| 項目 | 内容 |")
    md.append("|:---|:---|")
    md.append(f"| 対象回号 | 第{analysis['target_draw']}回 |")
    md.append(f"| 当選番号 | `{analysis['actual_numbers']}` |")
    md.append(f"| 予測回数 | {analysis['prediction_count']}回 |")
    
    # 的中状況
    if analysis['exact_hit']:
        status = "🎉 完全一致！"
    elif analysis['box_hit']:
        status = "📦 ボックス一致"
    elif analysis['position_hits_max'] >= 3:
        status = f"🔥 {analysis['position_hits_max']}桁一致"
    elif analysis['position_hits_max'] >= 2:
        status = f"📈 {analysis['position_hits_max']}桁一致"
    elif analysis['position_hits_max'] == 1:
        status = f"🔍 {analysis['position_hits_max']}桁一致"
    else:
        status = "❌ ハズレ"
    
    md.append(f"| 的中状況 | {status} |")
    md.append("")
    
    # 最も近い予測
    if analysis['best_match']:
        md.append("## 🎲 最も近い予測")
        md.append("")
        md.append(f"- **番号**: `{analysis['best_match']}`")
        md.append(f"- **予測順位**: {analysis['best_match_rank']}位")
        md.append(f"- **位置一致数**: {analysis['position_hits_max']}桁")
        md.append(f"- **数字一致数**: {analysis['digit_hits_max']}個")
        md.append("")
    
    # 桁別分析
    md.append("## 🔢 桁別分析")
    md.append("")
    md.append("| 桁 | 当選 | 予測TOP3 | 的中 |")
    md.append("|:---:|:---:|:---|:---:|")
    
    for i in range(4):
        digit_key = f'd{i+1}'
        if digit_key in analysis.get('digit_analysis', {}):
            info = analysis['digit_analysis'][digit_key]
            actual = info['actual']
            top3 = ', '.join([f"{d}({c}回)" for d, c in info['predicted_top3']])
            hit = "✅" if info['hit_in_top3'] else "❌"
            md.append(f"| {i+1}桁目 | `{actual}` | {top3} | {hit} |")
    
    md.append("")
    
    # 良かった点
    md.append("## 💡 分析・改善提案")
    md.append("")
    
    for suggestion in analysis.get('improvement_suggestions', []):
        md.append(f"- {suggestion}")
    
    md.append("")
    
    # 重み調整
    if weight_adjustments:
        md.append("## 🔧 自動重み調整")
        md.append("")
        md.append("| モデル | 調整 |")
        md.append("|:---|:---|")
        for model, delta in weight_adjustments.items():
            sign = "+" if delta > 0 else ""
            md.append(f"| {model} | {sign}{delta:.1f} |")
        md.append("")
    else:
        md.append("## 🔧 自動重み調整")
        md.append("")
        md.append("*今回は調整なし*")
        md.append("")
    
    # フッター
    md.append("---")
    md.append("")
    md.append("*Powered by Million Pocket 🎰*")
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description='予測結果と当選番号を比較・分析'
    )
    parser.add_argument(
        '--date', '-d', type=str,
        help='対象日（YYYYMMDD形式、未指定時は今日）'
    )
    parser.add_argument(
        '--output', '-o', type=str,
        help='出力ファイルパス（未指定時は自動生成）'
    )
    parser.add_argument(
        '--no-update', action='store_true',
        help='重み更新をスキップ'
    )
    
    args = parser.parse_args()
    
    # 日付を決定
    if args.date:
        date_str = args.date
    else:
        # 今日の日付（UTC）
        date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    print(f"📊 {date_str} の予測結果を分析中...")
    
    # 予測データを読み込み
    daily_data = load_daily_predictions(date_str)
    if not daily_data:
        print("❌ 予測データが見つかりません")
        sys.exit(1)
    
    target_draw = daily_data.get('target_draw_number')
    print(f"   🎯 対象抽選回: 第{target_draw}回")
    print(f"   📝 予測回数: {len(daily_data.get('predictions', []))}回")
    
    # 当選番号を取得
    actual_result = get_actual_result(target_draw)
    if not actual_result:
        # 最新の抽選結果を取得してみる
        latest = get_latest_draw()
        if latest and latest['draw_number'] == target_draw:
            actual_result = latest
        else:
            print(f"⚠️ 第{target_draw}回の当選番号がまだDBにありません")
            print(f"   最新の抽選回: 第{latest['draw_number'] if latest else '???'}回")
            print("   先にスクレイピングを実行してください")
            sys.exit(1)
    
    print(f"   🎰 当選番号: {actual_result['numbers']}")
    
    # 分析実行
    analysis = analyze_predictions(daily_data, actual_result)
    
    # 重み調整を計算
    weight_adjustments = {}
    if not args.no_update:
        weight_adjustments = calculate_weight_adjustments(analysis, {})
        if weight_adjustments:
            print("   🔧 重み調整を適用中...")
            update_model_weights(weight_adjustments)
    
    # レポート生成
    report = generate_report_markdown(analysis, weight_adjustments)
    
    # 出力
    if args.output:
        output_path = args.output
    else:
        reports_dir = get_reports_dir()
        output_path = os.path.join(reports_dir, f'analysis_{date_str}.md')
    
    # ディレクトリを作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"   ✅ レポートを保存しました: {output_path}")
    
    # 結果サマリーを表示
    print("")
    print("=" * 50)
    if analysis['exact_hit']:
        print("🎉🎉🎉 完全一致！おめでとう！ 🎉🎉🎉")
    elif analysis['box_hit']:
        print("📦 ボックス一致！惜しい！")
    elif analysis['position_hits_max'] >= 3:
        print(f"🔥 {analysis['position_hits_max']}桁一致！あと一歩！")
    else:
        print(f"📊 {analysis['position_hits_max']}桁一致。次回に期待！")
    print("=" * 50)


if __name__ == '__main__':
    main()


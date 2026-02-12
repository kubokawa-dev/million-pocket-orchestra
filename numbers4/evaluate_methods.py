"""
手法別予測の精度評価と重み更新スクリプト

各予測手法の精度を評価し、良い予測をした手法の重みを上げ、
悪い予測をした手法の重みを下げることで、翌日の予測精度を改善する

使い方:
  python numbers4/evaluate_methods.py --draw 6918
  python numbers4/evaluate_methods.py --draw 6918 --verbose
"""

import os
import sys
import json
import argparse
import glob
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection

# 定数
METHODS_DIR = os.path.join(project_root, 'predictions', 'daily', 'methods')
WEIGHTS_FILE = os.path.join(project_root, 'numbers4', 'method_weights.json')

# 評価対象の手法一覧
ALL_METHODS = [
    'box_model',
    'ml_neighborhood', 
    'even_odd_pattern',
    'low_sum_specialist',
    'sequential_pattern',
    'cold_revival',
    'hot_pair',
    'box_pattern',
    'digit_freq_box',
    'global_frequency',
    'lightgbm',
    'state_chain',
]


def get_default_method_weights() -> Dict[str, float]:
    """デフォルトの手法別重み"""
    return {
        'box_model': 15.0,
        'ml_neighborhood': 12.0,
        'even_odd_pattern': 8.0,
        'low_sum_specialist': 6.0,
        'sequential_pattern': 10.0,
        'cold_revival': 5.0,
        'hot_pair': 8.0,
        'box_pattern': 10.0,
        'digit_freq_box': 7.0,
        'global_frequency': 9.0,
        'lightgbm': 20.0,
        'state_chain': 8.0,
    }


def load_method_weights() -> Dict[str, float]:
    """保存された手法別重みを読み込む"""
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('weights', get_default_method_weights())
    return get_default_method_weights()


def save_method_weights(weights: Dict[str, float], metadata: dict = None):
    """手法別重みを保存"""
    data = {
        'weights': weights,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'metadata': metadata or {}
    }
    
    with open(WEIGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_actual_result(draw_number: int) -> Optional[str]:
    """当選番号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT numbers FROM numbers4_draws 
            WHERE draw_number = ?
        """, (draw_number,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def load_method_predictions(draw_number: int, method: str) -> List[str]:
    """指定手法の予測を読み込む"""
    predictions = []
    
    method_file = os.path.join(METHODS_DIR, method, f'numbers4_{draw_number}.json')
    
    if not os.path.exists(method_file):
        return predictions
    
    try:
        with open(method_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 全予測エントリから番号を収集（重複排除、順位順）
        seen = set()
        for pred_entry in data.get('predictions', []):
            for pred in pred_entry.get('top_predictions', []):
                number = pred.get('number', '')
                if number and number not in seen:
                    predictions.append(number)
                    seen.add(number)
        
    except Exception as e:
        print(f"⚠️ Error loading {method_file}: {e}")
    
    return predictions


def is_box_match(pred: str, actual: str) -> bool:
    """ボックス一致（順不同で数字が全て一致）をチェック"""
    return sorted(list(pred)) == sorted(list(actual))


def count_digit_matches(pred: str, actual: str) -> int:
    """何桁の数字が一致しているか（順不同）をカウント"""
    from collections import Counter
    pred_counter = Counter(pred)
    actual_counter = Counter(actual)
    return sum((actual_counter & pred_counter).values())


def count_position_matches(pred: str, actual: str) -> int:
    """位置一致数をカウント"""
    return sum(1 for a, p in zip(actual, pred) if a == p)


def evaluate_method(predictions: List[str], actual: str, top_k: int = 100) -> Dict:
    """
    手法の予測精度を評価
    
    Returns:
        {
            'straight_rank': 完全一致の順位（なければNone）,
            'box_rank': ボックス一致の順位（なければNone）,
            'best_position_hits': 最大位置一致数,
            'best_digit_hits': 最大数字一致数,
            'score': 総合スコア（0-100）
        }
    """
    result = {
        'straight_rank': None,
        'box_rank': None,
        'best_position_hits': 0,
        'best_digit_hits': 0,
        'score': 0.0
    }
    
    if not predictions:
        return result
    
    for i, pred in enumerate(predictions[:top_k]):
        rank = i + 1
        
        # ストレート一致
        if pred == actual and result['straight_rank'] is None:
            result['straight_rank'] = rank
        
        # ボックス一致
        if is_box_match(pred, actual) and result['box_rank'] is None:
            result['box_rank'] = rank
        
        # 位置一致数
        pos_hits = count_position_matches(pred, actual)
        if pos_hits > result['best_position_hits']:
            result['best_position_hits'] = pos_hits
        
        # 数字一致数
        digit_hits = count_digit_matches(pred, actual)
        if digit_hits > result['best_digit_hits']:
            result['best_digit_hits'] = digit_hits
    
    # スコア計算
    score = 0.0
    
    if result['straight_rank']:
        # ストレート一致: 高スコア（順位が高いほど良い）
        score = 100.0 * (top_k - result['straight_rank'] + 1) / top_k
    elif result['box_rank']:
        # ボックス一致: 70%のスコア
        score = 70.0 * (top_k - result['box_rank'] + 1) / top_k
    elif result['best_position_hits'] >= 3:
        # 3桁位置一致: 40%のスコア
        score = 40.0
    elif result['best_digit_hits'] >= 3:
        # 3桁数字一致: 30%のスコア
        score = 30.0
    elif result['best_position_hits'] >= 2:
        # 2桁位置一致: 15%のスコア
        score = 15.0
    elif result['best_digit_hits'] >= 2:
        # 2桁数字一致: 10%のスコア
        score = 10.0
    
    result['score'] = score
    return result


def update_method_weights(
    current_weights: Dict[str, float],
    evaluations: Dict[str, Dict],
    learning_rate: float = 0.08
) -> Dict[str, float]:
    """
    評価結果に基づいて手法別重みを更新
    
    良い予測をした手法の重みを上げ、悪い予測をした手法の重みを下げる
    """
    new_weights = current_weights.copy()
    
    # 平均スコアを計算
    scores = [e['score'] for e in evaluations.values() if e['score'] > 0]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    for method, evaluation in evaluations.items():
        if method not in new_weights:
            new_weights[method] = 10.0  # デフォルト値
        
        score = evaluation['score']
        
        # スコアに基づいて重みを調整
        if score > avg_score:
            # 平均以上: 重みを増加
            delta = learning_rate * (score / 100.0) * 2.0
            new_weights[method] = min(50.0, new_weights[method] + delta)
        elif score > 0:
            # 平均以下だが何かしら当たった: 微増
            delta = learning_rate * (score / 100.0) * 0.5
            new_weights[method] = min(50.0, new_weights[method] + delta)
        else:
            # 全く当たらなかった: ペナルティ
            penalty = learning_rate * 0.5
            new_weights[method] = max(1.0, new_weights[method] - penalty)
    
    # 正規化（合計を元の合計に近づける）
    total_old = sum(current_weights.values())
    total_new = sum(new_weights.values())
    if total_new > 0:
        scale = total_old / total_new
        new_weights = {k: v * scale for k, v in new_weights.items()}
    
    return new_weights


def main():
    parser = argparse.ArgumentParser(
        description='手法別予測の精度評価と重み更新'
    )
    parser.add_argument(
        '--draw', type=int, required=True,
        help='対象抽選回号'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='詳細を表示'
    )
    parser.add_argument(
        '--no-update', action='store_true',
        help='重み更新をスキップ'
    )
    parser.add_argument(
        '--top-k', type=int, default=100,
        help='評価対象のTop-K（デフォルト: 100）'
    )
    
    args = parser.parse_args()
    
    print(f"📊 手法別予測の精度評価: 第{args.draw}回")
    print("=" * 60)
    
    # 当選番号を取得
    actual = get_actual_result(args.draw)
    if not actual:
        print(f"❌ 第{args.draw}回の当選番号が見つかりません")
        sys.exit(1)
    
    print(f"🎰 当選番号: {actual}")
    print()
    
    # 現在の重みを読み込み
    current_weights = load_method_weights()
    
    # 各手法を評価
    evaluations = {}
    
    for method in ALL_METHODS:
        predictions = load_method_predictions(args.draw, method)
        
        if not predictions:
            if args.verbose:
                print(f"  {method:25s}: ⚠️ 予測データなし")
            continue
        
        evaluation = evaluate_method(predictions, actual, args.top_k)
        evaluations[method] = evaluation
        
        # 結果を表示
        if evaluation['straight_rank']:
            status = f"🎯 {evaluation['straight_rank']:3d}位 (ストレート!)"
        elif evaluation['box_rank']:
            status = f"📦 {evaluation['box_rank']:3d}位 (ボックス!)"
        elif evaluation['best_position_hits'] >= 3:
            status = f"🔥 {evaluation['best_position_hits']}桁位置一致"
        elif evaluation['best_digit_hits'] >= 3:
            status = f"🎲 {evaluation['best_digit_hits']}桁数字一致"
        elif evaluation['best_position_hits'] >= 2:
            status = f"📈 {evaluation['best_position_hits']}桁位置一致"
        else:
            status = f"❌ 予測外"
        
        print(f"  {method:25s}: {status:30s} (スコア: {evaluation['score']:.1f})")
    
    print()
    
    if not evaluations:
        print("⚠️ 評価可能な手法がありません")
        sys.exit(0)
    
    # 重みを更新
    if not args.no_update:
        print("🔧 重みを更新中...")
        new_weights = update_method_weights(current_weights, evaluations)
        
        if args.verbose:
            print("\n【重みの変化】")
            for method in sorted(current_weights.keys()):
                old_w = current_weights.get(method, 10.0)
                new_w = new_weights.get(method, 10.0)
                change = new_w - old_w
                sign = "+" if change >= 0 else ""
                print(f"  {method:25s}: {old_w:6.2f} → {new_w:6.2f} ({sign}{change:.2f})")
        
        # 保存
        metadata = {
            'draw_number': args.draw,
            'actual_number': actual,
            'evaluations': evaluations
        }
        save_method_weights(new_weights, metadata)
        print("\n✅ 手法別重みを更新・保存しました")
    
    print("=" * 60)
    
    # サマリー
    best_method = max(evaluations.items(), key=lambda x: x[1]['score'])
    print(f"🏆 最優秀手法: {best_method[0]} (スコア: {best_method[1]['score']:.1f})")
    
    # ストレート/ボックス一致があれば特別表示
    for method, eval_result in evaluations.items():
        if eval_result['straight_rank']:
            print(f"🎉 {method} がストレート一致！（{eval_result['straight_rank']}位）")
        elif eval_result['box_rank']:
            print(f"📦 {method} がボックス一致！（{eval_result['box_rank']}位）")


if __name__ == '__main__':
    main()

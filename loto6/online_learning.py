"""
ロト6用オンライン学習：新しい当選番号が出たら、モデルの重みを自動調整

仕組み：
1. 各モデルの予測結果を評価（正解が何位にあったか、何個一致したか）
2. 良い予測をしたモデルの重みを上げ、悪い予測をしたモデルの重みを下げる
3. 調整後の重みを保存し、次回の予測に使用
"""

import json
import os
from typing import Dict, List
from datetime import datetime


WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), 'model_weights.json')


def load_model_weights() -> Dict[str, float]:
    """保存された重みを読み込む"""
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('weights', get_default_weights())
    return get_default_weights()


def get_default_weights() -> Dict[str, float]:
    """デフォルトの重み"""
    return {
        'ultra_stats': 10.0,
        'hot_cold_mix': 8.0,
        'never_appeared': 6.0,
        'pair_affinity': 3.0,
        'sum_optimization': 2.5,
        'deep_learning': 2.0,
        'zone_balance': 1.5,
    }


def save_model_weights(weights: Dict[str, float], metadata: dict = None):
    """重みを保存"""
    data = {
        'weights': weights,
        'updated_at': datetime.now().isoformat(),
        'metadata': metadata or {}
    }
    
    with open(WEIGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_weights_online(
    current_weights: Dict[str, float],
    predictions_by_model: Dict[str, List[List[int]]],
    actual_numbers: List[int],
    learning_rate: float = 0.05,
    top_k: int = 50
) -> Dict[str, float]:
    """
    オンライン学習で重みを更新
    
    Args:
        current_weights: 現在の重み
        predictions_by_model: 各モデルの予測リスト（各要素は6個の数字のリスト）
        actual_numbers: 実際の当選番号（6個の数字のリスト）
        learning_rate: 学習率（0.0-1.0、デフォルト: 0.05）
        top_k: 評価対象のTop-K（デフォルト: 50）
    
    Returns:
        更新後の重み
    """
    new_weights = current_weights.copy()
    actual_set = set(actual_numbers)
    
    for model_name, predictions in predictions_by_model.items():
        if model_name not in new_weights:
            continue
        
        # 各予測と正解の一致数を計算
        match_counts = []
        for pred in predictions[:top_k]:
            pred_set = set(pred)
            match_count = len(actual_set & pred_set)
            match_counts.append(match_count)
        
        # 完全一致（6個一致）があるか
        if 6 in match_counts:
            rank = match_counts.index(6) + 1
            # 完全一致の順位が高いほど報酬が大きい
            reward = (top_k - rank + 1) / top_k
            new_weights[model_name] += learning_rate * reward * 2.0  # 完全一致は2倍の報酬
        else:
            # 完全一致がない場合、最高一致数で評価
            best_match = max(match_counts) if match_counts else 0
            if best_match >= 4:
                # 4個以上一致なら報酬
                reward = (best_match - 3) / 3.0  # 4個=0.33, 5個=0.67
                new_weights[model_name] += learning_rate * reward
            else:
                # 3個以下ならペナルティ
                penalty = learning_rate * 0.5
                new_weights[model_name] = max(0.1, new_weights[model_name] - penalty)
    
    # 正規化（合計を元の合計に保つ）
    total_old = sum(current_weights.values())
    total_new = sum(new_weights.values())
    if total_new > 0:
        scale = total_old / total_new
        new_weights = {k: v * scale for k, v in new_weights.items()}
    
    return new_weights


def evaluate_and_update(
    predictions_by_model: Dict[str, List[List[int]]],
    actual_numbers: List[int],
    verbose: bool = True
) -> Dict[str, float]:
    """
    予測を評価し、重みを更新して保存
    
    Args:
        predictions_by_model: 各モデルの予測リスト
        actual_numbers: 実際の当選番号
        verbose: 詳細を表示するか
    
    Returns:
        更新後の重み
    """
    # 現在の重みを読み込み
    current_weights = load_model_weights()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"オンライン学習：重みを更新中...")
        print(f"{'='*60}")
        print(f"正解: {sorted(actual_numbers)}")
    
    # 各モデルの一致数を評価
    actual_set = set(actual_numbers)
    model_results = {}
    
    for model_name, predictions in predictions_by_model.items():
        match_counts = []
        for pred in predictions:
            pred_set = set(pred)
            match_count = len(actual_set & pred_set)
            match_counts.append(match_count)
        
        best_match = max(match_counts) if match_counts else 0
        if 6 in match_counts:
            rank = match_counts.index(6) + 1
            model_results[model_name] = {'rank': rank, 'best_match': 6}
        else:
            model_results[model_name] = {'rank': None, 'best_match': best_match}
    
    if verbose:
        print(f"\n【各モデルの予測結果】")
        for model_name, result in sorted(model_results.items(), key=lambda x: (x[1]['rank'] is None, x[1]['rank'] or 999, -x[1]['best_match'])):
            if result['rank']:
                print(f"  {model_name:30s}: 完全一致 {result['rank']:3d}位")
            else:
                print(f"  {model_name:30s}: 最高{result['best_match']}個一致")
    
    # 重みを更新
    new_weights = update_weights_online(current_weights, predictions_by_model, actual_numbers)
    
    if verbose:
        print(f"\n【重みの変化】")
        for model_name in current_weights.keys():
            old_w = current_weights[model_name]
            new_w = new_weights[model_name]
            change = new_w - old_w
            sign = "+" if change >= 0 else ""
            print(f"  {model_name:30s}: {old_w:6.2f} → {new_w:6.2f} ({sign}{change:+.2f})")
    
    # 保存
    metadata = {
        'actual_numbers': actual_numbers,
        'model_results': model_results
    }
    save_model_weights(new_weights, metadata)
    
    if verbose:
        print(f"\n✅ 重みを更新し、保存しました")
        print(f"{'='*60}\n")
    
    return new_weights


if __name__ == "__main__":
    # テスト用
    test_predictions = {
        'ultra_stats': [[1, 6, 11, 26, 33, 40], [2, 7, 12, 27, 34, 41]],
        'hot_cold_mix': [[1, 6, 11, 26, 33, 40], [3, 8, 13, 28, 35, 42]],
        'never_appeared': [[4, 9, 14, 29, 36, 43], [5, 10, 15, 30, 37, 38]],
        'pair_affinity': [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],
        'sum_optimization': [[20, 21, 22, 23, 24, 25], [26, 27, 28, 29, 30, 31]],
        'deep_learning': [[32, 33, 34, 35, 36, 37], [38, 39, 40, 41, 42, 43]],
        'zone_balance': [[1, 10, 20, 30, 40, 43], [2, 11, 21, 31, 41, 42]],
    }
    
    actual = [1, 6, 11, 26, 33, 40]
    
    print("テスト：オンライン学習")
    new_weights = evaluate_and_update(test_predictions, actual, verbose=True)

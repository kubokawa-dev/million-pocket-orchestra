"""
ナンバーズ4用オンライン学習：新しい当選番号が出たら、モデルの重みを自動調整

仕組み：
1. 各モデルの予測結果を評価（正解が何位にあったか）
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
        'advanced_heuristics': 10.0,
        'exploratory': 8.0,
        'extreme_patterns': 3.0,
        'basic_stats': 2.0,
        'ml_model_new': 1.0,
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


def is_box_match(pred: str, actual: str) -> bool:
    """ボックス一致（順不同で数字が全て一致）をチェック"""
    return sorted(list(pred)) == sorted(list(actual))


def count_digit_matches(pred: str, actual: str) -> int:
    """何桁の数字が一致しているか（順不同）をカウント"""
    pred_counter = {}
    actual_counter = {}
    for d in pred:
        pred_counter[d] = pred_counter.get(d, 0) + 1
    for d in actual:
        actual_counter[d] = actual_counter.get(d, 0) + 1
    
    matches = 0
    for digit, count in actual_counter.items():
        matches += min(count, pred_counter.get(digit, 0))
    return matches


def update_weights_online(
    current_weights: Dict[str, float],
    predictions_by_model: Dict[str, List[str]],
    actual_number: str,
    learning_rate: float = 0.05,
    top_k: int = 50
) -> Dict[str, float]:
    """
    オンライン学習で重みを更新
    
    改善版v2.0: ボックス一致と部分一致も評価に追加！
    - ストレート一致: 最大報酬
    - ボックス一致: 70%の報酬
    - 3桁一致: 40%の報酬
    - 2桁一致: 10%の報酬
    
    Args:
        current_weights: 現在の重み
        predictions_by_model: 各モデルの予測リスト
        actual_number: 実際の当選番号
        learning_rate: 学習率（0.0-1.0、デフォルト: 0.05）
        top_k: 評価対象のTop-K（デフォルト: 50）
    
    Returns:
        更新後の重み
    """
    new_weights = current_weights.copy()
    
    for model_name, predictions in predictions_by_model.items():
        if model_name not in new_weights:
            continue
        
        best_reward = 0.0
        
        for i, pred in enumerate(predictions[:top_k]):
            rank = i + 1
            base_reward = (top_k - rank + 1) / top_k
            
            # 1. ストレート一致（完全一致）
            if pred == actual_number:
                reward = base_reward * 1.0  # 100%報酬
                best_reward = max(best_reward, reward)
                break  # 完全一致が見つかったらループ終了
            
            # 2. ボックス一致（順不同で4桁全て一致）
            elif is_box_match(pred, actual_number):
                reward = base_reward * 0.7  # 70%報酬
                best_reward = max(best_reward, reward)
                # 続けて探索（もっと良い一致があるかも）
            
            # 3. 部分一致（3桁または2桁が一致）
            else:
                digit_matches = count_digit_matches(pred, actual_number)
                if digit_matches >= 3:
                    reward = base_reward * 0.4  # 3桁一致: 40%報酬
                    best_reward = max(best_reward, reward)
                elif digit_matches >= 2:
                    reward = base_reward * 0.1  # 2桁一致: 10%報酬
                    best_reward = max(best_reward, reward)
        
        # 報酬に基づいて重みを更新
        if best_reward > 0:
            new_weights[model_name] += learning_rate * best_reward
        else:
            # 全く当たらなかった場合、ペナルティ
            penalty = learning_rate * 0.3  # ペナルティを少し軽減
            new_weights[model_name] = max(0.1, new_weights[model_name] - penalty)
    
    # 正規化（合計を元の合計に保つ）
    total_old = sum(current_weights.values())
    total_new = sum(new_weights.values())
    if total_new > 0:
        scale = total_old / total_new
        new_weights = {k: v * scale for k, v in new_weights.items()}
    
    return new_weights


def evaluate_and_update(
    predictions_by_model: Dict[str, List[str]],
    actual_number: str,
    verbose: bool = True
) -> Dict[str, float]:
    """
    予測を評価し、重みを更新して保存
    
    Args:
        predictions_by_model: 各モデルの予測リスト
        actual_number: 実際の当選番号
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
        print(f"正解: {actual_number}")
    
    # 各モデルの順位を評価（ストレート/ボックス/部分一致）
    model_results = {}
    for model_name, predictions in predictions_by_model.items():
        result = {'straight_rank': None, 'box_rank': None, 'partial_rank': None, 'partial_count': 0}
        
        for i, pred in enumerate(predictions):
            rank = i + 1
            
            # ストレート一致
            if pred == actual_number and result['straight_rank'] is None:
                result['straight_rank'] = rank
            
            # ボックス一致
            elif is_box_match(pred, actual_number) and result['box_rank'] is None:
                result['box_rank'] = rank
            
            # 部分一致（3桁以上）
            elif result['partial_rank'] is None:
                matches = count_digit_matches(pred, actual_number)
                if matches >= 3:
                    result['partial_rank'] = rank
                    result['partial_count'] = matches
        
        model_results[model_name] = result
    
    if verbose:
        print(f"\n【各モデルの予測順位】")
        for model_name, result in sorted(model_results.items(), 
                                          key=lambda x: (x[1]['straight_rank'] or 999, 
                                                        x[1]['box_rank'] or 999, 
                                                        x[1]['partial_rank'] or 999)):
            if result['straight_rank']:
                print(f"  {model_name:30s}: 🎯 {result['straight_rank']:3d}位 (ストレート!)")
            elif result['box_rank']:
                print(f"  {model_name:30s}: 📦 {result['box_rank']:3d}位 (ボックス!)")
            elif result['partial_rank']:
                print(f"  {model_name:30s}: 🎲 {result['partial_rank']:3d}位 ({result['partial_count']}桁一致)")
            else:
                print(f"  {model_name:30s}: ❌ 予測外")
    
    # 重みを更新
    new_weights = update_weights_online(current_weights, predictions_by_model, actual_number)
    
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
        'actual_number': actual_number,
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
        'advanced_heuristics': ['0100', '1234', '5678', '9012'],
        'exploratory': ['0100', '0200', '0300', '0400'],
        'extreme_patterns': ['0000', '0100', '9999', '1111'],
        'basic_stats': ['1234', '5678', '9012', '3456'],
        'ml_model_new': ['7890', '2345', '6789', '0123'],
    }
    
    actual = '0100'
    
    print("テスト：オンライン学習")
    new_weights = evaluate_and_update(test_predictions, actual, verbose=True)

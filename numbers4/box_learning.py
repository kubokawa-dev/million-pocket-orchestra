"""
ナンバーズ4 ボックス（組み合わせ）特化型学習・予測システム v1.0

従来のmodel_state.json（各桁の確率分布）とは別に、
ボックス（数字の組み合わせ）に特化したモデルを構築します。

ボックスとは：
- 4桁の数字を順不同で扱う（1263 = 1236 = 2136 = ...）
- 全部で715通りのユニークなボックスが存在
  - ABCD型（4つ異なる）: 210通り × 24並び = 5040通り → 210ボックス
  - AABC型（1つ重複）: 360通り × 12並び = 4320通り → 360ボックス
  - AABB型（2つ重複）: 45通り × 6並び = 270通り → 45ボックス
  - AAAB型（3つ重複）: 90通り × 4並び = 360通り → 90ボックス
  - AAAA型（4つ同じ）: 10通り × 1並び = 10通り → 10ボックス
  - 合計: 715ボックス

このモデルでは：
1. 過去の当選ボックスの出現頻度を学習
2. 数字の組み合わせパターンを分析
3. コールドボックス（長期間出ていない組み合わせ）を特定
4. ホットボックス（最近出やすい組み合わせ）を特定
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import numpy as np

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from tools.utils import load_all_numbers4_draws

BOX_MODEL_PATH = os.path.join(ROOT_DIR, 'numbers4', 'box_model_state.json')

# ========== ユーティリティ関数 ==========

def number_to_box(number: str) -> str:
    """4桁の番号をボックスID（ソート済み）に変換"""
    return ''.join(sorted(number))


def get_box_type(box_id: str) -> str:
    """ボックスのタイプを判定（ABCD, AABC, AABB, AAAB, AAAA）"""
    counts = sorted(Counter(box_id).values(), reverse=True)
    if counts == [1, 1, 1, 1]:
        return 'ABCD'
    elif counts == [2, 1, 1]:
        return 'AABC'
    elif counts == [2, 2]:
        return 'AABB'
    elif counts == [3, 1]:
        return 'AAAB'
    elif counts == [4]:
        return 'AAAA'
    return 'UNKNOWN'


def get_all_possible_boxes() -> List[str]:
    """全715通りのボックスIDを生成"""
    boxes = set()
    for d1 in range(10):
        for d2 in range(d1, 10):
            for d3 in range(d2, 10):
                for d4 in range(d3, 10):
                    boxes.add(f'{d1}{d2}{d3}{d4}')
    return sorted(boxes)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ========== ボックスモデルのスキーマ ==========

def ensure_box_model_schema(state: Dict) -> Dict:
    """ボックスモデルのスキーマを保証"""
    if not state:
        state = {}
    
    state.setdefault('version', 1)
    state.setdefault('updated_at', None)
    state.setdefault('total_draws', 0)
    
    # ボックス出現回数（全履歴）
    state.setdefault('box_counts', {})
    
    # ボックス出現確率（正規化済み）
    state.setdefault('box_probs', {})
    
    # 直近N回での出現回数
    state.setdefault('recent_box_counts', {})
    state.setdefault('recent_window', 50)
    
    # ホットボックス（直近で出やすい）
    state.setdefault('hot_boxes', [])
    
    # コールドボックス（長期間出ていない）
    state.setdefault('cold_boxes', [])
    
    # 数字ペアの出現頻度（ボックス内での共起）
    state.setdefault('digit_pair_counts', {})
    
    # ボックスタイプ別の出現率
    state.setdefault('box_type_probs', {
        'ABCD': 0.0,
        'AABC': 0.0,
        'AABB': 0.0,
        'AAAB': 0.0,
        'AAAA': 0.0
    })
    
    # 各数字の出現頻度（ボックス内での出現）
    state.setdefault('digit_in_box_counts', {str(d): 0 for d in range(10)})
    
    # メタデータ
    state.setdefault('metadata', {
        'last_learned_draw': None,
        'learning_events': 0
    })
    
    return state


# ========== 学習ロジック ==========

def learn_box_model_from_history(df=None) -> Dict:
    """
    全履歴からボックスモデルを学習
    
    Returns:
        学習済みのボックスモデル状態
    """
    if df is None:
        df = load_all_numbers4_draws()
    
    if df.empty:
        print("⚠️ データがありません")
        return ensure_box_model_schema({})
    
    state = ensure_box_model_schema({})
    
    # 全ボックスの出現回数をカウント
    box_counts = Counter()
    box_type_counts = Counter()
    digit_pair_counts = defaultdict(int)
    digit_in_box_counts = Counter()

    # v14.0: 指数減衰付き重み付きカウント（最近のデータをより重視）
    total_draws = len(df)
    decay_rate = 0.002  # 500回前で重み≈0.37、1000回前で≈0.14
    box_weighted_counts = defaultdict(float)

    # v14.0: 各ボックスの最終出現からの経過回数を追跡
    box_last_seen = {}  # box_id -> draws_since_last_appearance

    for idx, (_, row) in enumerate(df.iterrows()):
        number = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        box_id = number_to_box(number)
        box_type = get_box_type(box_id)

        box_counts[box_id] += 1
        box_type_counts[box_type] += 1

        # v14.0: 指数減衰重み（最新=1.0、古い=小さい）
        recency_weight = np.exp(-decay_rate * (total_draws - 1 - idx))
        box_weighted_counts[box_id] += recency_weight

        # 最終出現位置を記録
        box_last_seen[box_id] = idx

        # 数字ペアの共起をカウント
        digits = list(box_id)
        for i in range(len(digits)):
            digit_in_box_counts[digits[i]] += 1
            for j in range(i + 1, len(digits)):
                pair = ''.join(sorted([digits[i], digits[j]]))
                digit_pair_counts[pair] += 1

    # 確率に変換（重み付き）
    total_weight = sum(box_weighted_counts.values())
    box_probs = {box: w / total_weight for box, w in box_weighted_counts.items()}
    box_type_probs = {bt: count / total_draws for bt, count in box_type_counts.items()}

    # v14.0: box_recency - 各ボックスの「最後に出てからの回数」
    box_recency = {}
    for box_id, last_idx in box_last_seen.items():
        box_recency[box_id] = total_draws - 1 - last_idx

    # 直近N回の分析
    recent_window = 50
    recent_df = df.tail(recent_window)
    recent_box_counts = Counter()

    for _, row in recent_df.iterrows():
        number = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        box_id = number_to_box(number)
        recent_box_counts[box_id] += 1

    # ホットボックス（直近で出現、重み付きスコア順）
    hot_boxes = [box for box, count in recent_box_counts.most_common(20) if count >= 1]

    # v14.0: コールドボックスを「期待出現回数 vs 実際」で計算
    # 期待値: total_draws / 715 ≈ 9.7回（6950回の場合）
    expected_count = total_draws / 715.0
    cold_box_scores = []
    all_appeared_boxes = set(box_counts.keys())
    recent_appeared_boxes = set(recent_box_counts.keys())
    for box_id in all_appeared_boxes - recent_appeared_boxes:
        actual_count = box_counts[box_id]
        draws_since = box_recency.get(box_id, total_draws)
        # 期待値より少なく、かつ長期間出ていないほどスコアが高い
        cold_score = (expected_count - actual_count) + draws_since * 0.1
        cold_box_scores.append((box_id, cold_score))
    cold_box_scores.sort(key=lambda x: -x[1])
    cold_boxes = [box_id for box_id, _ in cold_box_scores[:50]]

    # 状態を更新
    state['total_draws'] = total_draws
    state['box_counts'] = dict(box_counts)
    state['box_probs'] = box_probs
    state['box_weighted_counts'] = dict(box_weighted_counts)  # v14.0 NEW
    state['box_recency'] = box_recency                        # v14.0 NEW
    state['recent_box_counts'] = dict(recent_box_counts)
    state['recent_window'] = recent_window
    state['hot_boxes'] = hot_boxes
    state['cold_boxes'] = cold_boxes
    state['digit_pair_counts'] = dict(digit_pair_counts)
    state['box_type_probs'] = box_type_probs
    state['digit_in_box_counts'] = dict(digit_in_box_counts)
    state['metadata']['last_learned_draw'] = int(df.iloc[-1]['draw_number'])
    state['metadata']['learning_events'] = total_draws
    state['updated_at'] = now_iso()

    return state


def update_box_model_with_result(state: Dict, actual_number: str) -> Dict:
    """
    新しい当選結果でボックスモデルを更新
    
    Args:
        state: 現在のモデル状態
        actual_number: 当選番号（4桁）
    
    Returns:
        更新後のモデル状態
    """
    state = ensure_box_model_schema(state)
    
    box_id = number_to_box(actual_number)
    box_type = get_box_type(box_id)
    
    # ボックス出現回数を更新
    state['box_counts'][box_id] = state['box_counts'].get(box_id, 0) + 1
    state['total_draws'] += 1
    
    # 確率を再計算
    total = state['total_draws']
    state['box_probs'] = {box: count / total for box, count in state['box_counts'].items()}
    
    # ボックスタイプの確率を更新
    type_counts = Counter()
    for box, count in state['box_counts'].items():
        bt = get_box_type(box)
        type_counts[bt] += count
    state['box_type_probs'] = {bt: count / total for bt, count in type_counts.items()}
    
    # 数字ペアの共起を更新
    digits = list(box_id)
    for i in range(len(digits)):
        state['digit_in_box_counts'][digits[i]] = state['digit_in_box_counts'].get(digits[i], 0) + 1
        for j in range(i + 1, len(digits)):
            pair = ''.join(sorted([digits[i], digits[j]]))
            state['digit_pair_counts'][pair] = state['digit_pair_counts'].get(pair, 0) + 1
    
    state['updated_at'] = now_iso()
    state['metadata']['learning_events'] += 1
    
    return state


# ========== 予測ロジック ==========

def predict_boxes_from_model(state: Dict, limit: int = 50) -> List[Tuple[str, float]]:
    """
    ボックスモデルから予測を生成
    
    戦略:
    1. 過去の出現確率が高いボックス
    2. 直近で出ていないコールドボックス
    3. 数字ペアの共起パターンから生成
    4. ボックスタイプのバランスを考慮
    5. 未出現ボックス（一度も出ていない組み合わせ）を狙う ← NEW!
    
    Returns:
        [(box_id, score), ...] のリスト
    """
    state = ensure_box_model_schema(state)
    
    predictions = {}
    
    # === 戦略1: 過去の出現確率ベース ===
    for box_id, prob in state.get('box_probs', {}).items():
        predictions[box_id] = predictions.get(box_id, 0) + prob * 100
    
    # === 戦略2: コールドボックス（そろそろ来そう、リーセンシー加味） ===
    cold_boxes = state.get('cold_boxes', [])
    box_recency = state.get('box_recency', {})
    total_draws = state.get('total_draws', 1)
    expected_interval = 715.0 / total_draws * total_draws  # ≈715回に1回
    for i, box_id in enumerate(cold_boxes[:30]):
        # v14.0: リーセンシーに基づくボーナス
        draws_since = box_recency.get(box_id, total_draws)
        # 期待間隔(≈715)を超えて出ていないほど高ボーナス
        overdue_ratio = draws_since / max(expected_interval, 1)
        bonus = 50 * (1 + overdue_ratio * 0.5) - i * 1.5
        predictions[box_id] = predictions.get(box_id, 0) + max(bonus, 10)
    
    # === 戦略3: 数字ペアの共起パターン ===
    digit_pair_counts = state.get('digit_pair_counts', {})
    top_pairs = sorted(digit_pair_counts.items(), key=lambda x: -x[1])[:20]
    
    # 頻出ペアを2つ組み合わせてボックスを生成
    for i, (pair1, count1) in enumerate(top_pairs[:10]):
        for pair2, count2 in top_pairs[i:15]:
            # 4桁の数字を作る
            digits = list(pair1) + list(pair2)
            box_id = ''.join(sorted(digits))
            
            if len(set(box_id)) >= 2:  # 最低2種類の数字
                score = (count1 + count2) * 0.5
                predictions[box_id] = predictions.get(box_id, 0) + score
    
    # === 戦略4: ボックスタイプのバランス ===
    box_type_probs = state.get('box_type_probs', {})
    
    # ABCD型（52.5%）とAABC型（40.5%）を重視
    for box_id in list(predictions.keys()):
        box_type = get_box_type(box_id)
        if box_type == 'ABCD':
            predictions[box_id] *= 1.2  # 20%ボーナス
        elif box_type == 'AABC':
            predictions[box_id] *= 1.15  # 15%ボーナス
    
    # === 戦略5: 直近で出ていない数字を含むボックス ===
    digit_in_box = state.get('digit_in_box_counts', {})
    total_digit_count = sum(digit_in_box.values())
    cold_digits = []
    if total_digit_count > 0:
        # 出現率が低い数字を特定
        for d in range(10):
            count = digit_in_box.get(str(d), 0)
            rate = count / total_digit_count
            if rate < 0.09:  # 9%未満（理論値10%より低い）
                cold_digits.append(str(d))
        
        # コールド数字を含むボックスにボーナス
        for box_id in list(predictions.keys()):
            cold_count = sum(1 for d in box_id if d in cold_digits)
            if cold_count >= 1:
                predictions[box_id] *= (1 + cold_count * 0.1)
    
    # === 戦略6: 未出現ボックスを狙う（超重要！） ===
    # 過去に一度も出ていないが、頻出数字ペアで構成されるボックス
    appeared_boxes = set(state.get('box_counts', {}).keys())
    all_boxes = get_all_possible_boxes()
    never_appeared = [box for box in all_boxes if box not in appeared_boxes]
    
    # 未出現ボックスのスコアリング
    for box_id in never_appeared:
        # 頻出数字ペアを含むかチェック
        digits = list(box_id)
        pair_score = 0
        for i in range(len(digits)):
            for j in range(i + 1, len(digits)):
                pair = ''.join(sorted([digits[i], digits[j]]))
                pair_score += digit_pair_counts.get(pair, 0)
        
        # 頻出数字を含むかチェック
        digit_score = 0
        for d in digits:
            digit_score += digit_in_box.get(d, 0)
        
        # 未出現ボックスの基本スコア（大幅強化！）
        base_score = 80  # 30→80 未出現ボーナスを大幅UP
        
        # ペアスコアと数字スコアを加算（係数UP）
        total_score = base_score + pair_score * 0.5 + digit_score * 0.1
        
        # ABCD型を優遇（さらに強化）
        if get_box_type(box_id) == 'ABCD':
            total_score *= 1.5  # 1.3→1.5
        elif get_box_type(box_id) == 'AABC':
            total_score *= 1.3  # 1.2→1.3
        
        # コールド数字を含む場合はさらにボーナス（強化）
        cold_count = sum(1 for d in box_id if d in cold_digits)
        if cold_count >= 1:
            total_score *= (1 + cold_count * 0.2)  # 0.15→0.2
        
        # 頻出数字（1,2,3）を多く含む場合はボーナス
        hot_digits = ['1', '2', '3']  # 全履歴で頻出
        hot_count = sum(1 for d in digits if d in hot_digits)
        if hot_count >= 2:
            total_score *= (1 + hot_count * 0.1)
        
        predictions[box_id] = predictions.get(box_id, 0) + total_score
    
    # ソートして返す
    sorted_predictions = sorted(predictions.items(), key=lambda x: -x[1])
    return sorted_predictions[:limit]


def predict_numbers_from_boxes(box_predictions: List[Tuple[str, float]], limit: int = 20) -> List[Tuple[str, float]]:
    """
    ボックス予測から具体的な4桁番号を生成
    
    各ボックスから1つの代表的な並びを選択
    """
    import random
    
    results = []
    seen_boxes = set()
    
    for box_id, score in box_predictions:
        if box_id in seen_boxes:
            continue
        seen_boxes.add(box_id)
        
        # ボックスからランダムな並びを生成
        digits = list(box_id)
        random.shuffle(digits)
        number = ''.join(digits)
        
        results.append((number, score))
        
        if len(results) >= limit:
            break
    
    return results


# ========== ファイル操作 ==========

def load_box_model() -> Dict:
    """ボックスモデルを読み込み"""
    if os.path.exists(BOX_MODEL_PATH):
        with open(BOX_MODEL_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        return ensure_box_model_schema(state)
    return ensure_box_model_schema({})


def save_box_model(state: Dict):
    """ボックスモデルを保存"""
    state['updated_at'] = now_iso()
    with open(BOX_MODEL_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"✅ ボックスモデルを保存しました: {BOX_MODEL_PATH}")


# ========== メイン処理 ==========

def rebuild_box_model():
    """ボックスモデルを全履歴から再構築"""
    print("🔄 ボックスモデルを全履歴から再構築中...")
    
    df = load_all_numbers4_draws()
    if df.empty:
        print("❌ データがありません")
        return
    
    state = learn_box_model_from_history(df)
    save_box_model(state)
    
    print(f"📊 学習結果:")
    print(f"   - 総抽選回数: {state['total_draws']}")
    print(f"   - ユニークボックス数: {len(state['box_counts'])}")
    print(f"   - ホットボックス: {state['hot_boxes'][:5]}")
    print(f"   - コールドボックス: {state['cold_boxes'][:5]}")
    print(f"   - ボックスタイプ分布:")
    for bt, prob in state['box_type_probs'].items():
        print(f"     {bt}: {prob*100:.1f}%")


def test_prediction():
    """予測テスト"""
    print("\n🔮 ボックス予測テスト")
    
    state = load_box_model()
    if not state.get('box_counts'):
        print("⚠️ モデルが学習されていません。rebuild_box_model()を実行してください。")
        return
    
    # ボックス予測
    box_predictions = predict_boxes_from_model(state, limit=30)
    
    print("\n📦 ボックス予測 TOP20:")
    for i, (box_id, score) in enumerate(box_predictions[:20], 1):
        box_type = get_box_type(box_id)
        print(f"  {i:2d}位: {box_id} ({box_type}) - スコア: {score:.1f}")
    
    # 1263のボックス「1236」がどこにあるか確認
    target_box = '1236'
    for i, (box_id, score) in enumerate(box_predictions, 1):
        if box_id == target_box:
            print(f"\n🎯 ボックス「{target_box}」は第{i}位にランクイン！")
            break
    else:
        print(f"\n❌ ボックス「{target_box}」はTOP{len(box_predictions)}に含まれていません")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'rebuild':
            rebuild_box_model()
        elif sys.argv[1] == 'test':
            test_prediction()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python box_learning.py [rebuild|test]")
    else:
        # デフォルト: 再構築してテスト
        rebuild_box_model()
        test_prediction()

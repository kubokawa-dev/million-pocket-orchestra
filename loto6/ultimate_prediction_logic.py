"""
🏆 ロト6 世界最強予測ロジック 🏆
目標: 6億円獲得のための究極の予測システム

10個の最先端モデルを統合したアンサンブル予測
"""

import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from itertools import combinations, product
import os
import json

NUM_RANGE = list(range(1, 44))


# ============================================================================
# Model 1: 超高度統計モデル（時系列重み付け）
# ============================================================================
def predict_ultra_stats(df: pd.DataFrame, limit: int = 20):
    """時系列で重み付けした超高度な統計分析"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 指数減衰重み付け（最近のデータほど重要）
    n = len(df)
    weights = np.exp(np.linspace(-3, 0, n))
    weights /= weights.sum()
    
    # 重み付き頻度
    weighted_freq = defaultdict(float)
    for idx, row in df.iterrows():
        w = weights[idx]
        for col in num_cols:
            if pd.notna(row[col]):
                num = int(row[col])
                weighted_freq[num] += w
    
    # トップ15の数字を選択
    top_numbers = sorted(weighted_freq.items(), key=lambda x: x[1], reverse=True)[:15]
    candidate_pool = [n for n, _ in top_numbers]
    
    # 組み合わせ生成
    predictions = set()
    # 重み付き確率でサンプリング
    probs = np.array([weighted_freq[n] for n in candidate_pool])
    probs /= probs.sum()
    
    for _ in range(limit * 50):
        combo = tuple(sorted(np.random.choice(candidate_pool, 6, replace=False, p=probs)))
        predictions.add(combo)
        if len(predictions) >= limit:
            break
    
    return [list(p) for p in predictions]


# ============================================================================
# Model 2: 未出現パターン特化モデル
# ============================================================================
def predict_never_appeared(df: pd.DataFrame, limit: int = 30):
    """過去に出現していない組み合わせを体系的に生成"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 過去の全組み合わせを取得
    historical_combos = set()
    for _, row in df.iterrows():
        combo = tuple(sorted([int(row[c]) for c in num_cols if pd.notna(row[c])]))
        if len(combo) == 6:
            historical_combos.add(combo)
    
    print(f"  [未出現モデル] 過去の組み合わせ数: {len(historical_combos)}")
    
    # 頻度の高い数字をベースに未出現組み合わせを生成
    all_numbers = np.concatenate([df[c].dropna().values for c in num_cols])
    freq = Counter(all_numbers.astype(int))
    
    # 上位20個の数字から組み合わせを生成
    top20 = [n for n, _ in freq.most_common(20)]
    
    predictions = []
    attempts = 0
    max_attempts = limit * 1000
    
    while len(predictions) < limit and attempts < max_attempts:
        attempts += 1
        # ランダムに6個選択
        combo = tuple(sorted(np.random.choice(top20, 6, replace=False)))
        
        # 未出現かつ重複していない組み合わせ
        if combo not in historical_combos and combo not in [tuple(p) for p in predictions]:
            predictions.append(list(combo))
    
    print(f"  [未出現モデル] 生成数: {len(predictions)}/{limit}")
    return predictions


# ============================================================================
# Model 3: 黄金比・数学的パターンモデル
# ============================================================================
def predict_golden_ratio(df: pd.DataFrame, limit: int = 20):
    """黄金比や数学的な美しいパターンを利用"""
    predictions = []
    
    # 黄金比 φ ≈ 1.618
    phi = (1 + np.sqrt(5)) / 2
    
    # 各数字の黄金比的な配置
    for start in range(1, 20):
        pattern = []
        current = start
        for _ in range(6):
            num = int(current) % 43
            if num == 0:
                num = 43
            if num not in pattern:
                pattern.append(num)
            current *= phi
        
        if len(pattern) == 6:
            predictions.append(sorted(pattern))
        
        if len(predictions) >= limit:
            break
    
    # フィボナッチ数列ベース
    fib = [1, 1]
    while len(fib) < 20:
        fib.append(fib[-1] + fib[-2])
    
    fib_numbers = [f % 43 if f % 43 != 0 else 43 for f in fib if f <= 100]
    if len(set(fib_numbers)) >= 6:
        for i in range(min(5, limit - len(predictions))):
            combo = sorted(np.random.choice(list(set(fib_numbers)), 6, replace=False))
            if combo not in predictions:
                predictions.append(combo)
    
    return predictions[:limit]


# ============================================================================
# Model 4: ホット＆コールド混合モデル
# ============================================================================
def predict_hot_cold_mix(df: pd.DataFrame, limit: int = 25):
    """ホットナンバーとコールドナンバーを戦略的に混合"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    all_numbers = np.concatenate([df[c].dropna().values for c in num_cols])
    freq = Counter(all_numbers.astype(int))
    
    # ホットナンバー（上位10個）
    hot = [n for n, _ in freq.most_common(10)]
    # コールドナンバー（下位10個）
    cold = [n for n, _ in freq.most_common()[-10:]]
    
    predictions = []
    
    # 様々な混合比率で組み合わせ
    mix_patterns = [
        (5, 1),  # ホット5個 + コールド1個
        (4, 2),  # ホット4個 + コールド2個
        (3, 3),  # ホット3個 + コールド3個
        (2, 4),  # ホット2個 + コールド4個
    ]
    
    for h_count, c_count in mix_patterns:
        for _ in range(limit // len(mix_patterns) + 1):
            hot_selected = np.random.choice(hot, h_count, replace=False)
            cold_selected = np.random.choice(cold, c_count, replace=False)
            combo = sorted(list(hot_selected) + list(cold_selected))
            if combo not in predictions:
                predictions.append(combo)
            if len(predictions) >= limit:
                return predictions
    
    return predictions


# ============================================================================
# Model 5: 区間バランス最適化モデル
# ============================================================================
def predict_zone_balance(df: pd.DataFrame, limit: int = 20):
    """1-43を複数の区間に分け、バランスの良い組み合わせを生成"""
    zones = [
        (1, 10),   # 低
        (11, 21),  # 中低
        (22, 32),  # 中高
        (33, 43),  # 高
    ]
    
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 各区間の過去の出現頻度を分析
    zone_patterns = defaultdict(int)
    for _, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
        zone_counts = [sum(1 for n in nums if lo <= n <= hi) for lo, hi in zones]
        zone_patterns[tuple(zone_counts)] += 1
    
    # 最頻出のバランスパターンを取得
    top_patterns = sorted(zone_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
    
    predictions = []
    for pattern, _ in top_patterns:
        # 各区間から指定数ずつ選択
        for _ in range(limit // len(top_patterns) + 1):
            combo = []
            for i, (lo, hi) in enumerate(zones):
                count = pattern[i]
                if count > 0:
                    zone_numbers = list(range(lo, hi + 1))
                    selected = np.random.choice(zone_numbers, min(count, len(zone_numbers)), replace=False)
                    combo.extend(selected)
            
            if len(combo) == 6:
                predictions.append(sorted(combo))
            
            if len(predictions) >= limit:
                return predictions
    
    return predictions


# ============================================================================
# Model 6: ペア相性分析モデル
# ============================================================================
def predict_pair_affinity(df: pd.DataFrame, limit: int = 20):
    """過去に一緒に出現した数字のペアを重視"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # ペアの出現頻度を計算
    pair_freq = defaultdict(int)
    for _, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
        for a, b in combinations(nums, 2):
            pair_freq[(min(a, b), max(a, b))] += 1
    
    # 最も相性の良いペアを取得
    top_pairs = sorted(pair_freq.items(), key=lambda x: x[1], reverse=True)[:30]
    
    predictions = []
    
    # トップペアを核に組み合わせを構築
    for (a, b), _ in top_pairs:
        # 残り4個を選択
        remaining_candidates = [n for n in NUM_RANGE if n not in [a, b]]
        for _ in range(2):
            remaining = np.random.choice(remaining_candidates, 4, replace=False)
            combo = sorted([a, b] + list(remaining))
            if combo not in predictions:
                predictions.append(combo)
            if len(predictions) >= limit:
                return predictions
    
    return predictions


# ============================================================================
# Model 7: オーバーデュー（未出現期間）モデル
# ============================================================================
def predict_overdue(df: pd.DataFrame, limit: int = 20):
    """長期間出現していない数字を優先"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 各数字の最後の出現位置を記録
    last_seen = {n: -1 for n in NUM_RANGE}
    for idx, row in df.iterrows():
        for col in num_cols:
            if pd.notna(row[col]):
                num = int(row[col])
                last_seen[num] = idx
    
    # オーバーデュー期間を計算
    max_idx = len(df) - 1
    overdue = {n: (max_idx - last_seen[n]) if last_seen[n] >= 0 else max_idx + 1 
               for n in NUM_RANGE}
    
    # オーバーデュー上位15個
    overdue_top = sorted(overdue.items(), key=lambda x: x[1], reverse=True)[:15]
    overdue_nums = [n for n, _ in overdue_top]
    
    predictions = []
    
    # オーバーデュー数字を2-4個含む組み合わせ
    for overdue_count in [2, 3, 4]:
        for _ in range(limit // 3):
            overdue_selected = np.random.choice(overdue_nums, overdue_count, replace=False)
            remaining_pool = [n for n in NUM_RANGE if n not in overdue_selected]
            remaining = np.random.choice(remaining_pool, 6 - overdue_count, replace=False)
            combo = sorted(list(overdue_selected) + list(remaining))
            if combo not in predictions:
                predictions.append(combo)
            if len(predictions) >= limit:
                return predictions
    
    return predictions


# ============================================================================
# Model 8: 偶奇バランス最適化モデル
# ============================================================================
def predict_even_odd_balance(df: pd.DataFrame, limit: int = 20):
    """偶数奇数のバランスを過去の傾向に合わせる"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 過去の偶奇パターンを分析
    eo_patterns = defaultdict(int)
    for _, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
        even_count = sum(1 for n in nums if n % 2 == 0)
        eo_patterns[even_count] += 1
    
    # 最頻出の偶奇バランスを取得
    top_balance = sorted(eo_patterns.items(), key=lambda x: x[1], reverse=True)[0][0]
    
    # 偶数と奇数のプール
    evens = [n for n in NUM_RANGE if n % 2 == 0]
    odds = [n for n in NUM_RANGE if n % 2 == 1]
    
    predictions = []
    
    # 最頻出バランスで組み合わせを生成
    for _ in range(limit):
        even_selected = np.random.choice(evens, top_balance, replace=False)
        odd_selected = np.random.choice(odds, 6 - top_balance, replace=False)
        combo = sorted(list(even_selected) + list(odd_selected))
        if combo not in predictions:
            predictions.append(combo)
    
    return predictions


# ============================================================================
# Model 9: 合計値最適化モデル
# ============================================================================
def predict_sum_optimization(df: pd.DataFrame, limit: int = 20):
    """6個の数字の合計値を過去の平均に近づける"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 過去の合計値を分析
    sums = []
    for _, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols if pd.notna(row[c])]
        if len(nums) == 6:
            sums.append(sum(nums))
    
    mean_sum = np.mean(sums)
    std_sum = np.std(sums)
    
    print(f"  [合計値モデル] 平均合計: {mean_sum:.1f}, 標準偏差: {std_sum:.1f}")
    
    # 目標範囲を設定
    target_range = (mean_sum - std_sum, mean_sum + std_sum)
    
    predictions = []
    attempts = 0
    
    while len(predictions) < limit and attempts < limit * 500:
        attempts += 1
        combo = sorted(np.random.choice(NUM_RANGE, 6, replace=False))
        combo_sum = sum(combo)
        
        # 目標範囲内の組み合わせのみ採用
        if target_range[0] <= combo_sum <= target_range[1]:
            if combo not in predictions:
                predictions.append(combo)
    
    return predictions


# ============================================================================
# Model 10: AIディープラーニング風モデル（擬似）
# ============================================================================
def predict_deep_learning_style(df: pd.DataFrame, limit: int = 30):
    """複数の特徴量を組み合わせた高度な予測"""
    num_cols = [f'num{i}' for i in range(1, 7)]
    
    # 複数の特徴量を計算
    all_numbers = np.concatenate([df[c].dropna().values for c in num_cols])
    freq = Counter(all_numbers.astype(int))
    
    # 特徴量1: 頻度スコア
    freq_scores = {n: freq.get(n, 0) / max(freq.values()) for n in NUM_RANGE}
    
    # 特徴量2: 最近の出現傾向（直近20回）
    recent_df = df.tail(20)
    recent_numbers = np.concatenate([recent_df[c].dropna().values for c in num_cols])
    recent_freq = Counter(recent_numbers.astype(int))
    recent_scores = {n: recent_freq.get(n, 0) / max(recent_freq.values() or [1]) for n in NUM_RANGE}
    
    # 特徴量3: 周期性スコア（簡易版）
    period_scores = {}
    for n in NUM_RANGE:
        appearances = []
        for idx, row in df.iterrows():
            if n in [row[c] for c in num_cols if pd.notna(row[c])]:
                appearances.append(idx)
        
        if len(appearances) >= 2:
            intervals = np.diff(appearances)
            period_scores[n] = 1.0 / (np.std(intervals) + 1)  # 安定した周期ほど高スコア
        else:
            period_scores[n] = 0.5
    
    # 総合スコアを計算（重み付き平均）
    combined_scores = {}
    for n in NUM_RANGE:
        combined_scores[n] = (
            0.4 * freq_scores.get(n, 0) +
            0.4 * recent_scores.get(n, 0) +
            0.2 * period_scores.get(n, 0)
        )
    
    # スコア上位20個を候補プールとする
    top_candidates = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:20]
    candidate_pool = [n for n, _ in top_candidates]
    candidate_scores = np.array([s for _, s in top_candidates])
    candidate_probs = candidate_scores / candidate_scores.sum()
    
    predictions = []
    
    for _ in range(limit * 10):
        combo = tuple(sorted(np.random.choice(candidate_pool, 6, replace=False, p=candidate_probs)))
        if list(combo) not in predictions:
            predictions.append(list(combo))
        if len(predictions) >= limit:
            break
    
    return predictions


# ============================================================================
# アンサンブル統合関数
# ============================================================================
def aggregate_loto6_predictions(predictions_by_model: dict, weights: dict, normalize_scores: bool = True):
    """
    各モデルの予測を重み付けして集計し、スコア付きDataFrameを返す
    
    Args:
        predictions_by_model: モデル名をキー、予測リストを値とする辞書
        weights: モデル名をキー、重みを値とする辞書
        normalize_scores: 各モデルのスコアを0-1に正規化するか（デフォルト: True）
    """
    combo_scores = defaultdict(float)
    
    for model_name, predictions in predictions_by_model.items():
        weight = weights.get(model_name, 1.0)
        
        if normalize_scores and predictions:
            # ランクベーススコア：1位=1.0, 最下位=0.0
            n = len(predictions)
            for rank, pred in enumerate(predictions):
                # 予測が文字列の場合とリストの場合に対応
                if isinstance(pred, str):
                    combo_key = pred.replace(' ', '')
                elif isinstance(pred, list):
                    combo_key = ''.join(f'{n:02d}' for n in sorted(pred))
                else:
                    continue
                
                # 線形減衰: 1位=1.0, 2位=0.99, ..., 最下位=0.0
                normalized_score = (n - rank) / n
                combo_scores[combo_key] += normalized_score * weight
        else:
            # 正規化なし（従来の方法）
            for pred in predictions:
                if isinstance(pred, str):
                    combo_key = pred.replace(' ', '')
                elif isinstance(pred, list):
                    combo_key = ''.join(f'{n:02d}' for n in sorted(pred))
                else:
                    continue
                
                combo_scores[combo_key] += weight
    
    # スコア順にソート
    sorted_combos = sorted(combo_scores.items(), key=lambda x: x[1], reverse=True)
    
    # DataFrameを作成
    df_result = pd.DataFrame([
        {
            'prediction': combo,
            'score': score,
            'numbers': ' '.join([combo[i:i+2] for i in range(0, len(combo), 2)])
        }
        for combo, score in sorted_combos
    ])
    
    return df_result


def apply_diversity_penalty(df: pd.DataFrame, penalty_strength: float = 0.3, similarity_threshold: int = 4):
    """
    多様性ペナルティを適用：類似した候補のスコアを下げる（ロト6用）
    
    Args:
        df: 予測結果のDataFrame（'prediction'と'score'列を持つ）
        penalty_strength: ペナルティの強さ（0.0-1.0、デフォルト: 0.3）
        similarity_threshold: 類似と判定する共通数字の数（デフォルト: 4）
    
    Returns:
        多様性ペナルティ適用後のDataFrame
    """
    if df.empty or len(df) <= 1:
        return df
    
    df = df.copy()
    df['adjusted_score'] = df['score'].copy()
    
    # 上位から順に処理
    for i in range(len(df)):
        current_pred = df.iloc[i]['prediction']
        # 2桁ずつ分割して数字のセットを作成
        current_numbers = set([int(current_pred[j:j+2]) for j in range(0, len(current_pred), 2)])
        
        # それより下位の候補と比較
        for j in range(i + 1, len(df)):
            other_pred = df.iloc[j]['prediction']
            other_numbers = set([int(other_pred[k:k+2]) for k in range(0, len(other_pred), 2)])
            
            # 共通する数字の数を計算
            common_count = len(current_numbers & other_numbers)
            
            # 類似度が閾値以上ならペナルティ
            if common_count >= similarity_threshold:
                penalty = penalty_strength * (common_count / 6.0)  # 6個中の共通割合
                df.loc[j, 'adjusted_score'] *= (1 - penalty)
    
    # 調整後のスコアで再ソート
    df = df.sort_values(by='adjusted_score', ascending=False).reset_index(drop=True)
    df['score'] = df['adjusted_score']  # スコアを更新
    df = df.drop(columns=['adjusted_score'])
    
    return df

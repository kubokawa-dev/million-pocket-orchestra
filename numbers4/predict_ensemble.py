import pandas as pd
import numpy as np
import sys
import os
from collections import Counter
from itertools import permutations
from dotenv import load_dotenv

load_dotenv()

# --- モジュール検索パスを追加 ---
# スクリプトの親ディレクトリ（numbers4）の親ディレクトリ（million-pocket）をパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.utils import get_db_connection, load_all_numbers4_draws
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_new_ml_model,
    predict_from_exploratory_heuristics,
    predict_from_extreme_patterns,
    predict_from_digit_repetition_model_n4,  # v10.0
    predict_from_digit_continuation_model_n4, # v10.0
    predict_from_large_change_model_n4,       # v10.0
    predict_from_realistic_frequency_model_n4,# v10.0
    predict_from_lightgbm,                    # LightGBM
    predict_from_lightgbm_with_probs,         # LightGBM + digit probabilities
    # v10.3 過去パターン学習モデル
    predict_from_transition_probability_n4,   # 遷移確率モデル
    predict_from_global_frequency_n4,         # 全体頻度モデル
    predict_from_box_pattern_analysis_n4,     # ボックスパターン分析 v10.5
    # v10.5 ボックス特化型モデル
    predict_from_hot_pair_combination_n4,     # ホットペア組み合わせ
    predict_from_digit_frequency_box_n4,      # 数字頻度ボックス
    predict_from_model_state_v2,              # model_stateチェーンモデル
    # v10.7 コールドナンバー復活モデル（NEW!）
    predict_from_cold_number_revival_n4,      # コールドナンバー復活
    # v11.1 ML近傍探索モデル（NEW! 2827問題対策）
    predict_from_ml_neighborhood_search_n4,   # ML近傍探索
    # v12.0 2404問題対策モデル（NEW!）
    predict_from_even_odd_pattern_n4,         # 偶数/奇数パターン
    predict_from_low_sum_specialist_n4,       # 低合計値特化
    predict_from_sequential_pattern_n4,       # 連続数字パターン
    # v13.0 6376問題対策モデル（NEW!）
    predict_from_adjacent_digit_pattern_n4,   # 隣接数字パターン
    # v14.0 ボックスレベルLightGBM（NEW!）
    predict_from_lgbm_box,                    # ボックスレベルLightGBM
    aggregate_predictions,
    apply_diversity_penalty
)
# v11.0 ボックス特化型モデル（NEW!）
from numbers4.box_learning import (
    load_box_model,
    predict_boxes_from_model,
    predict_numbers_from_boxes,
    rebuild_box_model,
)
from numbers4.save_prediction_history import save_ensemble_prediction
from numbers4.save_prediction_json import save_prediction_to_json
from numbers4.online_learning import load_model_weights
# learn_model_from_data は不要になったので削除

# --- 合計値ボーナス設定 ---
# 理論的な平均値: 4桁 x 4.5 = 18
# 標準偏差: 約5.7
# v12.0改善: 2404（合計10）のような低合計値も捕捉するため、許容範囲を拡大
# 実データ分析より、合計値10-26が約80%を占める
SUM_IDEAL = 18  # 理想的な合計値
SUM_TOLERANCE = 8  # 許容範囲（±8で10-26をカバー）← 6→8に拡大
SUM_BONUS_MAX = 0.25  # 最大ボーナス（25%）← 30%→25%に調整（範囲拡大の代わり）

# 過去出現に基づくボックスタイプ分布（実データから計測）
DEFAULT_BOX_DISTRIBUTION = {
    'ABCD': 0.51,
    'AABC': 0.42,
    'AABB': 0.025,
    'AAAB': 0.035,
    'AAAA': 0.002,
}

# 保存用に展開する候補数の上限
MAX_PERMUTATION_CANDIDATES = 400


def apply_sum_bonus(
    df: pd.DataFrame,
    ideal_sum: int = SUM_IDEAL, 
    tolerance: int = SUM_TOLERANCE,
    max_bonus: float = SUM_BONUS_MAX,
    out_of_range_penalty: float = 0.95
) -> pd.DataFrame:
    """
    合計値ボーナスを適用: 理想的な合計値に近い候補のスコアを上げる
    
    Numbers4の合計値 (0-36) の分布は正規分布に近く、
    平均18、標準偏差約5.7となる。
    合計値15-24が全体の約50%を占めるため、この範囲にボーナスを付与。
    
    Args:
        df: 予測結果のDataFrame ('prediction'と'score'列を持つ)
        ideal_sum: 理想的な合計値 (デフォルト: 18)
        tolerance: 許容範囲 (デフォルト: 6、つまり12-24がボーナス対象)
        max_bonus: 最大ボーナス倍率 (デフォルト: 0.3 = 30%)
        out_of_range_penalty: 範囲外のペナルティ倍率 (デフォルト: 0.95 = 5%減)
    
    Returns:
        合計値ボーナス適用後のDataFrame
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    def calc_bonus(pred: str) -> float:
        """予測番号の合計値に基づいてボーナス倍率を計算"""
        # 入力検証: 4桁の数字文字列であることを確認
        if not isinstance(pred, str) or not pred.isdigit() or len(pred) != 4:
            return 1.0
        
        s = sum(int(d) for d in pred)
        distance = abs(s - ideal_sum)
        
        if distance <= tolerance:
            # 距離が近いほどボーナスが大きい
            # distance=0 で max_bonus、distance=tolerance で 0
            bonus = max_bonus * (1 - distance / tolerance)
            return 1.0 + bonus
        else:
            # 範囲外はペナルティ
            return out_of_range_penalty
    
    # ボーナスを適用
    df['sum_bonus'] = df['prediction'].apply(calc_bonus)
    df['score'] = df['score'] * df['sum_bonus']
    df = df.drop(columns=['sum_bonus'])
    
    # スコアで再ソート
    df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    return df


# --- ボックス分布バランサー & 順列展開ユーティリティ ---

def compute_box_distribution_from_history(df: pd.DataFrame) -> dict:
    """過去データからボックスタイプの出現割合を算出"""
    if df is None or df.empty:
        return DEFAULT_BOX_DISTRIBUTION.copy()

    counts = Counter()
    for _, row in df.iterrows():
        number = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
        box_type, _ = get_box_type(number)
        counts[box_type] += 1

    total = sum(counts.values())
    if total == 0:
        return DEFAULT_BOX_DISTRIBUTION.copy()

    distribution = {}
    for box_type, default_ratio in DEFAULT_BOX_DISTRIBUTION.items():
        ratio = counts.get(box_type, 0) / total
        if ratio == 0:
            ratio = default_ratio
        distribution[box_type] = ratio

    # 正規化（合計が1になるように）
    norm = sum(distribution.values())
    return {k: v / norm for k, v in distribution.items() if norm}


def annotate_box_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """予測DFにボックスタイプ情報を付与"""
    if df.empty:
        return df

    df = df.copy()
    box_types = []
    box_coverages = []
    for pred in df['prediction']:
        box_type, coverage = get_box_type(str(pred))
        box_types.append(box_type)
        box_coverages.append(coverage)

    df['box_type'] = box_types
    df['box_coverage'] = box_coverages
    return df


def apply_box_type_balance(
    df: pd.DataFrame,
    target_distribution: dict,
    min_multiplier: float = 0.4,
    max_multiplier: float = 2.5,
) -> pd.DataFrame:
    """予測DFのボックスタイプ比率を実績分布に寄せる (v16: 調整力強化 0.6-1.6 → 0.4-2.5)"""
    if df.empty or 'box_type' not in df.columns:
        return df

    df = df.copy()
    counts = df['box_type'].value_counts()
    total = len(df)
    adjustments = {}

    for box_type, target_ratio in target_distribution.items():
        current_ratio = counts.get(box_type, 0) / total if total else 0
        if current_ratio == 0:
            multiplier = max_multiplier
        else:
            multiplier = target_ratio / current_ratio
        multiplier = max(min(multiplier, max_multiplier), min_multiplier)
        adjustments[box_type] = multiplier

    df['score'] = df.apply(
        lambda row: row['score'] * adjustments.get(row['box_type'], 1.0), axis=1
    )
    df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    return df


def expand_predictions_with_permutations(
    df: pd.DataFrame,
    max_candidates: int = MAX_PERMUTATION_CANDIDATES,
) -> pd.DataFrame:
    """ストレート当て用に各ボックスの順列を展開"""
    if df.empty:
        return df

    expanded_rows = []
    seen_numbers = set()

    for idx, row in df.iterrows():
        number = str(row['prediction'])
        base_score = float(row['score'])
        box_type = row.get('box_type')
        box_coverage = row.get('box_coverage')

        permutations_set = {"".join(p) for p in set(permutations(number))}
        # scoreの順位はベース番号に従わせる
        for perm in sorted(permutations_set):
            if perm in seen_numbers:
                continue

            expanded_rows.append({
                'prediction': perm,
                'score': base_score,
                'box_type': box_type,
                'box_coverage': box_coverage,
                'source_prediction': number,
                'source_rank': idx + 1,
            })
            seen_numbers.add(perm)

            if len(expanded_rows) >= max_candidates:
                break

        if len(expanded_rows) >= max_candidates:
            break

    if not expanded_rows:
        return df.copy()

    expanded_df = pd.DataFrame(expanded_rows)
    expanded_df = expanded_df.sort_values(
        by=['source_rank', 'score'], ascending=[True, False]
    ).reset_index(drop=True)
    return expanded_df


# --- ボックスタイプ判定関数 (共通ユーティリティからインポート) ---
from numbers4.box_utils import get_box_type


# --- 設定 ---
NUM_PREDICTIONS_BASIC = 5
NUM_PREDICTIONS_ADVANCED = 5
NUM_PREDICTIONS_ML_NEW = 15
NUM_PREDICTIONS_EXPLORATORY = 20
NUM_PREDICTIONS_EXTREME = 15

# v10.0 モデル設定
NUM_PREDICTIONS_DIGIT_REPETITION = 300
NUM_PREDICTIONS_DIGIT_CONTINUATION = 250
NUM_PREDICTIONS_LARGE_CHANGE = 200
NUM_PREDICTIONS_REALISTIC_FREQUENCY = 400


def load_all_draws():
    """データベースからすべての抽選データを読み込む（SQLite版）"""
    # tools/utils.pyのload_all_numbers4_draws()を利用
    df = load_all_numbers4_draws()
    # カラム名の互換性を保つ（winning_numbers → numbers）
    if 'winning_numbers' in df.columns:
        df = df.rename(columns={'winning_numbers': 'numbers'})
    if 'date' in df.columns:
        df = df.rename(columns={'date': 'draw_date'})
    return df

def generate_ensemble_prediction(progress_callback=None):
    """
    アンサンブル予測を実行し、結果のDataFrameを返す。
    StreamlitのUI更新用に、進捗を報告するコールバックを受け取る。
    """
    def report_progress(progress, message):
        if progress_callback:
            progress_callback(progress, message)

    report_progress(0.0, "データベースから全抽選データを読み込んでいます...")
    all_draws_df = load_all_draws()
    target_box_distribution = compute_box_distribution_from_history(all_draws_df)

    if all_draws_df.empty:
        # Streamlitにエラーを伝えるために空のDataFrameを返すか、例外を発生させる
        return pd.DataFrame()
    
    # モデルの更新状況を確認
    model_path = os.path.join(os.path.dirname(__file__), 'model_state.json')
    if os.path.exists(model_path):
        import json
        from datetime import datetime, timezone
        with open(model_path, 'r') as f:
            model_state = json.load(f)
        updated_at = model_state.get('updated_at', '')
        events = model_state.get('events', 0)
        if updated_at:
            try:
                updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                age_hours = (datetime.now(timezone.utc) - updated_dt).total_seconds() / 3600
                if age_hours > 24 or events < 10:
                    report_progress(0.05, f"警告: モデルが{age_hours:.1f}時間前に更新（学習イベント{events}回）。learn_from_predictions.pyの実行を推奨。")
            except:
                pass

    report_progress(0.1, "各モデルで予測を生成しています...")
    
    # 1. 基本統計モデル
    predictions_basic = predict_from_basic_stats(all_draws_df, NUM_PREDICTIONS_BASIC)
    report_progress(0.15, f"- 基本統計モデル予測完了: {len(predictions_basic)}件")

    # 2. 高度なヒューリスティックモデル
    predictions_advanced = predict_from_advanced_heuristics(all_draws_df, NUM_PREDICTIONS_ADVANCED)
    report_progress(0.2, f"- 高度ヒューリスティックモデル予測完了: {len(predictions_advanced)}件")

    # 3. 新しい機械学習モデル
    predictions_ml_new = predict_with_new_ml_model(all_draws_df, limit=NUM_PREDICTIONS_ML_NEW)
    report_progress(0.25, f"- 新MLモデル予測完了: {len(predictions_ml_new)}件")

    # 4. 探索的ヒューリスティックモデル
    predictions_exploratory = predict_from_exploratory_heuristics(all_draws_df, NUM_PREDICTIONS_EXPLORATORY)
    report_progress(0.3, f"- 探索的モデル予測完了: {len(predictions_exploratory)}件")

    # 5. 極端パターンモデル
    predictions_extreme = predict_from_extreme_patterns(all_draws_df, NUM_PREDICTIONS_EXTREME)
    report_progress(0.35, f"- 極端パターンモデル予測完了: {len(predictions_extreme)}件")

    # --- v10.0 新モデル ---
    
    # 6. 数字再出現モデル
    report_progress(0.4, "- [v10] 数字再出現モデルで予測中...")
    predictions_repetition = predict_from_digit_repetition_model_n4(all_draws_df, NUM_PREDICTIONS_DIGIT_REPETITION)
    report_progress(0.5, f"- [v10] 数字再出現モデル完了: {len(predictions_repetition)}件")

    # 7. 桁継続モデル
    report_progress(0.55, "- [v10] 桁継続モデルで予測中...")
    predictions_continuation = predict_from_digit_continuation_model_n4(all_draws_df, NUM_PREDICTIONS_DIGIT_CONTINUATION)
    report_progress(0.65, f"- [v10] 桁継続モデル完了: {len(predictions_continuation)}件")

    # 8. 大変化モデル
    report_progress(0.7, "- [v10] 大変化モデルで予測中...")
    predictions_large_change = predict_from_large_change_model_n4(all_draws_df, NUM_PREDICTIONS_LARGE_CHANGE)
    report_progress(0.75, f"- [v10] 大変化モデル完了: {len(predictions_large_change)}件")

    # 9. 現実的頻度モデル
    report_progress(0.8, "- [v10] 現実的頻度モデルで予測中...")
    predictions_realistic = predict_from_realistic_frequency_model_n4(all_draws_df, NUM_PREDICTIONS_REALISTIC_FREQUENCY)
    report_progress(0.85, f"- [v10] 現実的頻度モデル完了: {len(predictions_realistic)}件")

    # 10. LightGBMモデル
    report_progress(0.82, "- [ML] LightGBMモデルで予測中...")
    predictions_lgbm, lgbm_digit_probs = predict_from_lightgbm_with_probs(all_draws_df, limit=20)
    report_progress(0.84, f"- [ML] LightGBMモデル完了: {len(predictions_lgbm)}件")

    # 10.5 model_stateチェーンモデル（桁間相関を活用）
    report_progress(0.845, "- [state] model_stateチェーンモデルで予測中...")
    predictions_state_chain = predict_from_model_state_v2(limit=150)
    report_progress(0.85, f"- [state] model_stateチェーンモデル完了: {len(predictions_state_chain)}件")

    # --- v10.3 過去パターン学習モデル（直近依存からの脱却！） ---
    
    # 11. 遷移確率モデル（全履歴から学習）
    report_progress(0.85, "- [v10.3] 遷移確率モデルで予測中...")
    predictions_transition = predict_from_transition_probability_n4(all_draws_df, limit=200)
    report_progress(0.87, f"- [v10.3] 遷移確率モデル完了: {len(predictions_transition)}件")
    
    # 12. 全体頻度モデル（全履歴から学習）
    report_progress(0.88, "- [v10.3] 全体頻度モデルで予測中...")
    predictions_global_freq = predict_from_global_frequency_n4(all_draws_df, limit=150)
    report_progress(0.89, f"- [v10.3] 全体頻度モデル完了: {len(predictions_global_freq)}件")
    
    # 13. ボックスパターン分析モデル v10.5（ペア分析強化版）
    report_progress(0.90, "- [v10.5] ボックスパターン分析モデルで予測中...")
    predictions_box_pattern = predict_from_box_pattern_analysis_n4(all_draws_df, limit=100)
    report_progress(0.91, f"- [v10.5] ボックスパターン分析モデル完了: {len(predictions_box_pattern)}件")
    
    # --- v10.5 ボックス/セット特化モデル ---
    
    # 14. ホットペア組み合わせモデル（頻出ペアを2つ組み合わせ）
    report_progress(0.92, "- [v10.5] ホットペア組み合わせモデルで予測中...")
    predictions_hot_pair = predict_from_hot_pair_combination_n4(all_draws_df, limit=120)
    report_progress(0.93, f"- [v10.5] ホットペア組み合わせモデル完了: {len(predictions_hot_pair)}件")
    
    # 15. 数字頻度ボックスモデル（ABCD型優先）
    report_progress(0.94, "- [v10.5] 数字頻度ボックスモデルで予測中...")
    predictions_digit_freq_box = predict_from_digit_frequency_box_n4(all_draws_df, limit=100)
    report_progress(0.95, f"- [v10.5] 数字頻度ボックスモデル完了: {len(predictions_digit_freq_box)}件")
    
    # 16. コールドナンバー復活モデル（v10.7 NEW!）
    report_progress(0.955, "- [v10.7] コールドナンバー復活モデルで予測中...")
    predictions_cold_revival = predict_from_cold_number_revival_n4(all_draws_df, limit=150)
    report_progress(0.96, f"- [v10.7] コールドナンバー復活モデル完了: {len(predictions_cold_revival)}件")
    
    # 17. ボックス特化型モデル（v11.0 NEW! 最重要！）
    report_progress(0.965, "- [v11.0] ボックス特化型モデルで予測中...")
    try:
        box_model_state = load_box_model()
        if not box_model_state.get('box_counts'):
            # モデルが未学習の場合は再構築
            report_progress(0.966, "  → ボックスモデルを構築中...")
            rebuild_box_model()
            box_model_state = load_box_model()
        
        box_predictions = predict_boxes_from_model(box_model_state, limit=100)
        predictions_box_model = predict_numbers_from_boxes(box_predictions, limit=100)
        predictions_box_model = [num for num, _ in predictions_box_model]
        report_progress(0.97, f"- [v11.0] ボックス特化型モデル完了: {len(predictions_box_model)}件")
    except Exception as e:
        print(f"⚠️ ボックスモデルの読み込みに失敗: {e}")
        predictions_box_model = []
    
    # 18. ML近傍探索モデル（v11.1 NEW! 2827問題対策）
    report_progress(0.975, "- [v11.1] ML近傍探索モデルで予測中...")
    predictions_ml_neighborhood = predict_from_ml_neighborhood_search_n4(all_draws_df, limit=200)
    report_progress(0.98, f"- [v11.1] ML近傍探索モデル完了: {len(predictions_ml_neighborhood)}件")

    # --- v12.0 2404問題対策モデル（NEW!） ---
    
    # 19. 偶数/奇数パターンモデル（全偶数・全奇数を狙う）
    report_progress(0.981, "- [v12.0] 偶数/奇数パターンモデルで予測中...")
    predictions_even_odd = predict_from_even_odd_pattern_n4(all_draws_df, limit=150)
    report_progress(0.984, f"- [v12.0] 偶数/奇数パターンモデル完了: {len(predictions_even_odd)}件")
    
    # 20. 低合計値特化モデル（合計値0-12を狙う）
    report_progress(0.985, "- [v12.0] 低合計値特化モデルで予測中...")
    predictions_low_sum = predict_from_low_sum_specialist_n4(all_draws_df, limit=100)
    report_progress(0.988, f"- [v12.0] 低合計値特化モデル完了: {len(predictions_low_sum)}件")
    
    # 21. 連続数字パターンモデル（0,2,4のような連続を狙う）
    report_progress(0.985, "- [v12.0] 連続数字パターンモデルで予測中...")
    predictions_sequential = predict_from_sequential_pattern_n4(all_draws_df, limit=100)
    report_progress(0.988, f"- [v12.0] 連続数字パターンモデル完了: {len(predictions_sequential)}件")
    
    # 22. 隣接数字パターンモデル（v13.0 NEW! 6376問題対策）
    report_progress(0.986, "- [v13.0] 隣接数字パターンモデルで予測中...")
    predictions_adjacent = predict_from_adjacent_digit_pattern_n4(all_draws_df, limit=150)
    report_progress(0.988, f"- [v13.0] 隣接数字パターンモデル完了: {len(predictions_adjacent)}件")

    # 23. ボックスレベルLightGBMモデル（v14.0 NEW! ボックス直接予測）
    report_progress(0.989, "- [v14.0] ボックスレベルLightGBMモデルで予測中...")
    predictions_lgbm_box = predict_from_lgbm_box(all_draws_df, limit=150)
    report_progress(0.992, f"- [v14.0] ボックスレベルLightGBMモデル完了: {len(predictions_lgbm_box)}件")

    # --- アンサンブル集計 ---
    report_progress(0.993, "全モデルの予測を統合・集計中...")
    
    # v13.0: 学習済み重みを動的に読み込み、デフォルト重みとマージ
    from numbers4.evaluate_methods import load_method_weights
    
    # デフォルト重み（ベースライン）
    default_weights = {
        # v11.0 ボックス特化型モデル（最重要！未出現ボックスを狙う）
        'box_model': 45.0,                # ボックス特化型モデル
        
        # v11.1 ML近傍探索モデル（2827問題対策）
        'ml_neighborhood': 30.0,          # ML近傍探索
        
        # v12.0 2404問題対策モデル（偶奇・低合計値・連続パターン）
        'even_odd_pattern': 40.0,         # 偶数/奇数パターン
        'low_sum_specialist': 35.0,       # 低合計値特化
        'sequential_pattern': 25.0,       # 連続数字パターン
        
        # v13.0 6376問題対策モデル（隣接数字パターン）
        'adjacent_digit': 35.0,           # 隣接数字パターン

        # v14.0 ボックスレベルLightGBM（NEW! ボックス組み合わせを直接予測）
        'lgbm_box': 40.0,                # ボックスレベルLightGBM（NEW!）
        
        # v10.7 コールドナンバー復活モデル
        'cold_revival': 22.0,             # コールドナンバー復活
        
        # v10.5 ボックス/セット特化モデル
        'hot_pair': 18.0,                 # ホットペア組み合わせ
        'box_pattern': 16.0,              # ボックスパターン分析
        'digit_freq_box': 14.0,           # 数字頻度ボックス
        
        # model_stateチェーンモデル（桁間相関）
        'state_chain': 10.0,              # model_state.json のpair_probsを活用
        
        # v10.3 過去パターン学習モデル（全履歴ベース）
        'transition_probability': 12.0,   # 遷移確率
        'global_frequency': 18.0,         # 全体頻度
        
        # v10.0 モデル（直近依存 - 低重み維持）
        'digit_repetition': 4.0,          # 数字再出現
        'digit_continuation': 3.0,        # 桁継続
        'realistic_frequency': 4.0,       # 現実的頻度
        
        # 変化パターンモデル
        'large_change': 8.0,              # 大変化
        
        # 多様性モデル
        'advanced_heuristics': 3.0,       # 統計分析
        'exploratory': 10.0,              # 探索的分析
        'extreme_patterns': 3.0,          # 極端パターン
        
        # 補助モデル
        'basic_stats': 2.0,               # 基本統計
        'ml_model_new': 2.0,              # 機械学習
        'lightgbm': 12.0,                 # LightGBM
    }
    
    # 学習済み重みを読み込み（method_weights.json から）
    learned_weights = load_method_weights()
    
    # v13.0: デフォルト重みと学習済み重みをスマートにマージ
    # 学習済み重みがある手法は、デフォルトと学習済みの加重平均を使用
    # これにより、学習の効果を反映しつつ、極端な重みの変動を防ぐ
    ensemble_weights = default_weights.copy()
    
    LEARNING_BLEND_RATIO = 0.6  # 学習済み重みの反映率（60%）
    
    for method, default_w in default_weights.items():
        if method in learned_weights:
            learned_w = learned_weights[method]
            # 加重平均: デフォルト40% + 学習済み60%
            blended_w = default_w * (1 - LEARNING_BLEND_RATIO) + learned_w * LEARNING_BLEND_RATIO
            # 極端な値を防ぐためにクリップ
            ensemble_weights[method] = max(1.0, min(60.0, blended_w))
    
    report_progress(0.994, f"学習済み重みを反映（ブレンド率: {LEARNING_BLEND_RATIO*100:.0f}%）")
    
    # === Hot Model 戦略の組み込み ===
    try:
        from numbers4.predict_hot_models import analyze_hot_models
        latest_draw = int(all_draws_df['draw_number'].max())
        target_draw = latest_draw + 1
        
        report_progress(0.995, f"直近5回のトレンド（Hot Model）を分析中...")
        hot_models = analyze_hot_models(target_draw, lookback=5, top_k=100, quiet=True)
        
        if hot_models and hot_models[0][1] > 0:
            top_model = hot_models[0][0]
            
            # 1位のモデルには特別ボーナス（元の重みの1.5倍、最大+20.0）
            if top_model in ensemble_weights:
                bonus = min(20.0, ensemble_weights[top_model] * 0.5)
                ensemble_weights[top_model] += bonus
                report_progress(0.996, f"🔥 Hot Model【{top_model}】にボーナス +{bonus:.1f} を付与！")
                
            # 2位のモデルにも少しボーナス
            if len(hot_models) > 1 and hot_models[1][1] > 0:
                second_model = hot_models[1][0]
                if second_model in ensemble_weights:
                    bonus = min(10.0, ensemble_weights[second_model] * 0.2)
                    ensemble_weights[second_model] += bonus
                    report_progress(0.996, f"✨ 2位 Model【{second_model}】にボーナス +{bonus:.1f} を付与！")
    except Exception as e:
        print(f"Hot Model分析中にエラー: {e}")
        
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model_new': predictions_ml_new,
        'exploratory': predictions_exploratory,
        'extreme_patterns': predictions_extreme,
        # v10.0 直近依存モデル
        'digit_repetition': predictions_repetition,
        'digit_continuation': predictions_continuation,
        'large_change': predictions_large_change,
        'realistic_frequency': predictions_realistic,
        # v10.3 過去パターン学習モデル
        'transition_probability': predictions_transition,
        'global_frequency': predictions_global_freq,
        # v10.5 ボックス特化モデル
        'box_pattern': predictions_box_pattern,
        'hot_pair': predictions_hot_pair,
        'digit_freq_box': predictions_digit_freq_box,
        # v10.7 コールドナンバー復活モデル
        'cold_revival': predictions_cold_revival,
        # v11.0 ボックス特化型モデル（NEW! 最重要）
        'box_model': predictions_box_model,
        # v11.1 ML近傍探索モデル（NEW! 2827問題対策）
        'ml_neighborhood': predictions_ml_neighborhood,
        # v12.0 2404問題対策モデル（NEW!）
        'even_odd_pattern': predictions_even_odd,
        'low_sum_specialist': predictions_low_sum,
        'sequential_pattern': predictions_sequential,
        # v13.0 6376問題対策モデル（NEW!）
        'adjacent_digit': predictions_adjacent,
        # v14.0 ボックスレベルLightGBM（NEW!）
        'lgbm_box': predictions_lgbm_box,
        # ML
        'lightgbm': predictions_lgbm,
        # model_state
        'state_chain': predictions_state_chain,
    }

    # 重み付けして集計（スコア正規化を有効化）
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights, normalize_scores=True)
    
    # 多様性ペナルティを適用（類似した候補のスコアを下げる）
    # v10.1: penalty_strength を 0.2 → 0.4 に強化
    final_predictions_df = apply_diversity_penalty(final_predictions_df, penalty_strength=0.4, similarity_threshold=2)
    
    # 合計値ボーナスを適用 (合計値15-24の範囲にある候補を優遇)
    # v10.1: 合計値が理想的な範囲にある候補にボーナスを付与
    report_progress(0.95, "合計値ボーナスを適用中...")
    final_predictions_df = apply_sum_bonus(final_predictions_df)
    
    # v10.2: ボックスユニーク保証 - 同じ数字の組み合わせ（順不同）を持つ候補を排除
    # これにより、毎回異なるボックス組み合わせの予測が出力される
    report_progress(0.97, "ボックスユニーク処理中...")
    seen_boxes = set()
    box_unique_rows = []
    for idx, row in final_predictions_df.iterrows():
        pred_num = str(row['prediction'])
        box_id = "".join(sorted(pred_num))  # 数字をソートしてボックスIDを作成
        if box_id not in seen_boxes:
            seen_boxes.add(box_id)
            box_unique_rows.append(row)
    final_predictions_df = pd.DataFrame(box_unique_rows).reset_index(drop=True)
    
    # v11.1: ボックス情報を追加 & 分布調整
    report_progress(0.98, "ボックス情報を追加中...")
    final_predictions_df = annotate_box_metadata(final_predictions_df)
    final_predictions_df = apply_box_type_balance(final_predictions_df, target_box_distribution)

    # v16.0: ABCD型(シングル)の最低保証
    # 実データではABCD型が51%を占めるのに、予測上位20件にABCD型が不足しがち
    # Top20のうち最低10件(50%)はABCD型を確保する
    report_progress(0.985, "ABCD型最低保証を適用中...")
    ABCD_MIN_IN_TOP20 = 10
    top_20 = final_predictions_df.head(20)
    abcd_in_top20 = len(top_20[top_20['box_type'].str.contains('ABCD', na=False)]) if 'box_type' in top_20.columns else 0

    if abcd_in_top20 < ABCD_MIN_IN_TOP20:
        # Top20外のABCD型候補を探してスコアをブーストし上位に引き上げる
        deficit = ABCD_MIN_IN_TOP20 - abcd_in_top20
        rest = final_predictions_df.iloc[20:]
        abcd_rest = rest[rest['box_type'].str.contains('ABCD', na=False)] if 'box_type' in rest.columns else pd.DataFrame()

        if not abcd_rest.empty:
            # 不足分のABCD型候補のスコアをTop20の最低スコアより少し上にブースト
            top20_min_score = top_20['score'].min() if len(top_20) > 0 else 0
            boost_targets = abcd_rest.head(deficit).index
            final_predictions_df.loc[boost_targets, 'score'] = top20_min_score + 0.01

        # 再ソート
        final_predictions_df = final_predictions_df.sort_values(by='score', ascending=False).reset_index(drop=True)
        new_abcd = len(final_predictions_df.head(20)[final_predictions_df.head(20)['box_type'].str.contains('ABCD', na=False)]) if 'box_type' in final_predictions_df.columns else 0
        report_progress(0.99, f"ABCD型: {abcd_in_top20} → {new_abcd}件 (Top20中)")

    # 保存用に順列を展開
    storage_predictions_df = expand_predictions_with_permutations(final_predictions_df)
    
    report_progress(1.0, "予測完了！")
    
    # 予測履歴をデータベースに保存
    print("\n💾 予測結果をデータベースに保存中...")
    try:
        # モデル状態を読み込み
        model_state = None
        if os.path.exists(model_path):
            import json
            with open(model_path, 'r') as f:
                model_state = json.load(f)
        
        # 履歴を保存（DB）
        prediction_id = save_ensemble_prediction(
            predictions_df=storage_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model=predictions_by_model,
            model_state=model_state,
            notes="v11.0 Update: ボックス特化型モデル追加（未出現ボックス狙い）+ 1263問題完全対策"
        )
        print(f"✅ 予測履歴の保存が完了しました (ID: {prediction_id})")
        
        # JSONにも保存（GitHub Actions用：リポジトリにコミットして蓄積）
        from numbers4.save_prediction_history import get_latest_draw_info
        conn = get_db_connection()
        latest_draw = get_latest_draw_info(conn)
        conn.close()
        target_draw = latest_draw['draw_number'] + 1 if latest_draw else None
        
        if target_draw:
            # 上位20件の類似パターンを生成（各10件）
            similar_patterns_dict = {}
            for _, row in final_predictions_df.head(20).iterrows():
                number = str(row['prediction'])
                patterns = generate_similar_patterns_n4(
                    number,
                    count=10,
                    all_draws_df=all_draws_df,
                    preds_probs=lgbm_digit_probs
                )
                if patterns:
                    similar_patterns_dict[number] = [
                        {'number': p[0], 'description': p[1], 'score': round(float(p[2]), 4)}
                        for p in patterns
                    ]
            
            save_prediction_to_json(
                predictions_df=final_predictions_df,
                ensemble_weights=ensemble_weights,
                target_draw_number=target_draw,
                similar_patterns=similar_patterns_dict,
                hot_models=hot_models if 'hot_models' in locals() else None
            )
    except Exception as e:
        # 履歴保存に失敗しても予測結果は返す
        import traceback
        print(f"❌ 予測履歴の保存に失敗しました: {e}")
        print(f"   詳細: {traceback.format_exc()}")
    
    return final_predictions_df, ensemble_weights


def generate_similar_patterns_n4(number: str, count: int = 3, all_draws_df=None, preds_probs=None):
    """
    統計分析に基づいて、指定された4桁の番号に対して類似パターンを生成（ナンバーズ4版）
    
    過去の当選データを分析し、実際に起こりやすいパターンを提案
    
    Args:
        number: 4桁の番号（例: "1234"）
        count: 生成する類似パターンの数
        all_draws_df: 全抽選データのDataFrame（統計分析用）
    
    Returns:
        [(番号, 説明, スコア), ...] のリスト
    """
    # --- ML誘導版（LightGBMの各桁確率を使って“近いけど次回っぽい”を選抜） ---
    if preds_probs and all(k in preds_probs for k in ['d1', 'd2', 'd3', 'd4']):
        if not isinstance(number, str) or not number.isdigit() or len(number) != 4:
            return []

        base_digits = [int(d) for d in number]

        def sum_bonus_multiplier(num_str: str) -> float:
            # predict_ensemble.py の apply_sum_bonus と同じ思想（理想18±6を優遇）
            ideal_sum = SUM_IDEAL
            tolerance = SUM_TOLERANCE
            max_bonus = SUM_BONUS_MAX
            out_of_range_penalty = 0.95
            s = sum(int(d) for d in num_str)
            dist = abs(s - ideal_sum)
            if dist <= tolerance:
                bonus = max_bonus * (1 - dist / tolerance)
                return 1.0 + bonus
            return out_of_range_penalty

        def ml_logp(num_str: str) -> float:
            eps = 1e-12
            d = [int(x) for x in num_str]
            return (
                float(np.log(preds_probs['d1'][d[0]] + eps)) +
                float(np.log(preds_probs['d2'][d[1]] + eps)) +
                float(np.log(preds_probs['d3'][d[2]] + eps)) +
                float(np.log(preds_probs['d4'][d[3]] + eps))
            )

        def hamming(a: str, b: str) -> int:
            return sum(x != y for x, y in zip(a, b))

        def is_same_box(a: str, b: str) -> bool:
            return sorted(a) == sorted(b)

        # 候補生成（多めに作って、ML確率×近さで再ランキング）
        candidates = {}  # num_str -> reason

        # 1) ボックス（並び替え）候補
        for p in set(permutations(base_digits, 4)):
            cand = "".join(map(str, p))
            if cand != number:
                candidates[cand] = "並び替え(ボックス)"

        # 2) 1〜2桁だけ“高確率の数字”に差し替え
        topk = 5
        top_digits = {}
        for pos, key in enumerate(['d1', 'd2', 'd3', 'd4']):
            probs = np.array(preds_probs[key], dtype=np.float64)
            top_digits[pos] = [int(i) for i in probs.argsort()[::-1][:topk]]

        # 1桁変更
        for pos in range(4):
            for d in top_digits[pos]:
                if d == base_digits[pos]:
                    continue
                new_digits = base_digits.copy()
                new_digits[pos] = d
                cand = "".join(map(str, new_digits))
                candidates.setdefault(cand, f"ML高確率で{pos+1}桁目だけ変更")

        # 2桁変更（ランダムサンプル）
        # 予測番号ごとに“安定して”異なる探索ができるよう、番号からseedを作る（先頭0もOK）
        try:
            seed = int(number)
        except Exception:
            seed = 42
        rng = np.random.default_rng(seed)
        for _ in range(300):
            pos1, pos2 = rng.choice(4, size=2, replace=False)
            d1 = int(rng.choice(top_digits[pos1]))
            d2 = int(rng.choice(top_digits[pos2]))
            new_digits = base_digits.copy()
            new_digits[pos1] = d1
            new_digits[pos2] = d2
            cand = "".join(map(str, new_digits))
            if cand != number:
                candidates.setdefault(cand, "ML高確率で2桁変更")

        # 3) 確率分布からサンプリングしつつ、元番号に寄せる（探索）
        # keep_prob が高いほど「元の数字を保持」しやすい
        keep_prob = 0.70
        for _ in range(800):
            digits = []
            for pos, key in enumerate(['d1', 'd2', 'd3', 'd4']):
                if rng.random() < keep_prob:
                    digits.append(base_digits[pos])
                else:
                    digits.append(int(rng.choice(10, p=preds_probs[key])))
            cand = "".join(map(str, digits))
            if cand != number:
                candidates.setdefault(cand, "ML分布サンプリング(近傍探索)")

        scored = []
        for cand, reason in candidates.items():
            # 近すぎ/遠すぎのバランス：最大2桁違いを優先（ボックスは例外で通す）
            ham = hamming(number, cand)
            if ham > 2 and not is_same_box(number, cand):
                continue

            score = ml_logp(cand)
            score += float(np.log(sum_bonus_multiplier(cand)))
            # 近いほど少しだけ加点
            score -= 0.65 * ham
            # ボックス一致（並び替え）は“類似”としてボーナス
            if is_same_box(number, cand):
                score += 0.60

            scored.append((cand, reason, score))

        scored.sort(key=lambda x: x[2], reverse=True)

        # 重複除去して上位count件
        out = []
        seen = set([number])
        for cand, reason, score in scored:
            if cand in seen:
                continue
            seen.add(cand)
            out.append((cand, reason, score))
            if len(out) >= count:
                break
        return out

    d1, d2, d3, d4 = int(number[0]), int(number[1]), int(number[2]), int(number[3])
    similar_patterns = []
    
    # 統計分析用のデータがある場合
    if all_draws_df is not None and not all_draws_df.empty:
        # 直近30回のデータで分析
        recent_30 = all_draws_df.tail(30)
        
        # === 分析1: 各桁の変化傾向を分析 ===
        changes_d1, changes_d2, changes_d3, changes_d4 = [], [], [], []
        
        for i in range(1, len(recent_30)):
            prev = recent_30.iloc[i-1]
            curr = recent_30.iloc[i]
            changes_d1.append(curr['d1'] - prev['d1'])
            changes_d2.append(curr['d2'] - prev['d2'])
            changes_d3.append(curr['d3'] - prev['d3'])
            changes_d4.append(curr['d4'] - prev['d4'])
        
        from collections import Counter
        common_change_d1 = Counter(changes_d1).most_common(3)
        common_change_d2 = Counter(changes_d2).most_common(3)
        common_change_d3 = Counter(changes_d3).most_common(3)
        common_change_d4 = Counter(changes_d4).most_common(3)
        
        # === 戦略1: 統計的に頻出する変化パターン ===
        for change, freq in common_change_d1:
            if change != 0:
                new_d1 = d1 + change
                if 0 <= new_d1 <= 9:
                    num_str = f"{new_d1}{d2}{d3}{d4}"
                    score = freq * 10
                    similar_patterns.append((num_str, f"1桁目に頻出変化{change:+d} (出現{freq}回)", score))
        
        for change, freq in common_change_d4:
            if change != 0:
                new_d4 = d4 + change
                if 0 <= new_d4 <= 9:
                    num_str = f"{d1}{d2}{d3}{new_d4}"
                    score = freq * 10
                    similar_patterns.append((num_str, f"4桁目に頻出変化{change:+d} (出現{freq}回)", score))
        
        # === 分析2: 頻出数字への置き換え ===
        all_digits = []
        for _, row in recent_30.iterrows():
            all_digits.extend([row['d1'], row['d2'], row['d3'], row['d4']])
        
        digit_freq = Counter(all_digits)
        hot_digits = [d for d, _ in digit_freq.most_common(5)]
        
        for hot_digit in hot_digits[:3]:
            if hot_digit != d1:
                num_str = f"{hot_digit}{d2}{d3}{d4}"
                score = digit_freq[hot_digit] * 2
                similar_patterns.append((num_str, f"1桁目→頻出数字{hot_digit} (出現{digit_freq[hot_digit]}回)", score))
            
            if hot_digit != d4:
                num_str = f"{d1}{d2}{d3}{hot_digit}"
                score = digit_freq[hot_digit] * 2
                similar_patterns.append((num_str, f"4桁目→頻出数字{hot_digit} (出現{digit_freq[hot_digit]}回)", score))
    
    # === 基本パターン: 小さな変化（±1） ===
    basic_patterns = [
        (d1+1, d2, d3, d4, "1桁目+1", 5),
        (d1-1, d2, d3, d4, "1桁目-1", 5),
        (d1, d2, d3, d4+1, "4桁目+1", 5),
        (d1, d2, d3, d4-1, "4桁目-1", 5),
    ]
    
    for new_d1, new_d2, new_d3, new_d4, desc, score in basic_patterns:
        if 0 <= new_d1 <= 9 and 0 <= new_d2 <= 9 and 0 <= new_d3 <= 9 and 0 <= new_d4 <= 9:
            num_str = f"{new_d1}{new_d2}{new_d3}{new_d4}"
            similar_patterns.append((num_str, desc, score))
    
    # スコアでソートして重複除去
    seen = set()
    unique_patterns = []
    similar_patterns.sort(key=lambda x: -x[2])  # スコア降順
    
    for num, desc, score in similar_patterns:
        if num not in seen and num != number:
            seen.add(num)
            unique_patterns.append((num, desc, score))
            if len(unique_patterns) >= count:
                break
    
    return unique_patterns


def run_ensemble_prediction_cli():
    """アンサンブル予測を実行し、結果をCLIに表示する"""
    
    print("\n" + "="*60)
    print("ナンバーズ4 アンサンブル予測システム")
    print("="*60)
    
    # データを読み込む（類似パターン生成用）
    all_draws_df = load_all_draws()
    
    # 予測の実行（コールバックでコンソールに進捗表示）
    final_predictions_df, ensemble_weights = generate_ensemble_prediction(progress_callback=print)

    # --- DB保存結果の確認 ---
    print("\n" + "="*60)
    print("💾 データベース保存状況")
    print("="*60)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, target_draw_number, created_at, predictions_count
            FROM numbers4_ensemble_predictions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        
        if row:
            pred_id, target_draw, created_at, pred_count = row
            print(f"✅ 予測結果をDBに保存しました:")
            print(f"   - 予測ID: {pred_id}")
            print(f"   - 対象抽選回: 第{target_draw}回" if target_draw else "   - 対象抽選回: 未設定")
            print(f"   - 保存日時: {created_at}")
            print(f"   - 予測候補数: {pred_count}件")
        else:
            print("⚠️  予測結果が見つかりませんでした。")
    except Exception as e:
        print(f"⚠️  保存結果の確認中にエラーが発生しました: {e}")

    # --- 結果表示 ---
    print("\n" + "="*40)
    print("次回ナンバーズ4 最終予測")
    print("="*40)
    print(f"使用した重み: {ensemble_weights}")

    # 上位20件を表示
    top_20_predictions = final_predictions_df.head(20)

    print("\n--- 最終予測 (上位20件) ---")
    if top_20_predictions.empty:
        print("予測結果がありません。")
    else:
        for index, row in top_20_predictions.iterrows():
            box_type = row.get('box_type', '不明')
            box_coverage = row.get('box_coverage', 0)
            print(f"  {index+1:2d}位: {row['prediction']} (スコア: {row['score']:.1f}) [{box_type} / {box_coverage}通り]")

    print("\n" + "="*40)
    print("スコアが高いほど、複数のモデルが共通して予測した、あるいは実績のあるモデルが強く推奨した有望な番号です。")
    
    # === 新機能: 上位5件に対して類似パターンを提案 ===
    print("\n" + "="*80)
    print("💡 予測番号 + 類似パターン提案（もしかしたらこれも？）")
    print("="*80)
    
    top_5_predictions = final_predictions_df.head(5)
    
    for index, row in top_5_predictions.iterrows():
        print(f"\n【第{index+1}位】")
        print(f"  🎯 メイン予測: {row['prediction']}  (スコア: {row['score']:.2f})")
        
        # 統計分析に基づいて類似パターンを生成
        similar_patterns = generate_similar_patterns_n4(
            row['prediction'],
            count=10,
            all_draws_df=all_draws_df
        )
        
        if similar_patterns:
            for i, (similar_num, desc, score) in enumerate(similar_patterns, 1):
                print(f"    ↳ 類似{i}: {similar_num}  - {desc} (score={score:.3f})")
        else:
            print(f"    ↳ (類似パターンなし)")
    
    print("\n" + "="*80)
    print("💡 使い方:")
    print("  - メイン予測: アンサンブルモデルが最も推奨する番号")
    print("  - 類似1-3: 統計分析に基づく類似パターン（実際に起こりやすい変化）")
    print("    * 頻出する変化パターン（直近30回の傾向）")
    print("    * 頻出数字への置き換え（ホットナンバー）")
    print("  - 各順位のメイン予測 + 類似3つ = 計20通りの候補")
    print("="*80)

if __name__ == "__main__":
    run_ensemble_prediction_cli()

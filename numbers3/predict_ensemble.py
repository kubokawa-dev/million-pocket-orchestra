import psycopg2
import pandas as pd
import sys
import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# --- モジュール検索パスを追加 ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from numbers3.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_from_exploratory_heuristics,
    predict_with_ml_model,
    predict_from_extreme_patterns,
    predict_from_comprehensive_patterns,
    predict_from_permutation_coverage,
    predict_from_ultra_precision_recent_trend,  # 統計分析モデル
    predict_from_pattern_discovery,  # 法則発見モデル
    predict_from_enhanced_recent_analysis,  # 強化版統計モデル
    predict_from_enhanced_cycle_analysis,  # 強化版周期性モデル
    predict_from_digit_repetition_model,  # v10: 数字再出現モデル
    predict_from_digit_continuation_model,  # v10: 桁継続モデル
    predict_from_large_change_model,  # v10: 大変化モデル
    predict_from_realistic_frequency_model,  # v10: 現実的頻度モデル
    aggregate_predictions,
    apply_diversity_penalty
)
from numbers3.save_prediction_history import save_ensemble_prediction
from numbers3.online_learning import load_model_weights

# --- 設定（バランス型） ---
NUM_PREDICTIONS_BASIC = 10
NUM_PREDICTIONS_ADVANCED = 10
NUM_PREDICTIONS_ML = 15
NUM_PREDICTIONS_EXPLORATORY = 20
NUM_PREDICTIONS_EXTREME = 25
NUM_PREDICTIONS_COMPREHENSIVE = 30
NUM_PREDICTIONS_PERMUTATION = 100
NUM_PREDICTIONS_ULTRA_PRECISION = 300  # 統計分析モデル
NUM_PREDICTIONS_PATTERN_DISCOVERY = 300  # 法則発見モデル
NUM_PREDICTIONS_ENHANCED_RECENT = 400  # 強化版統計モデル
NUM_PREDICTIONS_ENHANCED_CYCLE = 250  # 強化版周期性モデル
NUM_PREDICTIONS_DIGIT_REPETITION = 300  # v10: 数字再出現モデル
NUM_PREDICTIONS_DIGIT_CONTINUATION = 250  # v10: 桁継続モデル
NUM_PREDICTIONS_LARGE_CHANGE = 200  # v10: 大変化モデル
NUM_PREDICTIONS_REALISTIC_FREQ = 400  # v10: 現実的頻度モデル


def get_db_connection():
    """データベース接続を取得する"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)


def load_all_draws():
    """データベースからすべての抽選データを読み込む"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date ASC", conn)
    conn.close()
    
    # numbersを各桁に分割する（Numbers3は3桁）
    df['d1'] = df['numbers'].str[0]
    df['d2'] = df['numbers'].str[1]
    df['d3'] = df['numbers'].str[2]

    # データ型を整数に変換
    for col in ['d1', 'd2', 'd3']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    for col in ['d1', 'd2', 'd3']:
        df[col] = df[col].astype(int)
        
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

    if all_draws_df.empty:
        return pd.DataFrame()

    report_progress(0.1, "各モデルで予測を生成しています...")
    
    # 1. 基本統計モデル
    predictions_basic = predict_from_basic_stats(all_draws_df, NUM_PREDICTIONS_BASIC)
    report_progress(0.4, f"- 基本統計モデル予測完了: {len(predictions_basic)}件")

    # 2. 高度なヒューリスティックモデル
    predictions_advanced = predict_from_advanced_heuristics(all_draws_df, NUM_PREDICTIONS_ADVANCED)
    report_progress(0.7, f"- 高度ヒューリスティックモデル予測完了: {len(predictions_advanced)}件")

    # 3. 機械学習モデル
    predictions_ml = predict_with_ml_model(all_draws_df, NUM_PREDICTIONS_ML)
    report_progress(0.6, f"- 機械学習モデル予測完了: {len(predictions_ml)}件")

    # 4. 探索的ヒューリスティックモデル
    predictions_exploratory = predict_from_exploratory_heuristics(all_draws_df, NUM_PREDICTIONS_EXPLORATORY)
    report_progress(0.75, f"- 探索的モデル予測完了: {len(predictions_exploratory)}件")

    # 5. 極端パターンモデル
    predictions_extreme = predict_from_extreme_patterns(all_draws_df, NUM_PREDICTIONS_EXTREME)
    report_progress(0.85, f"- 極端パターンモデル予測完了: {len(predictions_extreme)}件")

    # 6. 包括的パターンモデル（最強）
    predictions_comprehensive = predict_from_comprehensive_patterns(all_draws_df, NUM_PREDICTIONS_COMPREHENSIVE)
    report_progress(0.88, f"- 包括的パターンモデル予測完了: {len(predictions_comprehensive)}件")

    # 7. 順列完全網羅モデル（NEW: 究極）
    predictions_permutation = predict_from_permutation_coverage(all_draws_df, NUM_PREDICTIONS_PERMUTATION)
    report_progress(0.91, f"- 順列完全網羅モデル予測完了: {len(predictions_permutation)}件")

    # 8. 統計分析モデル
    predictions_ultra_precision = predict_from_ultra_precision_recent_trend(all_draws_df, NUM_PREDICTIONS_ULTRA_PRECISION)
    report_progress(0.91, f"- 統計分析モデル予測完了: {len(predictions_ultra_precision)}件")

    # 9. 法則発見モデル（NEW）
    predictions_pattern_discovery = predict_from_pattern_discovery(all_draws_df, NUM_PREDICTIONS_PATTERN_DISCOVERY)
    report_progress(0.91, f"- 法則発見モデル予測完了: {len(predictions_pattern_discovery)}件")

    # 10. 強化版統計モデル（第6844回向け最適化）
    predictions_enhanced_recent = predict_from_enhanced_recent_analysis(all_draws_df, NUM_PREDICTIONS_ENHANCED_RECENT)
    report_progress(0.93, f"- 強化版統計モデル予測完了: {len(predictions_enhanced_recent)}件")

    # 11. 強化版周期性モデル
    predictions_enhanced_cycle = predict_from_enhanced_cycle_analysis(all_draws_df, NUM_PREDICTIONS_ENHANCED_CYCLE)
    report_progress(0.88, f"- 強化版周期性モデル予測完了: {len(predictions_enhanced_cycle)}件")

    # 12. 数字再出現モデル（v10）
    predictions_digit_repetition = predict_from_digit_repetition_model(all_draws_df, NUM_PREDICTIONS_DIGIT_REPETITION)
    report_progress(0.90, f"- 数字再出現モデル予測完了: {len(predictions_digit_repetition)}件")

    # 13. 桁継続モデル（v10）
    predictions_digit_continuation = predict_from_digit_continuation_model(all_draws_df, NUM_PREDICTIONS_DIGIT_CONTINUATION)
    report_progress(0.92, f"- 桁継続モデル予測完了: {len(predictions_digit_continuation)}件")

    # 14. 大変化モデル（v10）
    predictions_large_change = predict_from_large_change_model(all_draws_df, NUM_PREDICTIONS_LARGE_CHANGE)
    report_progress(0.93, f"- 大変化モデル予測完了: {len(predictions_large_change)}件")

    # 15. 現実的頻度モデル（v10）
    predictions_realistic_freq = predict_from_realistic_frequency_model(all_draws_df, NUM_PREDICTIONS_REALISTIC_FREQ)
    report_progress(0.94, f"- 現実的頻度モデル予測完了: {len(predictions_realistic_freq)}件")

    # --- アンサンブル集計 ---
    report_progress(0.95, "全モデルの予測を統合・集計中...")
    
    # 【改良版】オンライン学習で調整された重みを使用
    try:
        ensemble_weights = load_model_weights()
        report_progress(0.96, "✅ オンライン学習済みの重みを読み込みました")
    except Exception as e:
        # 読み込み失敗時はデフォルト重みを使用
        ensemble_weights = {
            # v10.0 最優先モデル（根本的改善）
            'digit_repetition': 30.0,              # 数字再出現（656のような同じ数字が複数回）- 最重要
            'digit_continuation': 25.0,            # 桁継続（前回の数字が次回も出現）- 超重要
            'realistic_frequency': 20.0,           # 現実的頻度（過去当選番号も含む）- 重要
            
            # 変化パターンモデル
            'large_change': 15.0,                  # 大変化（±3-5の変化）
            'enhanced_recent_analysis': 12.0,      # 強化版統計（直近重視）
            
            # 従来モデル（中重み）
            'ultra_precision_recent_trend': 8.0,   # 統計分析
            'pattern_discovery': 6.0,              # 法則発見
            'enhanced_cycle_analysis': 5.0,        # 強化版周期性
            
            # 補助モデル（低重み）
            'comprehensive_patterns': 2.0,         # 包括的パターン
            'permutation_coverage': 2.0,           # 順列網羅
            'ml_model': 1.0,                       # 機械学習
            'exploratory': 1.0,                    # 探索的分析
        }
        report_progress(0.96, f"⚠️ デフォルト重みを使用: {e}")
    
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model': predictions_ml,
        'exploratory': predictions_exploratory,
        'extreme_patterns': predictions_extreme,
        'comprehensive_patterns': predictions_comprehensive,
        'permutation_coverage': predictions_permutation,
        'ultra_precision_recent_trend': predictions_ultra_precision,
        'pattern_discovery': predictions_pattern_discovery,
        'enhanced_recent_analysis': predictions_enhanced_recent,
        'enhanced_cycle_analysis': predictions_enhanced_cycle,
        'digit_repetition': predictions_digit_repetition,  # v10: 数字再出現
        'digit_continuation': predictions_digit_continuation,  # v10: 桁継続
        'large_change': predictions_large_change,  # v10: 大変化
        'realistic_frequency': predictions_realistic_freq  # v10: 現実的頻度
    }

    # 重み付けして集計（スコア正規化を有効化）
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights, normalize_scores=True)
    
    # 多様性ペナルティを適用（類似した候補のスコアを下げる）
    final_predictions_df = apply_diversity_penalty(final_predictions_df, penalty_strength=0.2, similarity_threshold=2)
    
    # ソート（モデルのスコアのみで順位決定）
    final_predictions_df = final_predictions_df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    report_progress(1.0, "予測完了！")
    
    # 予測履歴をデータベースに保存
    try:
        save_ensemble_prediction(
            predictions_df=final_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model=predictions_by_model,
            model_state=None,
            notes="Optimized Ensemble v10.0 (根本的改善版): 15 models with realistic patterns. 【重要な変更】過去当選番号除外を廃止、数字再出現と桁継続を最優先。Core models: (1) Digit Repetition (weight=30.0) - 同じ数字が複数回出現, (2) Digit Continuation (weight=25.0) - 前回の数字が継続, (3) Realistic Frequency (weight=20.0) - 過去当選番号も含む, (4) Large Change (weight=15.0) - 大きな変化, (5) Enhanced Recent (weight=12.0). Features: 第6843回(631)→第6844回(656)のパターン学習済み, 同じ数字の複数出現対応, 桁継続パターン対応, 大変化対応."
        )
    except Exception as e:
        print(f"⚠️  予測履歴の保存に失敗しました: {e}")
    
    return final_predictions_df, ensemble_weights


def run_ensemble_prediction_cli():
    """アンサンブル予測を実行し、結果をCLIに表示する"""
    
    print("\n" + "="*60)
    print("🎯 ナンバーズ3 アンサンブル予測システム")
    print("="*60)
    
    # 予測の実行（コールバックでコンソールに進捗表示）
    final_predictions_df, ensemble_weights = generate_ensemble_prediction(progress_callback=print)

    # --- 結果表示 ---
    print("\n" + "="*40)
    print("👑 次回ナンバーズ3 最終予測 👑")
    print("="*40)
    print(f"使用した重み: {ensemble_weights}")

    # 上位20件を表示
    top_20_predictions = final_predictions_df.head(20)

    print("\n--- 最終予測 (上位20件) ---")
    if top_20_predictions.empty:
        print("予測結果がありません。")
    else:
        for index, row in top_20_predictions.iterrows():
            print(f"  {index+1:2d}位: {row['prediction']} (スコア: {row['score']:.1f})")

    print("\n" + "="*40)
    print("スコアが高いほど、複数のモデルが共通して予測した、あるいは実績のあるモデルが強く推奨した有望な番号です。")


if __name__ == "__main__":
    run_ensemble_prediction_cli()

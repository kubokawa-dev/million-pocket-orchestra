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
    predict_from_pattern_discovery,  # NEW: 法則発見モデル
    aggregate_predictions
)
from numbers3.save_prediction_history import save_ensemble_prediction

# --- 設定（バランス型） ---
NUM_PREDICTIONS_BASIC = 10
NUM_PREDICTIONS_ADVANCED = 10
NUM_PREDICTIONS_ML = 15
NUM_PREDICTIONS_EXPLORATORY = 20
NUM_PREDICTIONS_EXTREME = 25
NUM_PREDICTIONS_COMPREHENSIVE = 30
NUM_PREDICTIONS_PERMUTATION = 100
NUM_PREDICTIONS_ULTRA_PRECISION = 300  # 統計分析モデル
NUM_PREDICTIONS_PATTERN_DISCOVERY = 300  # NEW: 法則発見モデル


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
    report_progress(0.94, f"- 法則発見モデル予測完了: {len(predictions_pattern_discovery)}件")

    # --- アンサンブル集計 ---
    report_progress(0.95, "全モデルの予測を統合・集計中...")
    
    ensemble_weights = {
        'basic_stats': 0.5,               # 基本統計
        'advanced_heuristics': 0.8,       # 高度な統計
        'ml_model': 0.6,                  # 機械学習
        'exploratory': 0.7,               # 探索的分析
        'extreme_patterns': 0.9,          # 極端パターン
        'comprehensive_patterns': 1.2,    # 包括的パターン
        'permutation_coverage': 3.0,      # 順列網羅
        'ultra_precision_recent_trend': 12.0,  # 統計分析（各桁頻度、合計値分布）
        'pattern_discovery': 10.0,        # 法則発見（周期性、移動傾向、飛び石パターン）
    }
    
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model': predictions_ml,
        'exploratory': predictions_exploratory,
        'extreme_patterns': predictions_extreme,
        'comprehensive_patterns': predictions_comprehensive,
        'permutation_coverage': predictions_permutation,
        'ultra_precision_recent_trend': predictions_ultra_precision,  # 統計分析
        'pattern_discovery': predictions_pattern_discovery  # NEW: 法則発見
    }

    # 重み付けして集計（純粋な統計分析のみ、ボーナスなし）
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights)
    
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
            notes="Balanced Ensemble v7.0: 9 models combining statistics and pattern discovery. Statistical model (weight=12.0): digit freq by position, sum distribution. Pattern discovery model (weight=10.0): cycles, movement trends, skip patterns, digit correlation, sum trends. No direct bonus for past winning numbers."
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

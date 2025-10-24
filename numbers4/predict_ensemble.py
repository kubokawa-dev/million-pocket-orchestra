import psycopg2
import pandas as pd
import sys
import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# --- モジュール検索パスを追加 ---
# スクリプトの親ディレクトリ（numbers4）の親ディレクトリ（million-pocket）をパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_new_ml_model,  # 古いpredict_with_modelを新しいものに置き換え
    predict_from_exploratory_heuristics,
    predict_from_extreme_patterns,  # 新しい極端パターンモデル
    aggregate_predictions
)
from numbers4.save_prediction_history import save_ensemble_prediction
# learn_model_from_data は不要になったので削除

# --- 設定 ---
NUM_PREDICTIONS_BASIC = 5
NUM_PREDICTIONS_ADVANCED = 5
NUM_PREDICTIONS_ML_NEW = 15  # 新しいMLモデルの予測数を増やす
NUM_PREDICTIONS_EXPLORATORY = 20  # 改善: 5→20に増加
NUM_PREDICTIONS_EXTREME = 15  # 新規: 極端パターンモデル (10→15に増加)


def get_db_connection():
    """データベース接続を取得する"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

def load_all_draws():
    """データベースからすべての抽選データを読み込む"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers4_draws ORDER BY draw_date ASC", conn)
    conn.close()
    
    # numbersを各桁に分割する
    df['d1'] = df['numbers'].str[0]
    df['d2'] = df['numbers'].str[1]
    df['d3'] = df['numbers'].str[2]
    df['d4'] = df['numbers'].str[3]

    # データ型を整数に変換
    for col in ['d1', 'd2', 'd3', 'd4']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    for col in ['d1', 'd2', 'd3', 'd4']:
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
                    report_progress(0.05, f"⚠️ 警告: モデルが{age_hours:.1f}時間前に更新（学習イベント{events}回）。learn_from_predictions.pyの実行を推奨。")
            except:
                pass

    report_progress(0.1, "各モデルで予測を生成しています...")
    
    # 1. 基本統計モデル
    predictions_basic = predict_from_basic_stats(all_draws_df, NUM_PREDICTIONS_BASIC)
    report_progress(0.3, f"- 基本統計モデル予測完了: {len(predictions_basic)}件")

    # 2. 高度なヒューリスティックモデル
    predictions_advanced = predict_from_advanced_heuristics(all_draws_df, NUM_PREDICTIONS_ADVANCED)
    report_progress(0.45, f"- 高度ヒューリスティックモデル予測完了: {len(predictions_advanced)}件")

    # 3. 新しい機械学習モデル (学習済みモデルを使用)
    report_progress(0.5, "- 新しいMLモデルで予測中...")
    predictions_ml_new = predict_with_new_ml_model(all_draws_df, limit=NUM_PREDICTIONS_ML_NEW)
    report_progress(0.65, f"- 新MLモデル予測完了: {len(predictions_ml_new)}件")

    # 4. 探索的ヒューリスティックモデル
    predictions_exploratory = predict_from_exploratory_heuristics(all_draws_df, NUM_PREDICTIONS_EXPLORATORY)
    report_progress(0.75, f"- 探索的モデル予測完了: {len(predictions_exploratory)}件")

    # 5. 極端パターンモデル（新規追加）
    report_progress(0.8, "- 極端パターンモデルで予測中...")
    predictions_extreme = predict_from_extreme_patterns(all_draws_df, NUM_PREDICTIONS_EXTREME)
    report_progress(0.85, f"- 極端パターンモデル予測完了: {len(predictions_extreme)}件")

    # --- アンサンブル集計 ---
    report_progress(0.9, "全モデルの予測を統合・集計中...")
    
    # 動的重み調整：最新データへの適応性を重視
    # 改善版：探索的モデルと極端パターンモデルの重みを増加
    ensemble_weights = {
        'basic_stats': 1.2,  # 時系列重み付けで最新データに適応
        'advanced_heuristics': 1.5,  # トレンド重視の改善版
        'ml_model_new': 1.0,  # 学習データが古い場合は控えめに
        'exploratory': 1.3,  # 改善: 0.9→1.3 極端パターンへの対応強化
        'extreme_patterns': 1.2,  # 新規: 極端パターン専用モデル
    }
    
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model_new': predictions_ml_new,
        'exploratory': predictions_exploratory,
        'extreme_patterns': predictions_extreme  # 新規追加
    }

    # 重み付けして集計
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights)
    report_progress(1.0, "予測完了！")
    
    # 予測履歴をデータベースに保存
    try:
        # モデル状態を読み込み
        model_state = None
        if os.path.exists(model_path):
            import json
            with open(model_path, 'r') as f:
                model_state = json.load(f)
        
        # 履歴を保存
        save_ensemble_prediction(
            predictions_df=final_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model=predictions_by_model,
            model_state=model_state,
            notes="Enhanced ensemble: added extreme_patterns model, increased exploratory coverage (v2.0)"
        )
    except Exception as e:
        # 履歴保存に失敗しても予測結果は返す
        print(f"⚠️  予測履歴の保存に失敗しました: {e}")
    
    return final_predictions_df, ensemble_weights


def run_ensemble_prediction_cli():
    """アンサンブル予測を実行し、結果をCLIに表示する"""
    
    print("\n" + "="*60)
    print("🎯 ナンバーズ4 アンサンブル予測システム")
    print("="*60)
    
    # 予測の実行（コールバックでコンソールに進捗表示）
    final_predictions_df, ensemble_weights = generate_ensemble_prediction(progress_callback=print)

    # --- 結果表示 ---
    print("\n" + "="*40)
    print("👑 次回ナンバーズ4 最終予測 👑")
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

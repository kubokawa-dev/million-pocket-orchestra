import psycopg2
import pandas as pd
import sys
import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# プロジェクトルートをパスに追加
# __file__ はこのスクリプト自身のパスを指す
# os.path.abspath(__file__) で絶対パスに変換
# os.path.dirname() で親ディレクトリを取得
# これを2回繰り返すことで、'numbers4'の一つ上の'million-pocket'のパスが得られる
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model,
    predict_from_exploratory_heuristics,
    aggregate_predictions
)
from numbers4.learning_logic import learn_model_from_data

# --- 設定 ---
MODEL_STATE_PATH = 'numbers4/model_state.json' # predict_with_modelのフォールバック用
NUM_PREDICTIONS_BASIC = 5
NUM_PREDICTIONS_ADVANCED = 5
NUM_PREDICTIONS_MODEL = 10 # 少し減らして多様性モデルの枠を作る
NUM_PREDICTIONS_EXPLORATORY = 5 # 新しい探索的モデルの予測数


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

    report_progress(0.1, "各モデルで予測を生成しています...")
    
    # 1. 基本統計モデル
    predictions_basic = predict_from_basic_stats(all_draws_df, NUM_PREDICTIONS_BASIC)
    report_progress(0.3, f"- 基本統計モデル予測完了: {len(predictions_basic)}件")

    # 2. 高度なヒューリスティックモデル
    predictions_advanced = predict_from_advanced_heuristics(all_draws_df, NUM_PREDICTIONS_ADVANCED)
    report_progress(0.45, f"- 高度ヒューリスティックモデル予測完了: {len(predictions_advanced)}件")

    # 3. 機械学習モデル (毎回再学習)
    report_progress(0.5, "- 機械学習モデルを再学習中...")
    relearned_weights = learn_model_from_data(all_draws_df)
    predictions_model = predict_with_model(relearned_weights, limit=NUM_PREDICTIONS_MODEL)
    report_progress(0.65, f"- 機械学習モデル予測完了: {len(predictions_model)}件")

    # 4. 探索的ヒューリスティックモデル
    predictions_exploratory = predict_from_exploratory_heuristics(all_draws_df, NUM_PREDICTIONS_EXPLORATORY)
    report_progress(0.8, f"- 探索的モデル予測完了: {len(predictions_exploratory)}件")

    # --- アンサンブル集計 ---
    report_progress(0.9, "全モデルの予測を統合・集計中...")
    ensemble_weights = {
        'basic_stats': 1.5,
        'advanced_heuristics': 1.0,
        'ml_model': 1.0,
        'exploratory': 1.5, 
    }
    
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model': predictions_model,
        'exploratory': predictions_exploratory
    }

    # 重み付けして集計
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights)
    report_progress(1.0, "予測完了！")
    
    return final_predictions_df, ensemble_weights


def run_ensemble_prediction_cli():
    """アンサンブル予測を実行し、結果をCLIに表示する"""
    
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

import sqlite3
import pandas as pd
import sys
import os
from collections import Counter

# プロジェクトルートをパスに追加
# __file__ はこのスクリプト自身のパスを指す
# os.path.abspath(__file__) で絶対パスに変換
# os.path.dirname() で親ディレクトリを取得
# これを2回繰り返すことで、'numbers4'の一つ上の'million-pocket'のパスが得られる
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model
)
from numbers4.learning_logic import learn_model_from_data

# --- 設定 ---
DB_PATH = 'millions.sqlite'
MODEL_STATE_PATH = 'numbers4/model_state.json' # predict_with_modelのフォールバック用
NUM_PREDICTIONS_BASIC = 5
NUM_PREDICTIONS_ADVANCED = 5
NUM_PREDICTIONS_MODEL = 12

def get_db_connection():
    """データベース接続を取得する"""
    # スクリプトがどこから実行されてもいいように、DBパスを絶対パスに変換
    db_abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_PATH)
    return sqlite3.connect(db_abs_path)

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

def run_ensemble_prediction():
    """アンサンブル予測を実行し、結果を表示する"""
    print("データベースから全抽選データを読み込んでいます...")
    all_draws_df = load_all_draws()

    if all_draws_df.empty:
        print("エラー: データベースにデータがありません。")
        return

    print("各モデルで予測を生成しています...")
    
    # 1. 基本統計モデル
    predictions_basic = predict_from_basic_stats(all_draws_df, NUM_PREDICTIONS_BASIC)
    print(f"- 基本統計モデル予測: {predictions_basic}")

    # 2. 高度なヒューリスティックモデル
    predictions_advanced = predict_from_advanced_heuristics(all_draws_df, NUM_PREDICTIONS_ADVANCED)
    print(f"- 高度ヒューリスティックモデル予測: {predictions_advanced}")

    # 3. 機械学習モデル (毎回再学習)
    print("- 機械学習モデルを再学習中...")
    relearned_weights = learn_model_from_data(all_draws_df)
    predictions_model = predict_with_model(all_draws_df, model_weights=relearned_weights, num_predictions=NUM_PREDICTIONS_MODEL)
    print(f"- 機械学習モデル予測: {predictions_model}")

    # --- アンサンブル集計 ---
    all_predictions = predictions_basic + predictions_advanced + predictions_model
    
    # ストレートのスコアリング
    straight_scores = Counter(all_predictions)
    
    # ボックスのスコアリング
    box_predictions = ["".join(sorted(p)) for p in all_predictions]
    box_scores = Counter(box_predictions)

    # --- 結果表示 ---
    print("\n" + "="*40)
    print("👑 アンサンブル予測結果 👑")
    print("="*40)

    # ストレート結果
    print("\n--- ストレート予測 (推奨度順) ---")
    sorted_straight = sorted(straight_scores.items(), key=lambda item: item[1], reverse=True)
    if not sorted_straight:
        print("予測結果がありません。")
    else:
        max_score = sorted_straight[0][1]
        for score in range(max_score, 0, -1):
            numbers_with_score = [num for num, s in sorted_straight if s == score]
            if numbers_with_score:
                print(f"\n[推奨度: {score} (/{len(all_predictions)}回中)]")
                print(f"  👉 {', '.join(numbers_with_score)}")

    # ボックス結果
    print("\n--- ボックス予測 (推奨度順) ---")
    sorted_box = sorted(box_scores.items(), key=lambda item: item[1], reverse=True)
    if not sorted_box:
        print("予測結果がありません。")
    else:
        max_score = sorted_box[0][1]
        for score in range(max_score, 0, -1):
            combinations_with_score = [comb for comb, s in sorted_box if s == score]
            if combinations_with_score:
                print(f"\n[推奨度: {score} (/{len(all_predictions)}回中)]")
                # 組み合わせを見やすくフォーマット
                formatted_combs = [f"[{','.join(list(c))}]" for c in combinations_with_score]
                print(f"  👉 {', '.join(formatted_combs)}")
    
    print("\n" + "="*40)
    print("推奨度が高いほど、複数のモデルが共通して予測した有望な番号です。")

if __name__ == "__main__":
    run_ensemble_prediction()

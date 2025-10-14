import sqlite3
import pandas as pd
import sys
import os
from tqdm import tqdm

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model
)

# --- 設定 ---
DB_PATH = 'millions.sqlite'
MODEL_STATE_PATH = 'numbers4/model_state.json'
BACKTEST_PERIOD = 50  # 直近何回分のデータでバックテストを行うか
NUM_PREDICTIONS_BASIC = 5
NUM_PREDICTIONS_ADVANCED = 5
NUM_PREDICTIONS_MODEL = 12

def get_db_connection():
    """データベース接続を取得する"""
    return sqlite3.connect(DB_PATH)

def load_all_draws():
    """データベースからすべての抽選データを読み込む"""
    conn = get_db_connection()
    # winning_numbers を numbers に修正
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

def check_hit(prediction: str, actual: str):
    """
    予測が当選番号と一致するかをチェックする
    :param prediction: 予測番号 (e.g., "1234")
    :param actual: 当選番号 (e.g., "4321")
    :return: "straight", "box", or None
    """
    if prediction == actual:
        return "straight"
    if sorted(prediction) == sorted(actual):
        return "box"
    return None

def run_backtest():
    """バックテストを実行し、各モデルの性能を評価する"""
    print("データベースから全抽選データを読み込んでいます...")
    all_draws_df = load_all_draws()
    
    if len(all_draws_df) < BACKTEST_PERIOD + 1:
        print(f"エラー: バックテストに必要なデータが不足しています。少なくとも {BACKTEST_PERIOD + 1} 回分のデータが必要です。")
        return

    print(f"直近 {BACKTEST_PERIOD} 回分のデータでバックテストを開始します...")

    results = {
        "basic_stats": {"straight": 0, "box": 0},
        "advanced_heuristics": {"straight": 0, "box": 0},
        "ml_model": {"straight": 0, "box": 0},
    }

    # バックテスト期間をループ
    for i in tqdm(range(len(all_draws_df) - BACKTEST_PERIOD, len(all_draws_df))):
        train_df = all_draws_df.iloc[:i]
        actual_draw = all_draws_df.iloc[i]
        actual_number = "".join(map(str, actual_draw[['d1', 'd2', 'd3', 'd4']].values))

        # 1. 基本統計モデル
        predictions_basic = predict_from_basic_stats(train_df, NUM_PREDICTIONS_BASIC)
        for pred in predictions_basic:
            hit_type = check_hit(pred, actual_number)
            if hit_type:
                results["basic_stats"][hit_type] += 1

        # 2. 高度なヒューリスティックモデル
        predictions_advanced = predict_from_advanced_heuristics(train_df, NUM_PREDICTIONS_ADVANCED)
        for pred in predictions_advanced:
            hit_type = check_hit(pred, actual_number)
            if hit_type:
                results["advanced_heuristics"][hit_type] += 1

        # 3. 機械学習モデル
        # 注意: このバックテストでは、毎回モデルの状態を読み込むだけです。
        # 本来は、この時点のデータでモデルを再学習する `learn_from_predictions.py` のロジックを
        # ここで実行するのが理想的ですが、今回は簡略化のため既存のモデル状態を使います。
        predictions_model = predict_with_model(train_df, MODEL_STATE_PATH, NUM_PREDICTIONS_MODEL)
        for pred in predictions_model:
            hit_type = check_hit(pred, actual_number)
            if hit_type:
                results["ml_model"][hit_type] += 1

    # --- 結果の表示 ---
    print("\n--- バックテスト結果 ---")
    print(f"対象期間: {all_draws_df.iloc[len(all_draws_df) - BACKTEST_PERIOD]['draw_date']} から {all_draws_df.iloc[-1]['draw_date']} まで")
    print(f"対象回数: {BACKTEST_PERIOD} 回\n")

    print("モデル別の的中回数:")
    for model_name, hits in results.items():
        print(f"  - {model_name}:")
        print(f"    - ストレート: {hits['straight']} 回")
        print(f"    - ボックス  : {hits['box']} 回")
    
    print("\n--- 分析 ---")
    print("この結果は、各モデルが過去のデータに対してどれだけ有効だったかを示します。")
    print("的中回数が多いモデルは、より信頼性が高いと考えることができます。")
    print("注意: 機械学習モデルは、バックテストの度に再学習を行っていないため、他のモデルより不利な条件での評価となっています。")

if __name__ == "__main__":
    run_backtest()

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
    aggregate_predictions,
    apply_diversity_penalty  # NEW: 多様性ペナルティ
)
from numbers4.save_prediction_history import save_ensemble_prediction
from numbers4.online_learning import load_model_weights
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
                    report_progress(0.05, f"警告: モデルが{age_hours:.1f}時間前に更新（学習イベント{events}回）。learn_from_predictions.pyの実行を推奨。")
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
    
    # 【改良版v3.0】オンライン学習で調整された重みを使用
    try:
        ensemble_weights = load_model_weights()
        report_progress(0.92, "オンライン学習済みの重みを読み込みました")
    except Exception as e:
        # 読み込み失敗時はデフォルト重みを使用
        ensemble_weights = {
            # コアモデル（高重み）
            'advanced_heuristics': 10.0,  # 統計分析（合計値、偶奇、ペア頻度）- 最重要
            'exploratory': 8.0,            # 探索的分析（コールドナンバー、未出現ペア）- 重要
            
            # 補助モデル（中重み）
            'extreme_patterns': 3.0,       # 極端パターン（超低/超高合計値）
            'basic_stats': 2.0,            # 基本統計（頻度分析）
            
            # 多様性確保モデル（低重み）
            'ml_model_new': 1.0,           # 機械学習
        }
        report_progress(0.92, f"デフォルト重みを使用: {e}")
    
    predictions_by_model = {
        'basic_stats': predictions_basic,
        'advanced_heuristics': predictions_advanced,
        'ml_model_new': predictions_ml_new,
        'exploratory': predictions_exploratory,
        'extreme_patterns': predictions_extreme
    }

    # 重み付けして集計（スコア正規化を有効化）
    final_predictions_df = aggregate_predictions(predictions_by_model, ensemble_weights, normalize_scores=True)
    
    # 多様性ペナルティを適用（類似した候補のスコアを下げる）
    final_predictions_df = apply_diversity_penalty(final_predictions_df, penalty_strength=0.2, similarity_threshold=3)
    
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
            notes="Optimized Ensemble v3.0: 5 core models with score normalization and diversity penalty. Models: (1) Advanced Heuristics (weight=10.0), (2) Exploratory (weight=8.0), (3) Extreme Patterns (weight=3.0), (4) Basic Stats (weight=2.0), (5) ML Model (weight=1.0). Features: rank-based score normalization, diversity penalty (strength=0.2, threshold=3)."
        )
    except Exception as e:
        # 履歴保存に失敗しても予測結果は返す
        print(f"予測履歴の保存に失敗しました: {e}")
    
    return final_predictions_df, ensemble_weights


def generate_similar_patterns_n4(number: str, count: int = 3, all_draws_df=None):
    """
    統計分析に基づいて、指定された4桁の番号に対して類似パターンを生成（ナンバーズ4版）
    
    過去の当選データを分析し、実際に起こりやすいパターンを提案
    
    Args:
        number: 4桁の番号（例: "1234"）
        count: 生成する類似パターンの数
        all_draws_df: 全抽選データのDataFrame（統計分析用）
    
    Returns:
        [(番号, 説明), ...] のリスト
    """
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
            unique_patterns.append((num, desc))
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
            print(f"  {index+1:2d}位: {row['prediction']} (スコア: {row['score']:.1f})")

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
        similar_patterns = generate_similar_patterns_n4(row['prediction'], count=3, all_draws_df=all_draws_df)
        
        if similar_patterns:
            for i, (similar_num, desc) in enumerate(similar_patterns, 1):
                print(f"    ↳ 類似{i}: {similar_num}  - {desc}")
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

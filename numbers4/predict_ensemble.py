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
    # v10.3 過去パターン学習モデル
    predict_from_transition_probability_n4,   # 遷移確率モデル
    predict_from_global_frequency_n4,         # 全体頻度モデル
    predict_from_box_pattern_analysis_n4,     # ボックスパターン分析 v10.5
    # v10.5 ボックス特化型モデル
    predict_from_hot_pair_combination_n4,     # ホットペア組み合わせ
    predict_from_digit_frequency_box_n4,      # 数字頻度ボックス
    aggregate_predictions,
    apply_diversity_penalty
)
from numbers4.save_prediction_history import save_ensemble_prediction
from numbers4.save_prediction_json import save_prediction_to_json
from numbers4.online_learning import load_model_weights
# learn_model_from_data は不要になったので削除

# --- 合計値ボーナス設定 ---
# 理論的な平均値: 4桁 x 4.5 = 18
# 標準偏差: 約5.7
# 実データ分析より、合計値15-24が約50%を占める
SUM_IDEAL = 18  # 理想的な合計値
SUM_TOLERANCE = 6  # 許容範囲（±6で12-24をカバー）
SUM_BONUS_MAX = 0.3  # 最大ボーナス（30%）


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
    predictions_lgbm = predict_from_lightgbm(all_draws_df, limit=20)
    report_progress(0.84, f"- [ML] LightGBMモデル完了: {len(predictions_lgbm)}件")

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

    # --- アンサンブル集計 ---
    report_progress(0.96, "全モデルの予測を統合・集計中...")
    
    ensemble_weights = {
        # v10.5 ボックス/セット特化モデル（最重要！）
        'hot_pair': 35.0,                 # ホットペア組み合わせ（NEW!）
        'box_pattern': 30.0,              # ボックスパターン分析 v10.5（18→30に強化）
        'digit_freq_box': 25.0,           # 数字頻度ボックス（NEW!）
        
        # v10.3 過去パターン学習モデル
        'transition_probability': 20.0,   # 遷移確率（25→20に調整）
        'global_frequency': 15.0,         # 全体頻度（20→15に調整）
        
        # v10.0 モデル（直近依存 - 低重み）
        'digit_repetition': 8.0,          # 数字再出現（12→8に調整）
        'digit_continuation': 6.0,        # 桁継続（10→6に調整）
        'realistic_frequency': 8.0,       # 現実的頻度（12→8に調整）
        
        # 変化パターンモデル
        'large_change': 10.0,             # 大変化（15→10に調整）
        
        # 多様性モデル（低重み）
        'advanced_heuristics': 5.0,       # 統計分析（10→5に調整）
        'exploratory': 8.0,               # 探索的分析（15→8に調整）
        'extreme_patterns': 3.0,          # 極端パターン（8→3に調整）
        
        # 補助モデル（最低重み）
        'basic_stats': 1.0,               # 基本統計
        'ml_model_new': 1.0,              # 機械学習
        'lightgbm': 20.0,                 # LightGBM（25→20に調整）
    }
    
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
        # v10.5 ボックス特化モデル（NEW!）
        'box_pattern': predictions_box_pattern,
        'hot_pair': predictions_hot_pair,
        'digit_freq_box': predictions_digit_freq_box,
        # ML
        'lightgbm': predictions_lgbm
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
            predictions_df=final_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model=predictions_by_model,
            model_state=model_state,
            notes="v10.1 Update: Temperature Scaling (LightGBM確率平滑化) + 合計値ボーナス (sum=18付近を優遇) + 多様性ペナルティ強化"
        )
        print(f"✅ 予測履歴の保存が完了しました (ID: {prediction_id})")
        
        # JSONにも保存（GitHub Actions用：リポジトリにコミットして蓄積）
        from numbers4.save_prediction_history import get_latest_draw_info
        conn = get_db_connection()
        latest_draw = get_latest_draw_info(conn)
        conn.close()
        target_draw = latest_draw['draw_number'] + 1 if latest_draw else None
        
        if target_draw:
            # 上位5件の類似パターンを生成
            similar_patterns_dict = {}
            for _, row in final_predictions_df.head(5).iterrows():
                number = str(row['prediction'])
                patterns = generate_similar_patterns_n4(number, count=3, all_draws_df=all_draws_df)
                if patterns:
                    similar_patterns_dict[number] = [
                        {'number': p[0], 'description': p[1]}
                        for p in patterns
                    ]
            
            save_prediction_to_json(
                predictions_df=final_predictions_df,
                ensemble_weights=ensemble_weights,
                target_draw_number=target_draw,
                similar_patterns=similar_patterns_dict
            )
    except Exception as e:
        # 履歴保存に失敗しても予測結果は返す
        import traceback
        print(f"❌ 予測履歴の保存に失敗しました: {e}")
        print(f"   詳細: {traceback.format_exc()}")
    
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

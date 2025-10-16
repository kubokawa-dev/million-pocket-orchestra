import os
import sys
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.utils import load_all_numbers4_draws
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_model,
    predict_from_exploratory_heuristics,
    aggregate_predictions
)
from numbers4.learning_logic import learn_model_from_data

def run_backtest(start_date, end_date, prediction_limit=50, final_prediction_count=5):
    """
    指定された期間でバックテストを実行し、モデルのパフォーマンスを評価します。

    Args:
        start_date (datetime): バックテストを開始する日付。
        end_date (datetime): バックテストを終了する日付。
        prediction_limit (int): 各モデルが生成する予測の数。

    Returns:
        dict: バックテストの結果サマリー。
    """
    print("すべての抽選データをロード中...")
    all_draws_df = load_all_numbers4_draws()
    all_draws_df['date'] = pd.to_datetime(all_draws_df['date'], errors='coerce')
    print(f"ロード完了。合計 {len(all_draws_df)} 件のデータ。")

    # バックテスト対象期間のデータをフィルタリング
    target_draws = all_draws_df[(all_draws_df['date'] >= start_date) & (all_draws_df['date'] <= end_date)].copy()
    
    if target_draws.empty:
        print("指定された期間にバックテスト対象のデータがありません。")
        return None

    print(f"{start_date.date()} から {end_date.date()} までの {len(target_draws)} 回の抽選でバックテストを実行します。")

    # --- アンサンブルの重み設定 ---
    # バックテスト結果に基づき、貢献度の高かったモデルの重みを上げる
    ensemble_weights = {
        'basic_stats': 1.5,
        'advanced_heuristics': 1.0,
        'ml_model': 1.0,
        'exploratory': 1.5, 
    }
    print(f"アンサンブル重み: {ensemble_weights}")

    results = {
        'total_draws': len(target_draws),
        'straight_hits': 0,
        'box_hits': 0,
        'set_straight_hits': 0,
        'set_box_hits': 0,
        'ensemble_hit_details': [],
        'model_performance': {
            'basic_stats': {'straight': 0, 'box': 0},
            'advanced_heuristics': {'straight': 0, 'box': 0},
            'ml_model': {'straight': 0, 'box': 0},
            'exploratory': {'straight': 0, 'box': 0},
        },
        'start_date': start_date,
        'end_date': end_date,
    }

    # tqdmを使用してプログレスバーを表示
    for index, actual_draw in tqdm(target_draws.iterrows(), total=target_draws.shape[0], desc="バックテスト実行中"):
        # 現在の抽選日より前のデータを学習データとして使用
        training_data = all_draws_df[all_draws_df['date'] < actual_draw['date']]

        # 学習データがなければ、その回のテストはスキップ
        if training_data.empty:
            continue
            
        actual_number = actual_draw['winning_numbers']
        actual_number_sorted = "".join(sorted(actual_number))

        # 1. モデルの学習
        ml_model_weights = learn_model_from_data(training_data)

        # 2. 各モデルで予測
        basic_preds = predict_from_basic_stats(training_data, limit=prediction_limit)
        advanced_preds = predict_from_advanced_heuristics(training_data, limit=prediction_limit)
        ml_preds = predict_with_model(ml_model_weights, limit=prediction_limit)
        exploratory_preds = predict_from_exploratory_heuristics(training_data, limit=prediction_limit)

        # 3. アンサンブル予測
        predictions_by_model = {
            'basic_stats': basic_preds,
            'advanced_heuristics': advanced_preds,
            'ml_model': ml_preds,
            'exploratory': exploratory_preds
        }
        final_predictions_df = aggregate_predictions(
            predictions_by_model, ensemble_weights
        )
        
        # 上位N件の予測を取得
        top_n_predictions = final_predictions_df.head(final_prediction_count)['prediction'].tolist()

        # 4. 結果の評価
        hit_found_for_draw = False
        # ストレートヒットの確認
        if actual_number in top_n_predictions:
            results['straight_hits'] += 1
            hit_rank = top_n_predictions.index(actual_number) + 1
            results['ensemble_hit_details'].append({
                'date': actual_draw['date'].date(),
                'winning_number': actual_number,
                'hit_type': 'ストレート',
                'rank': hit_rank
            })
            hit_found_for_draw = True

        # ボックスヒットの確認 (ストレートヒットでなかった場合のみ)
        top_n_predictions_sorted = ["".join(sorted(p)) for p in top_n_predictions]
        if not hit_found_for_draw and actual_number_sorted in top_n_predictions_sorted:
            results['box_hits'] += 1
            hit_rank = top_n_predictions_sorted.index(actual_number_sorted) + 1
            results['ensemble_hit_details'].append({
                'date': actual_draw['date'].date(),
                'winning_number': actual_number,
                'hit_type': 'ボックス',
                'rank': hit_rank
            })
        
        # セット球の計算
        results['set_straight_hits'] = results['straight_hits']
        results['set_box_hits'] = results['box_hits']


        # 個別モデルのパフォーマンス評価
        model_predictions = {
            'basic_stats': basic_preds,
            'advanced_heuristics': advanced_preds,
            'ml_model': ml_preds,
            'exploratory': exploratory_preds,
        }

        for model_name, preds in model_predictions.items():
            if actual_number in preds:
                results['model_performance'][model_name]['straight'] += 1
            if actual_number_sorted in ["".join(sorted(p)) for p in preds]:
                results['model_performance'][model_name]['box'] += 1


    return results

def print_summary(results):
    """
    バックテストの結果を整形して表示します。
    """
    if not results:
        return

    total = results['total_draws']
    straight_hits = results['straight_hits']
    box_hits = results['box_hits'] # これは純粋なボックスヒット（ストレートを外した場合）
    total_box_hits = straight_hits + box_hits # 一般的な意味でのボックスヒット総数
    set_straight_hits = results['set_straight_hits']
    set_box_hits = results['set_box_hits']

    print("\n--- バックテスト結果サマリー ---")
    print(f"対象期間: {results['start_date'].date()} ~ {results['end_date'].date()}")
    print(f"対象抽選回数: {total} 回")
    
    print(f"\n【アンサンブル予測（上位{results.get('final_prediction_count', 5)}件）の的中率】")
    if total > 0:
        print(f"ストレート: {straight_hits}回 / {total}回 ({(straight_hits/total)*100:.2f}%)")
        print(f"ボックス (全体): {total_box_hits}回 / {total}回 ({(total_box_hits/total)*100:.2f}%)")
        print(f"セット（ストレート）: {set_straight_hits}回 / {total}回 ({(set_straight_hits/total)*100:.2f}%)")
        print(f"セット（ボックス）: {set_box_hits}回 / {total}回 ({(set_box_hits/total)*100:.2f}%)")
    else:
        print("的中なし")

    if results['ensemble_hit_details']:
        print("\n【的中詳細】")
        # 日付でソートして表示
        for hit in sorted(results['ensemble_hit_details'], key=lambda x: x['date']):
            print(f"  - {hit['date']}: {hit['winning_number']} ({hit['hit_type']} - 予測{hit['rank']}位)")
    else:
        print("\n【的中詳細】: 期間中の的中はありませんでした。")


    print("\n【個別モデルの貢献度（予測上位50件に含まれた回数）】")
    for model, perf in results['model_performance'].items():
        print(f"- {model}:")
        print(f"  ストレート: {perf['straight']}回")
        print(f"  ボックス: {perf['box']}回")
    
    print("\n--- サマリー終了 ---")


if __name__ == "__main__":
    # --- バックテスト設定 ---
    start_date = datetime(2025, 1, 1) # 期間を拡大
    end_date = datetime(2025, 10, 15) # 最新のデータまで含める
    
    # 最終的な予測候補数を変更してテスト
    for count in [5, 10, 20]:
        print(f"\n{'='*20} 最終予測: 上位 {count}件の場合 {'='*20}")
        backtest_results = run_backtest(
            start_date, 
            end_date, 
            final_prediction_count=count
        )
        
        if backtest_results:
            # 結果辞書に設定値を保存
            backtest_results['final_prediction_count'] = count
            print_summary(backtest_results)

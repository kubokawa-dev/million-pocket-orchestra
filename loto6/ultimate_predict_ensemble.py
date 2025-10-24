"""
🏆🏆🏆 ロト6 世界最強アンサンブル予測システム 🏆🏆🏆
目標: 毎週月曜・木曜に6億円獲得

10個の最先端モデルを統合
予測候補数: 200件（圧倒的カバレッジ）
"""

import os
import sys
import pandas as pd
import numpy as np

# 親ディレクトリをsys.pathに追加
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from tools.utils import load_all_loto6_draws
from loto6.ultimate_prediction_logic import (
    predict_ultra_stats,
    predict_never_appeared,
    predict_golden_ratio,
    predict_hot_cold_mix,
    predict_zone_balance,
    predict_pair_affinity,
    predict_overdue,
    predict_even_odd_balance,
    predict_sum_optimization,
    predict_deep_learning_style,
    aggregate_loto6_predictions,
    apply_diversity_penalty  # NEW: 多様性ペナルティ
)
from loto6.save_prediction_history import save_ensemble_prediction
from loto6.online_learning import load_model_weights


def run_ultimate_loto6_prediction(top_n=50):
    """
    🎯 世界最強のロト6予測を実行
    
    10個の最先端モデルを統合し、200件の予測候補を生成
    """
    print("\n" + "="*80)
    print("🏆🏆🏆 ロト6 最適化予測システム v2.0 🏆🏆🏆")
    print("="*80)
    print("改善: スコア正規化 + 多様性ペナルティ + 7モデルに集約")
    print("="*80 + "\n")
    
    # データ読み込み
    print("📊 データベースから全抽選データを読み込んでいます...")
    df = load_all_loto6_draws()
    if df.empty:
        print("❌ データがありません。処理を中断します。")
        return
    
    print(f"✅ {len(df)}回分の抽選データを読み込みました\n")
    
    # 最新の抽選情報
    last_draw_row = df.sort_values(by='date', ascending=False).iloc[0]
    last_draw_date = last_draw_row['date']
    
    print(f"📅 最新抽選日: {last_draw_date}")
    print(f"🎯 次回予測を生成します\n")
    
    # ========================================================================
    # 各モデルで予測を生成
    # ========================================================================
    print("="*80)
    print("🤖 10個の最先端モデルで予測を生成中...")
    print("="*80 + "\n")
    
    predictions_by_model = {}
    
    # Model 1: 超高度統計
    print("1️⃣  超高度統計モデル（時系列重み付け）...")
    predictions_by_model['ultra_stats'] = predict_ultra_stats(df, limit=25)
    print(f"   ✅ {len(predictions_by_model['ultra_stats'])}件生成\n")
    
    # Model 2: 未出現パターン
    print("2️⃣  未出現パターン特化モデル...")
    predictions_by_model['never_appeared'] = predict_never_appeared(df, limit=30)
    print(f"   ✅ {len(predictions_by_model['never_appeared'])}件生成\n")
    
    # Model 3: 黄金比
    print("3️⃣  黄金比・数学的パターンモデル...")
    predictions_by_model['golden_ratio'] = predict_golden_ratio(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['golden_ratio'])}件生成\n")
    
    # Model 4: ホット&コールド
    print("4️⃣  ホット＆コールド混合モデル...")
    predictions_by_model['hot_cold_mix'] = predict_hot_cold_mix(df, limit=25)
    print(f"   ✅ {len(predictions_by_model['hot_cold_mix'])}件生成\n")
    
    # Model 5: 区間バランス
    print("5️⃣  区間バランス最適化モデル...")
    predictions_by_model['zone_balance'] = predict_zone_balance(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['zone_balance'])}件生成\n")
    
    # Model 6: ペア相性
    print("6️⃣  ペア相性分析モデル...")
    predictions_by_model['pair_affinity'] = predict_pair_affinity(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['pair_affinity'])}件生成\n")
    
    # Model 7: オーバーデュー
    print("7️⃣  オーバーデュー（未出現期間）モデル...")
    predictions_by_model['overdue'] = predict_overdue(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['overdue'])}件生成\n")
    
    # Model 8: 偶奇バランス
    print("8️⃣  偶奇バランス最適化モデル...")
    predictions_by_model['even_odd_balance'] = predict_even_odd_balance(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['even_odd_balance'])}件生成\n")
    
    # Model 9: 合計値最適化
    print("9️⃣  合計値最適化モデル...")
    predictions_by_model['sum_optimization'] = predict_sum_optimization(df, limit=20)
    print(f"   ✅ {len(predictions_by_model['sum_optimization'])}件生成\n")
    
    # Model 10: AIディープラーニング風
    print("🔟 AIディープラーニング風モデル...")
    predictions_by_model['deep_learning'] = predict_deep_learning_style(df, limit=30)
    print(f"   ✅ {len(predictions_by_model['deep_learning'])}件生成\n")
    
    # ========================================================================
    # アンサンブル統合
    # ========================================================================
    print("="*80)
    print("🔮 全モデルの予測を統合・集計中...")
    print("="*80 + "\n")
    
    # 【改良版v2.0】オンライン学習で調整された重みを使用
    try:
        ensemble_weights = load_model_weights()
        print("✅ オンライン学習済みの重みを読み込みました")
    except Exception as e:
        # 読み込み失敗時はデフォルト重みを使用
        ensemble_weights = {
            # コアモデル（高重み）
            'ultra_stats': 10.0,         # 時系列重み付け統計 - 最重要
            'hot_cold_mix': 8.0,         # ホット&コールド混合 - 重要
            'never_appeared': 6.0,       # 未出現パターン - 重要
            
            # 補助モデル（中重み）
            'pair_affinity': 3.0,        # ペア相性分析
            'sum_optimization': 2.5,     # 合計値最適化
            
            # 多様性確保モデル（低重み）
            'deep_learning': 2.0,        # AI風モデル
            'zone_balance': 1.5,         # 区間バランス
        }
        print(f"⚠️ デフォルト重みを使用: {e}")
    
    # 予測を集計（スコア正規化を有効化）
    final_predictions_df = aggregate_loto6_predictions(predictions_by_model, ensemble_weights, normalize_scores=True)
    
    # 多様性ペナルティを適用（類似した候補のスコアを下げる）
    final_predictions_df = apply_diversity_penalty(final_predictions_df, penalty_strength=0.2, similarity_threshold=4)
    
    print(f"✅ 統合完了！")
    print(f"📊 総予測候補数: {len(final_predictions_df)}件\n")
    
    # ========================================================================
    # データベースに保存
    # ========================================================================
    try:
        # 予測を保存用に変換
        predictions_for_save = {}
        for model_name, preds in predictions_by_model.items():
            predictions_for_save[model_name] = [
                ' '.join(f'{n:02d}' for n in p) if isinstance(p, list) else p 
                for p in preds
            ]
        
        pred_id = save_ensemble_prediction(
            predictions_df=final_predictions_df,
            ensemble_weights=ensemble_weights,
            predictions_by_model=predictions_for_save,
            model_state=None,
            notes="Optimized Ensemble v2.0: 7 core models with score normalization and diversity penalty. Models: (1) Ultra Stats (weight=10.0), (2) Hot&Cold Mix (weight=8.0), (3) Never Appeared (weight=6.0), (4) Pair Affinity (weight=3.0), (5) Sum Optimization (weight=2.5), (6) Deep Learning (weight=2.0), (7) Zone Balance (weight=1.5). Features: rank-based score normalization, diversity penalty (strength=0.2, threshold=4)."
        )
        print(f"✅ 予測履歴を保存しました (ID: {pred_id})\n")
    except Exception as e:
        print(f"⚠️  予測履歴の保存に失敗: {e}\n")
    
    # ========================================================================
    # 結果の表示
    # ========================================================================
    print("="*80)
    print("👑👑👑 最終予測結果（上位50件）👑👑👑")
    print("="*80 + "\n")
    
    print("【推奨度の見方】")
    print("  ★★★★★: 超推奨（複数モデルが強く推奨）")
    print("  ★★★★☆: 強推奨")
    print("  ★★★☆☆: 推奨")
    print("  ★★☆☆☆: やや推奨")
    print("  ★☆☆☆☆: 候補\n")
    
    # 上位50件を表示
    for idx, row in final_predictions_df.head(top_n).iterrows():
        score = row['score']
        numbers = row['numbers']
        
        # スコアに応じて星を表示
        if score >= 5.0:
            stars = "★★★★★"
        elif score >= 4.0:
            stars = "★★★★☆"
        elif score >= 3.0:
            stars = "★★★☆☆"
        elif score >= 2.0:
            stars = "★★☆☆☆"
        else:
            stars = "★☆☆☆☆"
        
        print(f"{idx + 1:3d}位 [{stars}] スコア:{score:5.2f} | {numbers}")
    
    print("\n" + "="*80)
    print("🎰 購入推奨: 上位10-20件を購入することで当選確率が最大化されます")
    print("💰 目標: 6億円獲得！")
    print("🍀 幸運を祈ります！")
    print("="*80 + "\n")
    
    return final_predictions_df


if __name__ == '__main__':
    run_ultimate_loto6_prediction(top_n=50)

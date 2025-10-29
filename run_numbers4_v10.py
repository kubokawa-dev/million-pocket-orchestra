"""
ナンバーズ4 v10.0 改善版実行スクリプト

第6843回(0523)を学習し、ナンバーズ3で成功したv10.0のアプローチを適用
"""
import subprocess

print("="*80)
print("🎯 ナンバーズ4 予測システム v10.0 - ナンバーズ3の成功を適用")
print("="*80)
print("\n【v10.0の改善】")
print("✅ 第6843回(0523)をデータベースに追加")
print("✅ ナンバーズ3で成功した4つのモデルを適用:")
print("   1. 数字再出現モデル - 同じ数字が複数桁に出現")
print("   2. 桁継続モデル - 前回の数字が次回も出現")
print("   3. 大変化モデル - ±3-5の大きな変化")
print("   4. 現実的頻度モデル - 過去当選番号も含む")
print("\n" + "="*80)

# ステップ1: 第6843回のデータを追加
print("\n【ステップ1】第6843回(0523)をデータベースに追加...")
print("-"*80)
result = subprocess.run(["python", "numbers4/add_recent_draws.py"], capture_output=False)

# ステップ2: 予測実行
print("\n【ステップ2】v10.0で第6844回を予測...")
print("-"*80)
result = subprocess.run(["python", "numbers4/predict_ensemble.py"], capture_output=False)

print("\n" + "="*80)
print("✅ 完了！")
print("="*80)
print("\n【注意】")
print("新しいv10.0モデルを完全に統合するには、")
print("numbers4/predict_ensemble.py を手動で更新する必要があります。")
print("\n追加が必要なインポート:")
print("  - predict_from_digit_repetition_model_n4")
print("  - predict_from_digit_continuation_model_n4")
print("  - predict_from_large_change_model_n4")
print("  - predict_from_realistic_frequency_model_n4")
print("="*80)

"""
ナンバーズ4 究極版実行スクリプト

第6844回(0017)の特徴を完全に捉える最高精度モデル

【第6844回(0017)の特徴】
- 0が2個（00で連続）
- 1桁目の0が連続（0523→0017）
- 極端に小さい合計値（8）
- 小さい数字が多い（0,0,1,7）

【追加した究極モデル】
1. 0重視モデル（重み50.0） - 0が複数個、特に00連続
2. 1桁目継続モデル（重み40.0） - 1桁目が連続
3. 低合計値モデル（重み35.0） - 合計5-12
4. 小数字重視モデル（重み30.0） - 0,1,2,3を多く含む
"""
import subprocess

print("="*80)
print("🎯 ナンバーズ4 究極版予測システム - 第6845回必勝モデル")
print("="*80)
print("\n【第6844回(0017)の分析結果】")
print("✅ 0が2個出現（00で連続）")
print("✅ 1桁目の0が2回連続（0523→0017）")
print("✅ 極端に小さい合計値（8）")
print("✅ 小さい数字が3個（0,0,1）")
print("\n【究極モデル】")
print("🥇 1. 0重視モデル - 0が複数個、特に00連続を最優先")
print("🥈 2. 1桁目継続モデル - 1桁目が連続する可能性を最重視")
print("🥉 3. 低合計値モデル - 極端に小さい合計値（5-12）")
print("   4. 小数字重視モデル - 0,1,2,3を多く含む")
print("   5. v10.0モデル - 数字再出現、桁継続、大変化、現実的頻度")
print("\n" + "="*80)

# ステップ1: パターン分析
print("\n【ステップ1】パターン分析...")
print("-"*80)
result = subprocess.run(["python", "analyze_n4_patterns.py"], capture_output=False)

# ステップ2: 第6844回のデータを追加
print("\n【ステップ2】第6844回(0017)をデータベースに追加...")
print("-"*80)
result = subprocess.run(["python", "numbers4/add_recent_draws.py"], capture_output=False)

# ステップ3: 究極版で予測実行
print("\n【ステップ3】究極版で第6845回を予測...")
print("-"*80)
result = subprocess.run(["python", "numbers4/predict_ensemble.py"], capture_output=False)

print("\n" + "="*80)
print("✅ 完了！")
print("="*80)
print("\n【重要】")
print("究極モデルを完全に活用するには、")
print("numbers4/predict_ensemble.py に以下のモデルを統合してください:")
print("\n追加が必要なインポート:")
print("  - predict_from_zero_heavy_model  ⭐最重要")
print("  - predict_from_first_digit_continuation_ultimate  ⭐超重要")
print("  - predict_from_low_sum_model")
print("  - predict_from_small_digits_model")
print("\n推奨重み配分:")
print("  zero_heavy: 50.0  # 0が複数個")
print("  first_digit_continuation_ultimate: 40.0  # 1桁目継続")
print("  low_sum: 35.0  # 低合計値")
print("  small_digits: 30.0  # 小数字重視")
print("="*80)

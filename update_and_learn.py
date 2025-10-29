"""
第6843回の結果を反映し、モデルを学習させるスクリプト
"""
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("="*60)
print("ステップ1: 第6843回の結果をデータベースに追加")
print("="*60)
os.system("python numbers3/add_recent_draws.py")

print("\n" + "="*60)
print("ステップ2: 予測履歴を更新（予測ID: 90）")
print("="*60)
os.system("python numbers3/manage_prediction_history.py update 90 631")

print("\n" + "="*60)
print("ステップ3: 統計情報を確認")
print("="*60)
os.system("python numbers3/manage_prediction_history.py stats")

print("\n" + "="*60)
print("✅ 学習完了！次は第6844回の予測を実行してください")
print("="*60)
print("\n実行コマンド: python numbers3/predict_ensemble.py")

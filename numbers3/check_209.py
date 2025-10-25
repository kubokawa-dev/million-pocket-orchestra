"""209とその順列が予測に含まれているか確認するスクリプト"""
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from numbers3.predict_ensemble import generate_ensemble_prediction

# 予測を生成
print("予測を生成中...")
predictions_df, weights = generate_ensemble_prediction()

# 209とその順列をチェック
target_digits = {2, 0, 9}
permutations_209 = ['209', '290', '029', '092', '902', '920']

print("\n" + "="*60)
print("【{2, 0, 9}の順列チェック】")
print("="*60)

for perm in permutations_209:
    matches = predictions_df[predictions_df['prediction'] == perm]
    if not matches.empty:
        rank = matches.index[0] + 1
        score = matches.iloc[0]['score']
        print(f"✅ {perm}: {rank}位 (スコア: {score:.1f})")
    else:
        print(f"❌ {perm}: 予測に含まれていません")

# トップ100を表示
print("\n" + "="*60)
print("【予測トップ100】")
print("="*60)
top_100 = predictions_df.head(100)
for idx, row in top_100.iterrows():
    marker = "⭐" if row['prediction'] in permutations_209 else "  "
    print(f"{marker} {idx+1:3d}位: {row['prediction']} (スコア: {row['score']:.1f})")

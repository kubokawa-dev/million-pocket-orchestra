import os, sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from numbers4.evaluate_methods import ALL_METHODS, get_actual_result, load_method_predictions, evaluate_method
from collections import Counter

latest_draw = 6949
start_draw = latest_draw - 50 + 1

flow = []
for draw in range(start_draw, latest_draw + 1):
    actual = get_actual_result(draw)
    if not actual: continue
    
    best_model = None
    best_score = -1
    
    for method in ALL_METHODS:
        preds = load_method_predictions(draw, method)
        if not preds: continue
        eval_res = evaluate_method(preds, actual, top_k=100)
        if eval_res['score'] > best_score:
            best_score = eval_res['score']
            best_model = method
            
    if best_model and best_score > 0:
        flow.append((draw, best_model, best_score))
    else:
        flow.append((draw, "None", 0))

print("=== 各回の最強モデル ===")
for draw, model, score in flow:
    print(f"第{draw}回: {model} (スコア: {score:.1f})")

print("\n=== ながれのパターン分析 ===")
models_only = [m for d, m, s in flow if m != "None"]

# 連続記録
streaks = []
current_model = None
current_streak = 0
for m in models_only:
    if m == current_model:
        current_streak += 1
    else:
        if current_model:
            streaks.append((current_model, current_streak))
        current_model = m
        current_streak = 1
if current_model:
    streaks.append((current_model, current_streak))

print("連続して強かったモデル:")
for m, s in [x for x in streaks if x[1] > 1]:
    print(f"  - {m}: {s}回連続")

# 次に来やすいモデルの遷移 (A -> B)
transitions = []
for i in range(len(models_only)-1):
    transitions.append(f"{models_only[i]} -> {models_only[i+1]}")

print("\nよくある遷移パターン (Aの次にBが来る):")
trans_counts = Counter(transitions)
for trans, count in trans_counts.most_common(5):
    print(f"  - {trans}: {count}回")


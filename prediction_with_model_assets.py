import os
import sys
import json
import pandas as pd
import numpy as np
import glob
from collections import Counter

# プロジェクトルートへのパス設定
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 必要なモジュールをインポート
# 既存のロジックを再利用する
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_from_extreme_patterns,
    predict_from_exploratory_heuristics,
    aggregate_predictions
)

def load_data():
    """CSVから全データを読み込む"""
    files = sorted(glob.glob('numbers4/*.csv'))
    all_data = []
    for f in files:
        try:
            df = pd.read_csv(f, header=None, encoding='utf-8')
            # 3列目が当選番号、2列目が日付と仮定
            if len(df.columns) >= 3:
                # データ形式に合わせて調整
                temp_df = pd.DataFrame()
                temp_df['numbers'] = df.iloc[:, 2].astype(str).apply(lambda x: x.zfill(4))
                
                # 各桁に分解
                temp_df['d1'] = temp_df['numbers'].apply(lambda x: int(x[0]) if x.isdigit() and len(x)==4 else -1)
                temp_df['d2'] = temp_df['numbers'].apply(lambda x: int(x[1]) if x.isdigit() and len(x)==4 else -1)
                temp_df['d3'] = temp_df['numbers'].apply(lambda x: int(x[2]) if x.isdigit() and len(x)==4 else -1)
                temp_df['d4'] = temp_df['numbers'].apply(lambda x: int(x[3]) if x.isdigit() and len(x)==4 else -1)
                
                # 無効なデータを除外
                temp_df = temp_df[temp_df['d1'] != -1]
                all_data.append(temp_df)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

def load_json_assets():
    """モデルのウェイトと状態をJSONから読み込む"""
    weights_path = 'numbers4/model_weights.json'
    state_path = 'numbers4/model_state.json'
    
    weights = {}
    state = {}
    
    if os.path.exists(weights_path):
        with open(weights_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            weights = data.get('weights', {})
            print(f"✅ Loaded weights from {weights_path}")
            print(f"   Weights: {weights}")
    else:
        print(f"⚠️ Weights file not found: {weights_path}")

    if os.path.exists(state_path):
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
            print(f"✅ Loaded model state from {state_path}")
    else:
        print(f"⚠️ Model state file not found: {state_path}")
        
    return weights, state

def predict_from_model_state(model_state, limit=15):
    """model_state.jsonの確率分布を使って予測する (ml_model_newとして使用)"""
    predictions = set()
    
    pos_probs = model_state.get('pos_probs', [])
    if not pos_probs or len(pos_probs) != 4:
        print("⚠️ Invalid pos_probs in model state")
        return []
    
    # 確率分布をnumpy配列に変換
    probs = [np.array(p) for p in pos_probs]
    
    # 確率分布の検証と正規化
    for i in range(4):
        if len(probs[i]) != 10:
             # 長さが足りない場合は補完
             p = np.zeros(10)
             p[:len(probs[i])] = probs[i]
             probs[i] = p
        
        # 合計が0またはNaNの場合は均等分布にする
        if np.sum(probs[i]) == 0 or np.isnan(np.sum(probs[i])):
            probs[i] = np.ones(10) / 10.0
        else:
            probs[i] = probs[i] / np.sum(probs[i])

    attempts = 0
    while len(predictions) < limit and attempts < limit * 50:
        attempts += 1
        digits = []
        for i in range(4):
            d = np.random.choice(10, p=probs[i])
            digits.append(str(d))
        
        num_str = "".join(digits)
        predictions.add(num_str)
        
    return list(predictions)

def main():
    print("🚀 Starting prediction using ONLY specified model assets...")
    
    # 1. データ読み込み
    df = load_data()
    print(f"📊 Loaded {len(df)} historical records.")
    
    # 2. モデル資産読み込み
    weights, model_state = load_json_assets()
    
    # 3. 各モデルで予測
    print("\n🔮 Generating predictions from sub-models...")
    
    # model_weights.jsonにあるモデルのみを実行する方針
    # キー: 'advanced_heuristics', 'exploratory', 'extreme_patterns', 'basic_stats', 'ml_model_new'
    
    predictions_by_model = {}
    
    # (1) Basic Stats
    if 'basic_stats' in weights:
        print("   - Running Basic Stats Model...")
        predictions_by_model['basic_stats'] = predict_from_basic_stats(df, limit=10)
        
    # (2) Advanced Heuristics
    if 'advanced_heuristics' in weights:
        print("   - Running Advanced Heuristics Model...")
        predictions_by_model['advanced_heuristics'] = predict_from_advanced_heuristics(df, limit=10)

    # (3) Exploratory
    if 'exploratory' in weights:
        print("   - Running Exploratory Model...")
        predictions_by_model['exploratory'] = predict_from_exploratory_heuristics(df, limit=20)
        
    # (4) Extreme Patterns
    if 'extreme_patterns' in weights:
        print("   - Running Extreme Patterns Model...")
        predictions_by_model['extreme_patterns'] = predict_from_extreme_patterns(df, limit=15)
        
    # (5) ML Model New (using model_state.json)
    if 'ml_model_new' in weights and model_state:
        print("   - Running ML Model (from state json)...")
        predictions_by_model['ml_model_new'] = predict_from_model_state(model_state, limit=20)
        
    # 4. アンサンブル集計
    print("\n⚖️  Aggregating predictions with weights...")
    final_df = aggregate_predictions(predictions_by_model, weights, normalize_scores=True)
    
    # 5. 結果表示
    print("\n" + "="*50)
    print("🏆 第6893回 ナンバーズ4 予測結果 (Top 20)")
    print("="*50)
    
    if final_df.empty:
        print("No predictions generated.")
    else:
        top_20 = final_df.head(20)
        for i, row in top_20.iterrows():
            pred = row['prediction']
            score = row['score']
            print(f"{i+1:2d}位: {pred} (Score: {score:.4f})")
            
    print("\nDone!")

if __name__ == "__main__":
    main()

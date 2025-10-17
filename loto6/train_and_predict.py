import os
import glob
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from collections import Counter

# 定数
NUM_RANGE = list(range(1, 44))  # 1から43までの数字
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
COLS = [
    'kai', 'date', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus',
    '1st_winners', '1st_prize', '2nd_winners', '2nd_prize',
    '3rd_winners', '3rd_prize', '4th_winners', '4th_prize',
    '5th_winners', '5th_prize', 'carryover'
]

def load_data(pattern=None) -> pd.DataFrame:
    if pattern is None:
        pattern = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'loto6', '*.csv')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError('loto6 CSVが見つかりませんでした。')
    df_list = []
    for f in files:
        tmp = pd.read_csv(f, header=None, names=COLS, dtype=str)
        df_list.append(tmp)
    df = pd.concat(df_list, ignore_index=True)
    num_cols = [f'num{i}' for i in range(1, 7)]
    for c in num_cols + ['bonus']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df.dropna(subset=num_cols, inplace=True)
    for c in num_cols:
        df[c] = df[c].astype(int)
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
    df = df.sort_values('date_dt').reset_index(drop=True)
    return df

def create_features(df: pd.DataFrame, window_size=10):
    features = []
    labels = []

    num_cols = [f'num{i}' for i in range(1, 7)]
    df_nums = df[num_cols]

    for i in range(window_size, len(df)):
        # 特徴量: 過去{window_size}回の出現パターン
        window = df_nums.iloc[i-window_size:i]
        # 各数字の出現回数
        freq = Counter(window.values.flatten())
        feature_vector = [freq.get(n, 0) for n in NUM_RANGE]
        features.append(feature_vector)

        # ラベル: 次の回の当選番号
        target = df_nums.iloc[i].values
        label_vector = [1 if n in target else 0 for n in NUM_RANGE]
        labels.append(label_vector)

    return np.array(features), np.array(labels)

def train_models(features, labels):
    os.makedirs(MODEL_DIR, exist_ok=True)
    models = {}
    for i, num in enumerate(NUM_RANGE):
        print(f'Training model for number {num}...')
        y = labels[:, i]
        
        # データが不均衡な場合（ほとんど0の場合）に対応
        if len(np.unique(y)) < 2:
            print(f'Skipping model for {num} due to single class in labels.')
            continue

        X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42, stratify=y)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)
        
        model_path = os.path.join(MODEL_DIR, f'loto6_model_{num}.joblib')
        joblib.dump(model, model_path)
        models[num] = model
        print(f'Model for {num} saved. Accuracy: {model.score(X_test, y_test):.4f}')
    return models

def load_models():
    models = {}
    if not os.path.exists(MODEL_DIR):
        return None
    for i, num in enumerate(NUM_RANGE):
        model_path = os.path.join(MODEL_DIR, f'loto6_model_{num}.joblib')
        if os.path.exists(model_path):
            models[num] = joblib.load(model_path)
    return models

def predict_next_draw(df: pd.DataFrame, window_size=10):
    models = load_models()
    if not models:
        print("Models not found. Please train first.")
        return None, None

    # 最新のデータから特徴量を生成
    latest_window = df.iloc[-window_size:][[f'num{i}' for i in range(1, 7)]]
    freq = Counter(latest_window.values.flatten())
    feature_vector = [freq.get(n, 0) for n in NUM_RANGE]
    
    # 各モデルで予測確率を計算
    probabilities = []
    for num in NUM_RANGE:
        if num in models:
            prob = models[num].predict_proba([feature_vector])[0][1] # クラス1（出現する）の確率
            probabilities.append(prob)
        else:
            probabilities.append(0.0)
            
    # 確率を降順にソート
    sorted_probs = sorted(zip(NUM_RANGE, probabilities), key=lambda x: x[1], reverse=True)

    # 上位の数字をいくつか選択
    top_n = 12
    high_prob_numbers = [num for num, prob in sorted_probs[:top_n]]

    # 組み合わせを生成（ここでは単純に上位6つを選ぶ）
    # TODO: advanced_predict_loto6.py のようなスコアリングロジックを組み合わせる
    predicted_combination = high_prob_numbers[:6]

    return predicted_combination, sorted_probs

if __name__ == '__main__':
    # --- 学習フェーズ ---
    print("Loading data for training...")
    df_train = load_data()
    print(f"Loaded {len(df_train)} records.")

    print("Creating features and labels...")
    features, labels = create_features(df_train)
    print(f"Created {len(features)} feature sets.")

    print("Training models...")
    train_models(features, labels)
    print("Training complete.")

    # --- 予測フェーズ ---
    print("\nLoading data for prediction...")
    df_pred = load_data() # 本来は最新のデータを取得
    
    print("Predicting next draw...")
    prediction, probabilities = predict_next_draw(df_pred)

    if prediction:
        print(f"\nPredicted combination: {sorted(prediction)}")
        print("\nTop 12 numbers and their probabilities:")
        for num, prob in probabilities[:12]:
            print(f"  Number {num:2d}: {prob:.4f}")

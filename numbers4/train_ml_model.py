import os
import pandas as pd
import numpy as np
import joblib
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 定数
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

def load_all_draws():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers4_draws ORDER BY draw_date ASC", conn)
    conn.close()
    
    df['d1'] = df['numbers'].str[0].astype(int)
    df['d2'] = df['numbers'].str[1].astype(int)
    df['d3'] = df['numbers'].str[2].astype(int)
    df['d4'] = df['numbers'].str[3].astype(int)
    df['date_dt'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('date_dt').reset_index(drop=True)
    return df

def create_features(df: pd.DataFrame, main_window=20):
    features = []
    labels = {
        'd1': [], 'd2': [], 'd3': [], 'd4': []
    }

    # 過去のデータを参照するため、十分な履歴がある時点から開始
    start_index = main_window 
    for i in range(start_index, len(df)):
        
        feature_vector = []
        # --- ラグ特徴量 (直近3回) ---
        for lag in [1, 2, 3]:
            past_row = df.iloc[i - lag]
            for d in range(1, 5):
                feature_vector.append(past_row[f'd{d}'])

        # --- 統計的特徴量 (異なるウィンドウサイズ) ---
        for window_size in [5, 10, 20]:
            window = df.iloc[i-window_size:i]
            # 各桁の平均値
            for d in range(1, 5):
                feature_vector.append(window[f'd{d}'].mean())
            # 各桁の標準偏差
            for d in range(1, 5):
                feature_vector.append(window[f'd{d}'].std())
            # 合計値の平均
            feature_vector.append(window[['d1', 'd2', 'd3', 'd4']].sum(axis=1).mean())

        # --- 未出現期間 (Overdue) & 移動度数 --- 
        window_main = df.iloc[i-main_window:i]
        for d in range(1, 5):
            col = f'd{d}'
            for num in range(10):
                # 移動度数 (過去20回でその数字が何回出たか)
                freq = (window_main[col] == num).sum()
                feature_vector.append(freq)
                
                # 未出現期間
                if freq > 0:
                    last_seen_index = window_main[window_main[col] == num].index[-1]
                    overdue = i - last_seen_index
                    feature_vector.append(overdue)
                else:
                    feature_vector.append(main_window + 1) # ウィンドウ内になければ最大+1

        features.append(feature_vector)

        # ラベル: 次の回の当選番号
        target = df.iloc[i]
        for d in range(1, 5):
            labels[f'd{d}'].append(target[f'd{d}'])

    # NaNを0で埋める（標準偏差が計算できない場合など）
    features_np = np.array(features)
    features_np = np.nan_to_num(features_np)

    return features_np, {k: np.array(v) for k, v in labels.items()}

def train_and_save_models(features, labels):
    os.makedirs(MODEL_DIR, exist_ok=True)
    models = {}
    for i in range(1, 5):
        digit_label = f'd{i}'
        print(f'Training model for {digit_label}...')
        y = labels[digit_label]
        
        if len(np.unique(y)) < 2:
            print(f'Skipping model for {digit_label} due to single class in labels.')
            continue

        # 時系列データなので、シャッフルせずに過去のデータで学習し、未来のデータでテストする
        X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42, shuffle=False)
        
        model = lgb.LGBMClassifier(random_state=42, class_weight='balanced', n_estimators=200, learning_rate=0.05, num_leaves=31)
        model.fit(X_train, y_train)
        
        model_path = os.path.join(MODEL_DIR, f'numbers4_model_{digit_label}.joblib')
        joblib.dump(model, model_path)
        models[digit_label] = model
        print(f'Model for {digit_label} saved. Accuracy: {model.score(X_test, y_test):.4f}')
    return models

if __name__ == '__main__':
    print("Loading data for training...")
    df_train = load_all_draws()
    print(f"Loaded {len(df_train)} records.")

    print("Creating features and labels...")
    features, labels = create_features(df_train)
    print(f"Created {len(features)} feature sets.")

    print("Training and saving models...")
    train_and_save_models(features, labels)
    print("\nAll models have been trained and saved successfully.")

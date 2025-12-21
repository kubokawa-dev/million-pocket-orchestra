import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime

def create_base_features(df: pd.DataFrame):
    """
    ロト6の履歴データから、各抽選回ごとの基本特徴量を作成する。
    """
    df = df.copy()
    if 'date' not in df.columns and 'draw_date' in df.columns:
        df['date'] = pd.to_datetime(df['draw_date'])
    else:
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.sort_values('date').reset_index(drop=True)
    df['draw_id'] = df.index  # 連番ID
    
    # 当選番号を解析 (set_1..set_6 or similar columns expected)
    # 既存の load_all_loto6_draws が返す形式を確認する必要があるが、
    # 通常は set_1, ..., set_6 のような列名か、numbers=[...] 形式。
    # ここでは一般的な形式として set_1...set_6 を想定し、なければ numbers カラムから展開する。
    
    cols_numbers = [f'set_{i}' for i in range(1, 7)]
    if not all(col in df.columns for col in cols_numbers):
        # numbers カラム (list or string) から展開
        # "01,02,..." or [1, 2, ...]
        if 'numbers' in df.columns:
            # check type of first element
            first_val = df['numbers'].iloc[0]
            if isinstance(first_val, str):
                # "01 02 03..." or "01,02,..."
                sep = ',' if ',' in first_val else ' '
                temp = df['numbers'].str.split(sep, expand=True)
            elif isinstance(first_val, list) or isinstance(first_val, np.ndarray):
                temp = pd.DataFrame(df['numbers'].tolist())
            
            for i in range(6):
                df[f'set_{i+1}'] = temp[i].astype(int)
    
    # 各数字(1-43)の出現フラグを作成 (One-hot encoding of winning numbers)
    for i in range(1, 44):
        # どの列(set_1..6)に数字iが含まれているか
        df[f'is_{i}'] = df[[f'set_{k}' for k in range(1, 7)]].isin([i]).any(axis=1).astype(int)

    # 日付特徴量
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['dayofyear'] = df['date'].dt.dayofyear
    
    return df

def create_number_features(df: pd.DataFrame):
    """
    数字ごとの特徴量を作成し、(draw_id, number) 形式のロングフォーマットに変換する。
    
    特徴量:
    - 直近N回の出現回数
    - 前回の出現からの間隔 (Recency)
    - 同時出現ペアの相性スコア (簡易版)
    """
    # 抽選回数
    n_draws = len(df)
    
    # 結果を格納するリスト
    rows = []
    
    # 計算高速化のためにnumpy配列化
    is_appeared_matrix = df[[f'is_{i}' for i in range(1, 44)]].values # (n_draws, 43)
    
    # 特徴量作成のためのループ
    # 過去のデータを参照するため、ある程度の履歴が必要
    start_idx = 50 
    
    for i in range(start_idx, n_draws):
        draw_id = df.loc[i, 'draw_id']
        date_feats = df.loc[i, ['year', 'month', 'day', 'dayofweek', 'dayofyear']].to_dict()
        
        # 過去データのスライス
        past_5 = is_appeared_matrix[i-5:i]
        past_10 = is_appeared_matrix[i-10:i]
        past_20 = is_appeared_matrix[i-20:i]
        past_50 = is_appeared_matrix[i-50:i]
        
        for num in range(1, 44):
            num_idx = num - 1 # 0-indexed for matrix
            
            # Target: 今回出現したか？
            target = is_appeared_matrix[i, num_idx]
            
            # Features
            feat = {
                'draw_id': draw_id,
                'number': num,
                'target': target,
                **date_feats
            }
            
            # Frequency features
            feat['freq_5'] = past_5[:, num_idx].sum()
            feat['freq_10'] = past_10[:, num_idx].sum()
            feat['freq_20'] = past_20[:, num_idx].sum()
            feat['freq_50'] = past_50[:, num_idx].sum()
            
            # Recency (何回前に出たか)
            # 過去50回で探す。見つからなければ50とする。
            last_appear = np.where(past_50[:, num_idx] == 1)[0]
            if len(last_appear) > 0:
                feat['recency'] = 50 - 1 - last_appear[-1]
            else:
                feat['recency'] = 50
            
            rows.append(feat)
            
    return pd.DataFrame(rows)

def train_and_predict_lgbm_loto6(df: pd.DataFrame, limit: int = 20):
    """
    Loto6のLightGBM予測モデル
    """
    # 1. 基本データ作成
    df_base = create_base_features(df)
    
    # 2. 学習用データセット作成 (Long format)
    # 最新の抽選回を含まない形で学習データを作る
    # (train_and_predictなので、全データを使って学習し、未来を予測する形にするが、
    #  create_number_featuresは「その回の正解」を含むので、最終行まで作ると直近回の学習データになる)
    
    df_train_rows = create_number_features(df_base)
    
    if df_train_rows.empty:
        return []
        
    # 特徴量カラムの特定
    exclude_cols = ['draw_id', 'target', 'year'] # yearはトレンドあるかもしれないが入れるか迷う。一旦除外しない。
    feature_cols = [c for c in df_train_rows.columns if c not in ['draw_id', 'target']]
    
    X = df_train_rows[feature_cols]
    y = df_train_rows['target']
    
    # 学習 (直近10%を検証用にする)
    split_idx = int(len(X) * 0.9)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # LightGBMパラメータ (Binary Classification for each number)
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,
        'num_leaves': 31,
        'max_depth': -1,
        'verbose': -1,
        'random_state': 42,
        'is_unbalance': True # 当選(1)は圧倒的に少ないので不均衡データ対策
    }
    
    train_set = lgb.Dataset(X_train, label=y_train)
    val_set = lgb.Dataset(X_val, label=y_val, reference=train_set)
    
    model = lgb.train(
        params,
        train_set,
        num_boost_round=1000,
        valid_sets=[train_set, val_set],
        callbacks=[
            lgb.early_stopping(stopping_rounds=50, verbose=False),
            lgb.log_evaluation(period=0)
        ]
    )
    
    # 3. 次回予測用の特徴量作成
    # 「次の回」のための特徴量は、直近のデータ履歴から作られる
    # create_number_features のロジックを使って、"未来の回" のための行を生成する
    
    last_idx = len(df_base)
    is_appeared_matrix = df_base[[f'is_{i}' for i in range(1, 44)]].values
    
    next_rows = []
    
    # 次回の日付（推定）
    last_date = df_base['date'].iloc[-1]
    next_date = last_date + pd.Timedelta(days=3) # 仮
    
    date_feats = {
        'year': next_date.year,
        'month': next_date.month,
        'day': next_date.day,
        'dayofweek': next_date.dayofweek,
        'dayofyear': next_date.dayofyear
    }
    
    past_5 = is_appeared_matrix[-5:]
    past_10 = is_appeared_matrix[-10:]
    past_20 = is_appeared_matrix[-20:]
    past_50 = is_appeared_matrix[-50:]
    
    for num in range(1, 44):
        num_idx = num - 1
        
        feat = {
            'number': num,
            **date_feats
        }
        
        # Frequency
        feat['freq_5'] = past_5[:, num_idx].sum()
        feat['freq_10'] = past_10[:, num_idx].sum()
        feat['freq_20'] = past_20[:, num_idx].sum()
        feat['freq_50'] = past_50[:, num_idx].sum()
        
        # Recency
        last_appear = np.where(past_50[:, num_idx] == 1)[0]
        if len(last_appear) > 0:
            feat['recency'] = 50 - 1 - last_appear[-1] # 直近のインデックスが末尾に近いほど小さい値にしたいならこれ逆かも？
            # last_appear[-1] は 0..49 のインデックス。49が最新(直前)。
            # Recency = 0 (前回出た) -> index=49. 50 - 1 - 49 = 0. OK.
        else:
            feat['recency'] = 50
            
        next_rows.append(feat)
        
    df_next = pd.DataFrame(next_rows)
    X_pred = df_next[feature_cols]
    
    # 確率予測
    probs = model.predict(X_pred)
    df_next['prob'] = probs
    
    # 確率の高い順に数字をソート
    df_next = df_next.sort_values('prob', ascending=False)
    
    # 予測生成戦略:
    # 単純にTop 6を選ぶだけでなく、確率分布に基づいてランダムサンプリングして多様な組み合わせを作る
    
    predictions = []
    seen = set()
    
    top_candidates = df_next['number'].values[:15] # 上位15個を有力候補とする
    top_probs = df_next['prob'].values[:15]
    top_probs = top_probs / top_probs.sum() # Normalize
    
    attempts = 0
    while len(predictions) < limit and attempts < limit * 100:
        attempts += 1
        
        # 確率に基づいて6個選ぶ（非復元抽出）
        # np.random.choice は replace=False で非復元抽出できる
        try:
            chosen = np.random.choice(top_candidates, size=6, replace=False, p=top_probs)
            chosen = sorted(chosen)
            
            # フォーマット "01 02 ..."
            pred_str = " ".join([f"{n:02d}" for n in chosen])
            
            if pred_str not in seen:
                seen.add(pred_str)
                predictions.append(pred_str)
        except ValueError:
            # 万が一確率計算でエラーが出た場合はランダム
            chosen = np.random.choice(range(1, 44), size=6, replace=False)
            chosen = sorted(chosen)
            pred_str = " ".join([f"{n:02d}" for n in chosen])
            if pred_str not in seen:
                seen.add(pred_str)
                predictions.append(pred_str)
                
    return predictions

def predict_from_lightgbm(df: pd.DataFrame, limit: int = 20):
    """
    Main entry point
    """
    try:
        return train_and_predict_lgbm_loto6(df, limit=limit)
    except Exception as e:
        print(f"[LightGBM Loto6] Error: {e}")
        import traceback
        traceback.print_exc()
        return []










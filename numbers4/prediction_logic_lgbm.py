import pandas as pd
import numpy as np
import lightgbm as lgb
from collections import Counter
from datetime import datetime

def create_features(df: pd.DataFrame):
    """
    Numbers4の履歴データから特徴量を作成する
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Extract digits
    df['d1'] = df['numbers'].str[0].astype(int)
    df['d2'] = df['numbers'].str[1].astype(int)
    df['d3'] = df['numbers'].str[2].astype(int)
    df['d4'] = df['numbers'].str[3].astype(int)
    
    # Date features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['dayofyear'] = df['date'].dt.dayofyear
    
    # Lag features (past N draws)
    lags = [1, 2, 3, 5, 10]
    cols_to_lag = ['d1', 'd2', 'd3', 'd4']
    
    for lag in lags:
        for col in cols_to_lag:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    # Rolling statistics (past N draws)
    windows = [5, 10, 20]
    for window in windows:
        for col in cols_to_lag:
            df[f'{col}_mean_{window}'] = df[col].rolling(window=window).mean()
            df[f'{col}_std_{window}'] = df[col].rolling(window=window).std()
            # Count of odd/even in window
            df[f'{col}_odd_count_{window}'] = df[col].rolling(window=window).apply(lambda x: (x % 2 != 0).sum())
    
    # Sum of digits
    df['sum'] = df['d1'] + df['d2'] + df['d3'] + df['d4']
    df['sum_lag_1'] = df['sum'].shift(1)
    df['sum_mean_5'] = df['sum'].rolling(5).mean()
    
    # Drop rows with NaN (due to shifting/rolling)
    df_clean = df.dropna().reset_index(drop=True)
    return df_clean

def train_and_predict_lgbm(df: pd.DataFrame, limit: int = 15):
    """
    LightGBMモデルを学習し、次回予測を行う
    """
    # Prepare data
    df_features = create_features(df)
    
    if len(df_features) < 100:
        # Not enough data
        return []
    
    # Latest data for prediction (features from the last available row, but shifted contextually for "next" prediction)
    # Ideally, we want to predict row T+1 using features from T.
    # create_features puts features for row T in row T.
    # So for training: X=features[T-1], y=target[T].
    # For prediction: X=features[T] (latest known), y=target[T+1] (unknown).
    
    # Let's reconstruct features specifically for "next prediction" paradigm.
    # We use features derived from data up to row T to predict T+1.
    
    target_cols = ['d1', 'd2', 'd3', 'd4']
    feature_cols = [c for c in df_features.columns if c not in target_cols + ['draw_date', 'numbers', 'date', 'sum']]
    
    # Training data:
    # X = current row's features (which contain lags/stats of PAST)
    # But wait, create_features puts `d1_lag_1` as `d1` of row T-1.
    # If we want to predict row T's d1, we should use lag_1 (which is T-1's d1).
    # Yes, create_features aligns `d1` with `d1_lag_1` on the same row.
    # So X = feature_cols, y = target_cols is correct for "predicting current row given past context".
    
    X = df_features[feature_cols]
    y = df_features[target_cols]
    
    # Train/Test split not strictly needed for final prediction, use all data
    # But early stopping is good. Let's use last 100 for validation.
    
    X_train = X.iloc[:-50]
    X_val = X.iloc[-50:]
    
    models = {}
    predictions = {}
    
    params = {
        'objective': 'multiclass',
        'num_class': 10,
        'metric': 'multi_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,
        'num_leaves': 31,
        'max_depth': -1,
        'verbose': -1,
        'random_state': 42
    }
    
    for i, target in enumerate(target_cols):
        y_train = y[target].iloc[:-50]
        y_val = y[target].iloc[-50:]
        
        train_set = lgb.Dataset(X_train, label=y_train)
        val_set = lgb.Dataset(X_val, label=y_val, reference=train_set)
        
        model = lgb.train(
            params,
            train_set,
            num_boost_round=1000,
            valid_sets=[train_set, val_set],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50, verbose=False),
                lgb.log_evaluation(period=0) # Suppress log
            ]
        )
        models[target] = model
    
    # Predict for NEXT draw
    # We need features for the "next" draw.
    # Basically, we construct a row that represents "after the last known draw".
    # The easiest way is to append a dummy row to original df, run create_features, take the last row.
    
    last_date = df_features['date'].iloc[-1]
    next_date = last_date + pd.Timedelta(days=1) # Approximate, exact day doesn't matter too much for lags
    
    # Create a dummy row to generate features for T+1
    # Values of d1..d4 don't matter as they will be shifted into lags for T+2, but we need lags for T+1
    # Actually, `create_features` calculates lags/stats based on previous rows.
    # So if we have rows 0..T, and we want features for T+1:
    # We can just take the last row of `df_features`?
    # No, df_features row T contains `d1` (target) and `d1_lag_1` (feature).
    # We want to predict T+1. The features for T+1 would be based on T.
    # `d1_lag_1` for T+1 should be `d1` of T.
    
    # Let's manually construct the feature vector for prediction.
    # OR, easier: Append a dummy row to DF, re-run create_features, pick last row.
    
    dummy_row = pd.DataFrame({
        'draw_date': [next_date],
        'numbers': ['0000'], # Dummy
        'd1': [0], 'd2': [0], 'd3': [0], 'd4': [0],
        'date': [next_date]
    })
    
    # Ensure df has date column for concatenation if it doesn't already
    if 'date' not in df.columns:
        df = df.copy()
        df['date'] = df_features['date']

    df_extended = pd.concat([df, dummy_row], ignore_index=True)
    df_features_ext = create_features(df_extended)
    
    X_pred = df_features_ext[feature_cols].iloc[[-1]]
    
    # Predict probabilities for each digit position
    preds_probs = {}
    for target in target_cols:
        preds_probs[target] = models[target].predict(X_pred)[0] # array of 10 probs
    
    # Generate candidates based on top probabilities
    # Strategy: Randomly sample from prob distribution to generate diversity
    
    generated_preds = []
    seen = set()
    
    # Try to generate 'limit' unique predictions
    attempts = 0
    while len(generated_preds) < limit and attempts < limit * 50:
        attempts += 1
        
        # Sample digits based on predicted probabilities
        p_d1 = np.random.choice(10, p=preds_probs['d1'])
        p_d2 = np.random.choice(10, p=preds_probs['d2'])
        p_d3 = np.random.choice(10, p=preds_probs['d3'])
        p_d4 = np.random.choice(10, p=preds_probs['d4'])
        
        num_str = f"{p_d1}{p_d2}{p_d3}{p_d4}"
        
        # Exclude latest actual result to avoid repeating exactly same (unless it's a strategy)
        # But here we just want unique candidates
        if num_str not in seen:
            generated_preds.append(num_str)
            seen.add(num_str)
            
    return generated_preds

def predict_from_lightgbm(df: pd.DataFrame, limit: int = 15):
    """
    Main entry point for LightGBM prediction
    """
    try:
        # Convert 'date' column if needed or ensure format
        # The `create_features` handles conversion from `draw_date` or `date`
        # The input df usually has 'date' as datetime object from `load_all_numbers4_draws`
        # but `create_features` expects `draw_date` (string) or handles `date`.
        # Let's ensure compatibility.
        
        df_local = df.copy()
        if 'draw_date' not in df_local.columns and 'date' in df_local.columns:
            df_local['draw_date'] = df_local['date']
        
        # Run prediction
        return train_and_predict_lgbm(df_local, limit=limit)
        
    except Exception as e:
        print(f"[LightGBM] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


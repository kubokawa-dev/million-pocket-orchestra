import pandas as pd
import numpy as np
import lightgbm as lgb
from collections import Counter
from datetime import datetime

# ========== Temperature Scaling ==========
# 確率分布を平滑化して多様性を向上させる
# temperature > 1.0: より均一に (多様性UP)
# temperature < 1.0: よりピーキーに (確信度UP)
# v14.0: 2.5→1.5に引き下げ（2.5は均一分布に近すぎてML学習が無効化されていた）
# 1.5なら低確率数字にもチャンスを残しつつ、MLの予測信号を保持
DEFAULT_TEMPERATURE = 1.5

def apply_temperature(probs: np.ndarray, temperature: float = DEFAULT_TEMPERATURE) -> np.ndarray:
    """
    確率分布にTemperature Scalingを適用
    
    数学的に: exp(log(p)/T) = p^(1/T) と等価
    
    Args:
        probs: 確率分布 (0-1の配列、合計1)
        temperature: 温度パラメータ (デフォルト: 2.0)
            - 1.0: 変化なし
            - 2.0: 確率を平滑化 (低確率の数字も選ばれやすく)
            - 0.5: 確率を尖らせる (高確率の数字がより選ばれやすく)
    
    Returns:
        Temperature適用後の確率分布
    """
    probs = np.array(probs, dtype=np.float64)
    # ゼロ除算防止
    probs = np.clip(probs, 1e-10, 1.0)
    # Temperature適用 (確率をべき乗): p^(1/T)
    scaled_probs = probs ** (1.0 / temperature)
    # 正規化
    return scaled_probs / scaled_probs.sum()

def create_features(df: pd.DataFrame):
    """
    Numbers4の履歴データから特徴量を作成する
    
    v2.0 強化版：ボックス的中率向上のため、以下の特徴量を追加
    - ペア出現頻度
    - 数字の偏り（ユニーク数、最大繰り返し数）
    - 連続性（前回との差分）
    - 合計値のカテゴリ
    - 偶数・奇数パターン
    - 数字ごとの出現サイクル
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Extract digits
    df['d1'] = df['numbers'].str[0].astype(int)
    df['d2'] = df['numbers'].str[1].astype(int)
    df['d3'] = df['numbers'].str[2].astype(int)
    df['d4'] = df['numbers'].str[3].astype(int)
    
    # ========== 基本特徴量 ==========
    # Date features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['dayofyear'] = df['date'].dt.dayofyear
    df['is_monday'] = (df['dayofweek'] == 0).astype(int)
    df['is_friday'] = (df['dayofweek'] == 4).astype(int)
    
    # Lag features (past N draws)
    lags = [1, 2, 3, 5, 10, 20]
    cols_to_lag = ['d1', 'd2', 'd3', 'd4']
    
    for lag in lags:
        for col in cols_to_lag:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    # Rolling statistics (past N draws)
    windows = [5, 10, 20, 50]
    for window in windows:
        for col in cols_to_lag:
            df[f'{col}_mean_{window}'] = df[col].rolling(window=window).mean()
            df[f'{col}_std_{window}'] = df[col].rolling(window=window).std()
            df[f'{col}_min_{window}'] = df[col].rolling(window=window).min()
            df[f'{col}_max_{window}'] = df[col].rolling(window=window).max()
            # Count of odd/even in window
            df[f'{col}_odd_count_{window}'] = df[col].rolling(window=window).apply(lambda x: (x % 2 != 0).sum(), raw=True)
    
    # ========== 合計値関連 ==========
    df['sum'] = df['d1'] + df['d2'] + df['d3'] + df['d4']
    df['sum_lag_1'] = df['sum'].shift(1)
    df['sum_lag_2'] = df['sum'].shift(2)
    df['sum_lag_3'] = df['sum'].shift(3)
    df['sum_mean_5'] = df['sum'].rolling(5).mean()
    df['sum_mean_10'] = df['sum'].rolling(10).mean()
    df['sum_std_5'] = df['sum'].rolling(5).std()
    df['sum_diff'] = df['sum'].diff()  # 前回との差分
    
    # 合計値のカテゴリ（低/中低/中高/高）
    df['sum_category'] = pd.cut(df['sum'], bins=[-1, 9, 18, 27, 37], labels=[0, 1, 2, 3]).astype(float)
    
    # ========== NEW: ペア特徴量 ==========
    # 隣接桁のペアID
    df['pair_12'] = df['d1'] * 10 + df['d2']
    df['pair_23'] = df['d2'] * 10 + df['d3']
    df['pair_34'] = df['d3'] * 10 + df['d4']
    df['pair_12_lag_1'] = df['pair_12'].shift(1)
    df['pair_23_lag_1'] = df['pair_23'].shift(1)
    df['pair_34_lag_1'] = df['pair_34'].shift(1)
    
    # ========== NEW: 数字の偏り特徴量 ==========
    # ユニークな数字の数（1-4）
    df['unique_count'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda x: len(set(x)), axis=1)
    df['unique_count_lag_1'] = df['unique_count'].shift(1)
    
    # 最も多く出現する数字の回数（1-4）
    df['max_repeat'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda x: max(Counter(x).values()), axis=1)
    df['max_repeat_lag_1'] = df['max_repeat'].shift(1)
    
    # ゾロ目フラグ（4つ全部同じ）
    df['is_quads'] = (df['unique_count'] == 1).astype(int)
    
    # トリプルフラグ（3つ同じ）
    df['has_triple'] = (df['max_repeat'] >= 3).astype(int)
    
    # ダブルダブルフラグ（2つ×2組）
    df['is_double_double'] = df[['d1', 'd2', 'd3', 'd4']].apply(
        lambda x: len([c for c in Counter(x).values() if c == 2]) == 2, axis=1
    ).astype(int)
    
    # ========== NEW: 連続性・差分特徴量 ==========
    for col in cols_to_lag:
        df[f'{col}_diff_1'] = df[col].diff(1)  # 前回との差
        df[f'{col}_diff_2'] = df[col].diff(2)  # 2回前との差
        df[f'{col}_abs_diff_1'] = df[col].diff(1).abs()  # 絶対差
    
    # 全桁の変化量合計
    df['total_change'] = (df['d1_abs_diff_1'].fillna(0) + df['d2_abs_diff_1'].fillna(0) + 
                          df['d3_abs_diff_1'].fillna(0) + df['d4_abs_diff_1'].fillna(0))
    
    # ========== NEW: 偶数・奇数パターン ==========
    df['even_count'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda x: sum(v % 2 == 0 for v in x), axis=1)
    df['odd_count'] = 4 - df['even_count']
    df['even_count_lag_1'] = df['even_count'].shift(1)
    
    # 偶奇パターン（EEEO=3, EEOO=2, EOOO=1, OOOO=0など）
    df['even_odd_pattern'] = df['even_count']  # シンプルに偶数の数
    
    # ========== NEW: 数字ごとの出現サイクル ==========
    # 各数字(0-9)が何回前に出たか
    for digit in range(10):
        digit_appeared = ((df['d1'] == digit) | (df['d2'] == digit) | 
                          (df['d3'] == digit) | (df['d4'] == digit)).astype(int)
        # 最後に出現してからの経過回数
        df[f'digit_{digit}_since_last'] = digit_appeared.groupby((~digit_appeared.astype(bool)).cumsum()).cumcount()
    
    # ========== NEW: 高低バランス ==========
    df['high_count'] = df[['d1', 'd2', 'd3', 'd4']].apply(lambda x: sum(v >= 5 for v in x), axis=1)
    df['low_count'] = 4 - df['high_count']
    df['high_count_lag_1'] = df['high_count'].shift(1)

    # ========== v14.0 NEW: 桁間相関特徴量 ==========
    # 隣接桁の差（ボックスパターンの手がかり）
    df['diff_12'] = (df['d1'] - df['d2']).abs()
    df['diff_23'] = (df['d2'] - df['d3']).abs()
    df['diff_34'] = (df['d3'] - df['d4']).abs()
    df['diff_13'] = (df['d1'] - df['d3']).abs()
    df['diff_24'] = (df['d2'] - df['d4']).abs()
    df['diff_14'] = (df['d1'] - df['d4']).abs()

    # 桁の最大値・最小値・レンジ
    df['digit_max'] = df[['d1', 'd2', 'd3', 'd4']].max(axis=1)
    df['digit_min'] = df[['d1', 'd2', 'd3', 'd4']].min(axis=1)
    df['digit_range'] = df['digit_max'] - df['digit_min']

    # ソート済み桁（ボックスID的な特徴量）
    sorted_digits = df[['d1', 'd2', 'd3', 'd4']].apply(lambda x: sorted(x), axis=1, result_type='expand')
    sorted_digits.columns = ['sd1', 'sd2', 'sd3', 'sd4']
    df = pd.concat([df, sorted_digits], axis=1)

    # ソート済み桁のラグ
    for col in ['sd1', 'sd2', 'sd3', 'sd4']:
        df[f'{col}_lag_1'] = df[col].shift(1)
        df[f'{col}_lag_2'] = df[col].shift(2)

    # ボックスタイプの数値化（ABCD=4, AABC=3, AABB=2, AAAB=1, AAAA=0）
    df['box_type_num'] = df['unique_count']  # unique_countがそのままボックスタイプ指標
    df['box_type_num_lag_1'] = df['box_type_num'].shift(1)
    df['box_type_num_lag_2'] = df['box_type_num'].shift(2)

    # 桁の積（非線形パターン）
    df['prod_12'] = df['d1'] * df['d2']
    df['prod_34'] = df['d3'] * df['d4']

    # 前半と後半の合計差
    df['front_back_diff'] = (df['d1'] + df['d2']) - (df['d3'] + df['d4'])
    df['front_back_diff_lag_1'] = df['front_back_diff'].shift(1)

    # 隣接桁が同じかどうか
    df['adj_same_12'] = (df['d1'] == df['d2']).astype(int)
    df['adj_same_23'] = (df['d2'] == df['d3']).astype(int)
    df['adj_same_34'] = (df['d3'] == df['d4']).astype(int)

    # 桁の標準偏差（ばらつき指標）
    df['digit_std'] = df[['d1', 'd2', 'd3', 'd4']].std(axis=1)
    df['digit_std_lag_1'] = df['digit_std'].shift(1)

    # ========== v16.0 NEW: コールド/ホットナンバー特徴量 ==========
    # バックテストでcold_revival(19% BOX的中率)が最強だったため、
    # コールドナンバー情報をLightGBMに統合
    for digit in range(10):
        col_since = f'digit_{digit}_since_last'
        if col_since in df.columns:
            # コールド度（出現間隔が長い = コールド）
            df[f'digit_{digit}_is_cold'] = (df[col_since] >= 15).astype(int)
            # ホット度（出現間隔が短い = ホット）
            df[f'digit_{digit}_is_hot'] = (df[col_since] <= 3).astype(int)

    # 全桁のコールド数字数（0-4）
    cold_cols = [f'digit_{d}_is_cold' for d in range(10) if f'digit_{d}_is_cold' in df.columns]
    if cold_cols:
        # 現在の4桁に含まれるコールド数字の数
        def count_cold_in_number(row):
            count = 0
            for d in [int(row['d1']), int(row['d2']), int(row['d3']), int(row['d4'])]:
                col_name = f'digit_{d}_is_cold'
                if col_name in row.index and row[col_name] == 1:
                    count += 1
            return count
        df['cold_digit_count'] = df.apply(count_cold_in_number, axis=1)
        df['cold_digit_count_lag_1'] = df['cold_digit_count'].shift(1)

    # ========== v16.0 NEW: 曜日別パターン強化 ==========
    # 曜日ごとの合計値の傾向
    if 'dayofweek' in df.columns and 'sum' in df.columns:
        for dow in range(5):  # 月〜金
            mask = df['dayofweek'] == dow
            df[f'dow_{dow}_sum_mean'] = df.loc[mask, 'sum'].expanding().mean()
            df[f'dow_{dow}_sum_mean'] = df[f'dow_{dow}_sum_mean'].ffill()

    # ========== v16.0 NEW: ギャップ分析特徴量 ==========
    # 各桁の「前回値からの距離」のパターン
    for col in ['d1', 'd2', 'd3', 'd4']:
        diff_col = f'{col}_diff_1'
        if diff_col in df.columns:
            # 符号（上昇/下降トレンド）
            df[f'{col}_trend'] = df[diff_col].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0) if pd.notna(x) else 0)
            # 2回連続同方向かどうか
            df[f'{col}_trend_streak'] = (df[f'{col}_trend'] == df[f'{col}_trend'].shift(1)).astype(int)

    # ========== v16.0 NEW: ボックスパターン連続性 ==========
    # 前回と同じボックスタイプになるかどうかの手がかり
    if 'unique_count' in df.columns:
        df['box_type_same_as_prev'] = (df['unique_count'] == df['unique_count'].shift(1)).astype(int)
        # 過去5回でのABCD型(unique=4)の割合
        df['abcd_ratio_5'] = (df['unique_count'] == 4).astype(int).rolling(5).mean()
        df['abcd_ratio_10'] = (df['unique_count'] == 4).astype(int).rolling(10).mean()

    # Drop rows with NaN (due to shifting/rolling)
    df_clean = df.dropna().reset_index(drop=True)
    return df_clean

def train_and_get_digit_probabilities_lgbm(
    df: pd.DataFrame,
    temperature: float = DEFAULT_TEMPERATURE
) -> dict:
    """
    LightGBMモデルを学習し、次回予測の各桁(d1-d4)の確率分布を返す。

    Returns:
        {'d1': np.ndarray(10,), 'd2': ..., 'd3': ..., 'd4': ...}
    """
    # Prepare data
    df_features = create_features(df)

    if len(df_features) < 100:
        return {}

    target_cols = ['d1', 'd2', 'd3', 'd4']
    exclude_cols = target_cols + ['draw_date', 'numbers', 'winning_numbers', 'date', 'sum', 'draw_number']
    feature_cols = [c for c in df_features.columns if c not in exclude_cols and df_features[c].dtype in ['int64', 'float64', 'int32', 'float32']]

    X = df_features[feature_cols]
    y = df_features[target_cols]

    X_train = X.iloc[:-50]
    X_val = X.iloc[-50:]

    params = {
        'objective': 'multiclass',
        'num_class': 10,
        'metric': 'multi_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.03,          # 0.05→0.03 より慎重な学習
        'num_leaves': 63,               # 31→63 より複雑なパターンを捕捉
        'max_depth': 8,                 # 無制限→8 過学習防止
        'min_child_samples': 20,        # NEW: 葉の最小サンプル数
        'reg_alpha': 0.1,              # NEW: L1正則化（スパース特徴量選択）
        'reg_lambda': 1.0,             # NEW: L2正則化（過学習防止）
        'feature_fraction': 0.8,       # NEW: 特徴量サブサンプリング
        'bagging_fraction': 0.8,       # NEW: データサブサンプリング
        'bagging_freq': 5,             # NEW: バギング頻度
        'verbose': -1,
        'random_state': 42
    }

    models = {}
    for target in target_cols:
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
                lgb.log_evaluation(period=0)
            ]
        )
        models[target] = model

    # Build features for next draw by appending dummy row
    last_date = df_features['date'].iloc[-1]
    next_date = last_date + pd.Timedelta(days=1)

    dummy_row = pd.DataFrame({
        'draw_date': [next_date],
        'numbers': ['0000'],
        'd1': [0], 'd2': [0], 'd3': [0], 'd4': [0],
        'date': [next_date]
    })

    df_local = df.copy()
    if 'date' not in df_local.columns:
        df_local['date'] = df_features['date']

    df_extended = pd.concat([df_local, dummy_row], ignore_index=True)
    df_features_ext = create_features(df_extended)
    X_pred = df_features_ext[feature_cols].iloc[[-1]]

    preds_probs = {}
    for target in target_cols:
        raw_probs = models[target].predict(X_pred)[0]  # array of 10 probs
        preds_probs[target] = apply_temperature(raw_probs, temperature=temperature)

    return preds_probs

def train_and_predict_lgbm_with_probs(
    df: pd.DataFrame,
    limit: int = 15,
    temperature: float = DEFAULT_TEMPERATURE
):
    """
    LightGBMモデルを学習し、次回予測候補と各桁確率を返す。

    Returns:
        (generated_preds: List[str], preds_probs: Dict[str, np.ndarray])
    """
    preds_probs = train_and_get_digit_probabilities_lgbm(df, temperature=temperature)
    if not preds_probs:
        return [], {}

    generated_preds = []
    seen = set()

    attempts = 0
    max_attempts = max(50, limit * 50)
    while len(generated_preds) < limit and attempts < max_attempts:
        attempts += 1

        p_d1 = np.random.choice(10, p=preds_probs['d1'])
        p_d2 = np.random.choice(10, p=preds_probs['d2'])
        p_d3 = np.random.choice(10, p=preds_probs['d3'])
        p_d4 = np.random.choice(10, p=preds_probs['d4'])
        num_str = f"{p_d1}{p_d2}{p_d3}{p_d4}"

        if num_str not in seen:
            generated_preds.append(num_str)
            seen.add(num_str)

    return generated_preds, preds_probs

def train_and_predict_lgbm(
    df: pd.DataFrame,
    limit: int = 15,
    temperature: float = DEFAULT_TEMPERATURE
):
    """
    LightGBMモデルを学習し、次回予測を行う
    
    Args:
        df: 履歴データのDataFrame
        limit: 生成する予測数 (デフォルト: 15)
        temperature: 確率分布の温度パラメータ (デフォルト: 2.0)
    """
    generated_preds, _preds_probs = train_and_predict_lgbm_with_probs(df, limit=limit, temperature=temperature)
    return generated_preds

def predict_from_lightgbm(
    df: pd.DataFrame,
    limit: int = 15,
    temperature: float = DEFAULT_TEMPERATURE
):
    """
    Main entry point for LightGBM prediction
    
    Args:
        df: 履歴データのDataFrame
        limit: 生成する予測数 (デフォルト: 15)
        temperature: 確率分布の温度パラメータ (デフォルト: 2.0)
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
        if 'numbers' not in df_local.columns and 'winning_numbers' in df_local.columns:
            df_local['numbers'] = df_local['winning_numbers']

        # Run prediction
        return train_and_predict_lgbm(df_local, limit=limit, temperature=temperature)
        
    except Exception as e:
        print(f"[LightGBM] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def predict_from_lgbm_box(df: pd.DataFrame, limit: int = 150, temperature: float = 1.2):
    """
    v14.0 NEW: ボックスレベルLightGBM予測モデル

    各桁を独立に予測する従来モデルとは異なり、
    ソート済み4桁（ボックスID）の各桁を予測する。
    これにより桁間の組み合わせパターンを直接学習できる。

    Args:
        df: 履歴データのDataFrame
        limit: 生成する予測数
        temperature: 確率分布の温度（ボックス用は低めで精度重視）

    Returns:
        予測番号のリスト（各ボックスから1つの並びを生成）
    """
    try:
        df_local = df.copy()
        if 'draw_date' not in df_local.columns and 'date' in df_local.columns:
            df_local['draw_date'] = df_local['date']
        if 'numbers' not in df_local.columns and 'winning_numbers' in df_local.columns:
            df_local['numbers'] = df_local['winning_numbers']

        df_features = create_features(df_local)
        if len(df_features) < 100:
            return []

        # ソート済み桁をターゲットにする（sd1 <= sd2 <= sd3 <= sd4）
        target_cols = ['sd1', 'sd2', 'sd3', 'sd4']
        exclude_cols = ['d1', 'd2', 'd3', 'd4', 'sd1', 'sd2', 'sd3', 'sd4',
                        'draw_date', 'numbers', 'winning_numbers', 'date', 'sum', 'draw_number']
        feature_cols = [c for c in df_features.columns if c not in exclude_cols and df_features[c].dtype in ['int64', 'float64', 'int32', 'float32']]

        X = df_features[feature_cols]
        y = df_features[target_cols]
        X_train = X.iloc[:-50]
        X_val = X.iloc[-50:]

        params = {
            'objective': 'multiclass',
            'num_class': 10,
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'learning_rate': 0.03,
            'num_leaves': 63,
            'max_depth': 8,
            'min_child_samples': 20,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 123  # 異なるseedで多様性確保
        }

        models = {}
        for target in target_cols:
            y_train = y[target].iloc[:-50]
            y_val = y[target].iloc[-50:]
            train_set = lgb.Dataset(X_train, label=y_train)
            val_set = lgb.Dataset(X_val, label=y_val, reference=train_set)
            model = lgb.train(
                params, train_set,
                num_boost_round=1000,
                valid_sets=[train_set, val_set],
                callbacks=[
                    lgb.early_stopping(stopping_rounds=50, verbose=False),
                    lgb.log_evaluation(period=0)
                ]
            )
            models[target] = model

        # ダミー行で次回の特徴量を作成
        last_date = df_features['date'].iloc[-1]
        next_date = last_date + pd.Timedelta(days=1)
        dummy_row = pd.DataFrame({
            'draw_date': [next_date], 'numbers': ['0000'],
            'd1': [0], 'd2': [0], 'd3': [0], 'd4': [0], 'date': [next_date]
        })

        if 'date' not in df_local.columns:
            df_local['date'] = df_features['date']
        df_extended = pd.concat([df_local, dummy_row], ignore_index=True)
        df_features_ext = create_features(df_extended)
        X_pred = df_features_ext[feature_cols].iloc[[-1]]

        # 各ソート済み桁の確率分布を取得
        box_probs = {}
        for target in target_cols:
            raw_probs = models[target].predict(X_pred)[0]
            box_probs[target] = apply_temperature(raw_probs, temperature=temperature)

        # ボックス候補を生成（ソート制約付き）
        generated = []
        seen_boxes = set()
        rng = np.random.default_rng(42)
        max_attempts = limit * 30

        for _ in range(max_attempts):
            if len(generated) >= limit:
                break

            # 各桁をサンプリング
            sd1 = rng.choice(10, p=box_probs['sd1'])
            sd2 = rng.choice(10, p=box_probs['sd2'])
            sd3 = rng.choice(10, p=box_probs['sd3'])
            sd4 = rng.choice(10, p=box_probs['sd4'])

            # ソート制約を適用（sd1 <= sd2 <= sd3 <= sd4）
            digits = sorted([int(sd1), int(sd2), int(sd3), int(sd4)])
            box_id = ''.join(map(str, digits))

            if box_id not in seen_boxes:
                seen_boxes.add(box_id)
                # ボックスからランダムな並びを1つ生成
                shuffled = digits.copy()
                rng.shuffle(shuffled)
                num_str = ''.join(map(str, shuffled))
                generated.append(num_str)

        return generated

    except Exception as e:
        print(f"[LightGBM-Box] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


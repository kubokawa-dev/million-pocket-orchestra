"""
ナンバーズ4のオンライン学習を手動実行
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import psycopg2
import pandas as pd
from dotenv import load_dotenv
from numbers4.online_learning import evaluate_and_update
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_new_ml_model,
    predict_from_exploratory_heuristics,
    predict_from_extreme_patterns
)

load_dotenv()

# データベースから読み込み
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers4_draws ORDER BY draw_date ASC", conn)
conn.close()

df['d1'] = df['numbers'].str[0].astype(int)
df['d2'] = df['numbers'].str[1].astype(int)
df['d3'] = df['numbers'].str[2].astype(int)
df['d4'] = df['numbers'].str[3].astype(int)

# 最新4回分について評価
recent_draws = [
    (6839, '8607'),
    (6840, '2326'),
    (6841, '8612'),
    (6842, '4591'),
]

print('\n' + '='*60)
print('ナンバーズ4 オンライン学習を実行します...')
print('='*60)

for draw_number, numbers in recent_draws:
    print(f'\n第{draw_number}回（{numbers}）の評価中...')
    
    # この回を除いたデータで予測
    train_df = df[df['numbers'] != numbers].copy()
    
    # 予測を生成
    predictions_by_model = {
        'basic_stats': predict_from_basic_stats(train_df, 50),
        'advanced_heuristics': predict_from_advanced_heuristics(train_df, 50),
        'ml_model_new': predict_with_new_ml_model(train_df, 50),
        'exploratory': predict_from_exploratory_heuristics(train_df, 50),
        'extreme_patterns': predict_from_extreme_patterns(train_df, 50),
    }
    
    # 重みを更新
    evaluate_and_update(predictions_by_model, numbers, verbose=True)

print('\n✅ オンライン学習が完了しました！')
print('次回の予測では、調整された重みが自動的に使用されます。')
print('='*60)

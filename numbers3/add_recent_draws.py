import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# 第6844回を追加
new_draws = [
    (6844, '656', '2025-10-26'),
]

for draw_number, numbers, draw_date in new_draws:
    # 既に存在するか確認
    cursor.execute("SELECT draw_number FROM numbers3_draws WHERE draw_number = %s", (draw_number,))
    if cursor.fetchone():
        print(f'第{draw_number}回は既に登録されています')
    else:
        cursor.execute(
            "INSERT INTO numbers3_draws (draw_number, numbers, draw_date) VALUES (%s, %s, %s)",
            (draw_number, numbers, draw_date)
        )
        print(f'第{draw_number}回: {numbers} ({draw_date}) を追加しました')

conn.commit()

# 確認
cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers3_draws ORDER BY draw_number DESC LIMIT 5")
results = cursor.fetchall()
print('\n最新5件の抽選結果:')
for r in results:
    print(f'  第{r[0]}回: {r[2]} ({r[1]})')

conn.close()

# オンライン学習を実行（重みを自動調整）
if new_draws:
    print('\n' + '='*60)
    print('オンライン学習を実行します...')
    print('='*60)
    
    try:
        from numbers3.predict_ensemble import generate_ensemble_prediction
        from numbers3.online_learning import evaluate_and_update
        import pandas as pd
        
        # 最新の予測を取得（簡易版：直前のデータで予測）
        conn = psycopg2.connect(db_url)
        df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers3_draws ORDER BY draw_date ASC", conn)
        conn.close()
        
        df['d1'] = df['numbers'].str[0].astype(int)
        df['d2'] = df['numbers'].str[1].astype(int)
        df['d3'] = df['numbers'].str[2].astype(int)
        
        # 追加した各回について評価
        for draw_number, numbers, draw_date in new_draws:
            print(f'\n第{draw_number}回（{numbers}）の評価中...')
            
            # この回を除いたデータで予測
            train_df = df[df['numbers'] != numbers].copy()
            
            # 予測を生成（簡易版）
            from numbers3.prediction_logic import (
                predict_from_ultra_precision_recent_trend,
                predict_from_pattern_discovery,
                predict_from_comprehensive_patterns,
                predict_from_permutation_coverage,
                predict_with_ml_model,
                predict_from_exploratory_heuristics
            )
            
            predictions_by_model = {
                'ultra_precision_recent_trend': predict_from_ultra_precision_recent_trend(train_df, 50),
                'pattern_discovery': predict_from_pattern_discovery(train_df, 50),
                'comprehensive_patterns': predict_from_comprehensive_patterns(train_df, 30),
                'permutation_coverage': predict_from_permutation_coverage(train_df, 50),
                'ml_model': predict_with_ml_model(train_df, 15),
                'exploratory': predict_from_exploratory_heuristics(train_df, 20),
            }
            
            # 重みを更新
            evaluate_and_update(predictions_by_model, numbers, verbose=True)
        
        print('\n✅ オンライン学習が完了しました！')
        print('次回の予測では、調整された重みが自動的に使用されます。')
        print('='*60)
    
    except Exception as e:
        print(f'\n⚠️ オンライン学習でエラーが発生しました: {e}')
        print('予測システムは通常通り動作します。')
        print('='*60)

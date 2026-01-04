"""
最近の抽選結果を追加するスクリプト（SQLite版）
"""
import os
import sys

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection

# 第6844回を追加
new_draws = [
    (6844, '0017', '2025-10-26'),
]

conn = get_db_connection()
cursor = conn.cursor()

if not new_draws:
    print('⚠️ new_draws が空です。実際の当選番号を追加してください。')
    print('例:')
    print("new_draws = [")
    print("    (6839, '1234', '2025-10-21'),")
    print("    (6840, '5678', '2025-10-22'),")
    print("    (6841, '9012', '2025-10-23'),")
    print("    (6842, '3456', '2025-10-24'),")
    print("]")
else:
    for draw_number, numbers, draw_date in new_draws:
        # 既に存在するか確認
        cursor.execute("SELECT draw_number FROM numbers4_draws WHERE draw_number = ?", (draw_number,))
        if cursor.fetchone():
            print(f'第{draw_number}回は既に登録されています')
        else:
            cursor.execute(
                "INSERT INTO numbers4_draws (draw_number, numbers, draw_date) VALUES (?, ?, ?)",
                (draw_number, numbers, draw_date)
            )
            print(f'第{draw_number}回: {numbers} ({draw_date}) を追加しました')

    conn.commit()

    # 確認
    cursor.execute("SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT 5")
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
        from numbers4.online_learning import evaluate_and_update
        import pandas as pd
        
        # 最新の予測を取得（簡易版：直前のデータで予測）
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT draw_date, numbers FROM numbers4_draws ORDER BY draw_date ASC", conn)
        conn.close()
        
        df['d1'] = df['numbers'].str[0].astype(int)
        df['d2'] = df['numbers'].str[1].astype(int)
        df['d3'] = df['numbers'].str[2].astype(int)
        df['d4'] = df['numbers'].str[3].astype(int)
        
        # 追加した各回について評価
        for draw_number, numbers, draw_date in new_draws:
            print(f'\n第{draw_number}回（{numbers}）の評価中...')
            
            # この回を除いたデータで予測
            train_df = df[df['numbers'] != numbers].copy()
            
            # 予測を生成（簡易版）
            from numbers4.prediction_logic import (
                predict_from_basic_stats,
                predict_from_advanced_heuristics,
                predict_with_new_ml_model,
                predict_from_exploratory_heuristics,
                predict_from_extreme_patterns
            )
            
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
    
    except Exception as e:
        print(f'\n⚠️ オンライン学習でエラーが発生しました: {e}')
        print('予測システムは通常通り動作します。')
        print('='*60)

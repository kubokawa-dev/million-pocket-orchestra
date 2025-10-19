#!/usr/bin/env python3
"""
Supabaseへのデータ移行スクリプト
既存のPostgreSQLデータベースからSupabaseにデータを移行します
"""

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

def get_connection(db_url):
    """データベース接続を取得"""
    return psycopg2.connect(db_url)

def export_table_data(conn, table_name):
    """テーブルのデータをエクスポート"""
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql_query(query, conn)

def import_table_data(conn, table_name, df):
    """テーブルにデータをインポート"""
    if df.empty:
        print(f"  {table_name}: データなし")
        return
    
    # カラム名を取得
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    
    # データを挿入
    cursor = conn.cursor()
    for _, row in df.iterrows():
        try:
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                tuple(row.values)
            )
        except Exception as e:
            print(f"    エラー: {e}")
            continue
    
    conn.commit()
    cursor.close()
    print(f"  {table_name}: {len(df)}件のデータを移行")

def main():
    # 環境変数を読み込み
    load_dotenv()
    
    # 接続URL
    local_db_url = os.getenv('DATABASE_URL')
    supabase_db_url = os.getenv('SUPABASE_DATABASE_URL')
    
    if not supabase_db_url:
        print("❌ SUPABASE_DATABASE_URLが設定されていません")
        print("環境変数ファイルに以下を追加してください：")
        print("SUPABASE_DATABASE_URL=\"postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres\"")
        return
    
    print("🚀 Supabaseへのデータ移行を開始します...")
    
    # ローカルデータベースに接続
    print("📊 ローカルデータベースからデータを取得中...")
    local_conn = get_connection(local_db_url)
    
    # 移行対象のテーブル
    tables = [
        'numbers3_draws',
        'numbers4_draws', 
        'loto6_draws',
        'numbers3_model_events',
        'numbers4_model_events',
        'loto6_model_events',
        'numbers3_predictions_log',
        'numbers4_predictions_log',
        'loto6_predictions_log',
        'numbers3_ensemble_predictions',
        'numbers4_ensemble_predictions',
        'loto6_ensemble_predictions',
        'numbers3_prediction_candidates',
        'numbers4_prediction_candidates',
        'loto6_prediction_candidates'
    ]
    
    # Supabaseデータベースに接続
    print("☁️ Supabaseデータベースに接続中...")
    supabase_conn = get_connection(supabase_db_url)
    
    # 各テーブルのデータを移行
    for table in tables:
        try:
            print(f"📋 {table} を処理中...")
            
            # ローカルからデータを取得
            df = export_table_data(local_conn, table)
            
            # Supabaseにデータを移行
            import_table_data(supabase_conn, table, df)
            
        except Exception as e:
            print(f"  ⚠️ {table}: {e}")
            continue
    
    # 接続を閉じる
    local_conn.close()
    supabase_conn.close()
    
    print("✅ データ移行が完了しました！")

if __name__ == "__main__":
    main()

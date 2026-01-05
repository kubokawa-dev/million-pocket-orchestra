"""
PostgreSQLからSQLiteへのデータ移行スクリプト

使用方法:
1. PostgreSQLが動作している状態で実行
2. DATABASE_URL環境変数が設定されていること

python tools/migrate_to_sqlite.py
"""

import os
import sys
import sqlite3

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from tools.utils import DB_PATH, init_database

# PostgreSQL接続用（移行元）
try:
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("⚠️ psycopg2がインストールされていません。")
    print("   既存のPostgreSQLからの移行をスキップします。")


def get_postgres_connection():
    """PostgreSQL接続を取得"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return None
    if '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"⚠️ PostgreSQL接続エラー: {e}")
        return None


def migrate_table(pg_conn, sqlite_conn, table_name, columns):
    """テーブルのデータを移行"""
    pg_cur = pg_conn.cursor()
    sqlite_cur = sqlite_conn.cursor()
    
    # PostgreSQLからデータ取得
    try:
        pg_cur.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = pg_cur.fetchall()
    except Exception as e:
        print(f"  ⚠️ {table_name}: 取得エラー - {e}")
        return 0
    
    if not rows:
        print(f"  📭 {table_name}: データなし")
        return 0
    
    # SQLiteに挿入
    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    try:
        sqlite_cur.executemany(insert_sql, rows)
        sqlite_conn.commit()
        print(f"  ✅ {table_name}: {len(rows)}件 移行完了")
        return len(rows)
    except Exception as e:
        print(f"  ❌ {table_name}: 挿入エラー - {e}")
        return 0


def main():
    print("="*60)
    print("🔄 PostgreSQL → SQLite 移行ツール")
    print("="*60)
    
    # SQLiteデータベースを初期化
    print("\n[Step 1] SQLiteデータベースを初期化中...")
    init_database()
    
    sqlite_conn = sqlite3.connect(DB_PATH)
    
    # PostgreSQL接続を試行
    if not HAS_PSYCOPG2:
        print("\n[Step 2] PostgreSQLからの移行をスキップ（psycopg2なし）")
        sqlite_conn.close()
        print("\n✅ SQLiteデータベースの初期化が完了しました！")
        print(f"   📁 {DB_PATH}")
        return
    
    print("\n[Step 2] PostgreSQLに接続中...")
    pg_conn = get_postgres_connection()
    
    if not pg_conn:
        print("  ⚠️ PostgreSQLに接続できませんでした。")
        print("     新規のSQLiteデータベースとして初期化します。")
        sqlite_conn.close()
        print("\n✅ SQLiteデータベースの初期化が完了しました！")
        print(f"   📁 {DB_PATH}")
        return
    
    print("  ✅ PostgreSQL接続成功")
    
    # データ移行
    print("\n[Step 3] データ移行中...")
    
    tables = {
        'numbers3_draws': ['draw_number', 'draw_date', 'numbers'],
        'numbers4_draws': ['draw_number', 'draw_date', 'numbers'],
        'loto6_draws': ['draw_number', 'draw_date', 'numbers', 'bonus_number'],
        'numbers3_model_events': ['id', 'event_ts', 'actual_number', 'predictions', 'hit_exact', 'top_match', 'max_position_hits', 'notes'],
        'numbers4_model_events': ['id', 'event_ts', 'actual_number', 'predictions', 'hit_exact', 'top_match', 'max_position_hits', 'notes'],
        'loto6_model_events': ['id', 'event_ts', 'actual_number', 'predictions', 'hit_exact', 'top_match', 'max_position_hits', 'notes'],
        'numbers3_predictions_log': ['id', 'created_at', 'source', 'label', 'number', 'target_draw_number'],
        'numbers4_predictions_log': ['id', 'created_at', 'source', 'label', 'number', 'target_draw_number'],
        'loto6_predictions_log': ['id', 'created_at', 'source', 'label', 'number', 'target_draw_number'],
        'numbers3_ensemble_predictions': ['id', 'created_at', 'target_draw_number', 'model_updated_at', 'model_events_count', 
                                          'ensemble_weights', 'predictions_count', 'top_predictions', 'model_predictions',
                                          'actual_draw_number', 'actual_numbers', 'hit_status', 'hit_count', 'notes'],
        'numbers4_ensemble_predictions': ['id', 'created_at', 'target_draw_number', 'model_updated_at', 'model_events_count', 
                                          'ensemble_weights', 'predictions_count', 'top_predictions', 'model_predictions',
                                          'actual_draw_number', 'actual_numbers', 'hit_status', 'hit_count', 'notes'],
        'loto6_ensemble_predictions': ['id', 'created_at', 'target_draw_number', 'model_updated_at', 'model_events_count', 
                                       'ensemble_weights', 'predictions_count', 'top_predictions', 'model_predictions',
                                       'actual_draw_number', 'actual_numbers', 'actual_bonus_number', 'hit_status', 'hit_count', 'bonus_hit', 'notes'],
        'numbers3_prediction_candidates': ['id', 'ensemble_prediction_id', 'rank', 'number', 'score', 'contributing_models', 'created_at'],
        'numbers4_prediction_candidates': ['id', 'ensemble_prediction_id', 'rank', 'number', 'score', 'contributing_models', 'created_at'],
        'loto6_prediction_candidates': ['id', 'ensemble_prediction_id', 'rank', 'number', 'score', 'contributing_models', 'created_at'],
    }
    
    total_migrated = 0
    for table_name, columns in tables.items():
        count = migrate_table(pg_conn, sqlite_conn, table_name, columns)
        total_migrated += count
    
    # クリーンアップ
    pg_conn.close()
    sqlite_conn.close()
    
    print("\n" + "="*60)
    print(f"✅ 移行完了！合計 {total_migrated} 件のレコードを移行しました")
    print(f"   📁 SQLite: {DB_PATH}")
    print("="*60)
    
    print("\n📝 次のステップ:")
    print("   1. docker-compose down でPostgreSQLを停止")
    print("   2. 不要なNode.js関連ファイルを削除")
    print("   3. python tools/run_numbers4_pipeline.py でテスト")


if __name__ == '__main__':
    main()



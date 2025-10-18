"""
データベースマイグレーションを実行するスクリプト

使い方:
  python scripts/run_migration.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_connection():
    """データベース接続を取得"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL が設定されていません。")
        sys.exit(1)
    if '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)


def run_migration(migration_file: str):
    """マイグレーションSQLを実行"""
    if not os.path.exists(migration_file):
        print(f"❌ マイグレーションファイルが見つかりません: {migration_file}")
        return False
    
    print(f"\n📄 マイグレーションファイル: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("🔄 マイグレーションを実行中...")
        cur.execute(sql)
        conn.commit()
        print("✅ マイグレーション完了")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ マイグレーション失敗: {e}")
        return False
    finally:
        conn.close()


def verify_tables():
    """テーブルが正しく作成されたか確認"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("\n🔍 テーブルの確認...")
        
        # 予測履歴テーブルの確認
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('numbers4_ensemble_predictions', 'numbers4_prediction_candidates')
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        
        if len(tables) == 2:
            print("✅ 予測履歴テーブルが正しく作成されました:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # レコード数を確認
            cur.execute("SELECT COUNT(*) FROM numbers4_ensemble_predictions")
            count = cur.fetchone()[0]
            print(f"\n📊 numbers4_ensemble_predictions: {count}件")
            
            cur.execute("SELECT COUNT(*) FROM numbers4_prediction_candidates")
            count = cur.fetchone()[0]
            print(f"📊 numbers4_prediction_candidates: {count}件")
            
            return True
        else:
            print("⚠️  一部のテーブルが作成されていません。")
            return False
            
    except Exception as e:
        print(f"❌ テーブル確認エラー: {e}")
        return False
    finally:
        conn.close()


def main():
    print("\n" + "="*60)
    print("🚀 データベースマイグレーション")
    print("="*60)
    
    # マイグレーションファイルのパス
    migration_file = os.path.join(
        project_root,
        'prisma',
        'migrations',
        'add_prediction_history',
        'migration.sql'
    )
    
    # マイグレーション実行
    success = run_migration(migration_file)
    
    if success:
        # テーブル確認
        verify_tables()
        
        print("\n" + "="*60)
        print("✅ マイグレーションが正常に完了しました！")
        print("="*60)
        print("\n💡 次のステップ:")
        print("   1. 予測を実行: python numbers4/predict_ensemble.py")
        print("   2. 履歴を確認: python numbers4/manage_prediction_history.py list")
    else:
        print("\n" + "="*60)
        print("❌ マイグレーションに失敗しました。")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()

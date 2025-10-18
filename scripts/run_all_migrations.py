"""
すべてのマイグレーションを実行するスクリプト

使い方:
  python scripts/run_all_migrations.py
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


def run_migration(migration_name: str, migration_file: str):
    """マイグレーションSQLを実行"""
    if not os.path.exists(migration_file):
        print(f"⚠️  マイグレーションファイルが見つかりません: {migration_file}")
        return False
    
    print(f"\n📄 マイグレーション: {migration_name}")
    print(f"   ファイル: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("   🔄 実行中...")
        cur.execute(sql)
        conn.commit()
        print("   ✅ 完了")
        return True
    except Exception as e:
        conn.rollback()
        print(f"   ❌ 失敗: {e}")
        return False
    finally:
        conn.close()


def main():
    print("\n" + "="*60)
    print("🚀 データベースマイグレーション（全実行）")
    print("="*60)
    
    migrations_dir = os.path.join(project_root, 'prisma', 'migrations')
    
    # 実行するマイグレーションのリスト
    migrations = [
        {
            'name': '予測履歴テーブル追加',
            'path': os.path.join(migrations_dir, 'add_prediction_history', 'migration.sql')
        },
        {
            'name': 'predictions_logに対象抽選回カラム追加',
            'path': os.path.join(migrations_dir, 'add_target_draw_to_prediction_log', 'migration.sql')
        }
    ]
    
    success_count = 0
    fail_count = 0
    
    for migration in migrations:
        if run_migration(migration['name'], migration['path']):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*60)
    print(f"📊 マイグレーション結果")
    print("="*60)
    print(f"✅ 成功: {success_count}件")
    print(f"❌ 失敗: {fail_count}件")
    
    if fail_count == 0:
        print("\n🎉 すべてのマイグレーションが正常に完了しました！")
        
        # テーブル確認
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            print("\n🔍 テーブルの確認...")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'numbers4%'
                ORDER BY table_name
            """)
            
            tables = cur.fetchall()
            print(f"\n📊 Numbers4関連テーブル ({len(tables)}件):")
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cur.fetchone()[0]
                print(f"   - {table[0]}: {count}件")
            
        finally:
            conn.close()
        
        print("\n💡 次のステップ:")
        print("   1. 予測を実行: python numbers4/predict_ensemble.py")
        print("   2. 履歴を確認: python numbers4/manage_prediction_history.py list")
    else:
        print("\n⚠️  一部のマイグレーションに失敗しました。")
        print("   エラーメッセージを確認してください。")
        sys.exit(1)


if __name__ == '__main__':
    main()

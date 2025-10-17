"""
ナンバーズ4モデルを最新の当選番号で更新するスクリプト

使い方:
  python numbers4/update_model.py <当選番号>
  例: python numbers4/update_model.py 1234

または、DBから最新の当選番号を自動取得:
  python numbers4/update_model.py --auto
"""

import sys
import os
import argparse
import psycopg2
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from numbers4.learn_from_predictions import learn

load_dotenv()


def get_latest_number_from_db():
    """データベースから最新の当選番号を取得"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            ORDER BY draw_date DESC, draw_number DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        
        if row:
            draw_number, draw_date, numbers = row
            print(f"📊 最新の抽選結果: 第{draw_number}回 ({draw_date}) = {numbers}")
            return numbers
        else:
            print("❌ データベースに抽選結果が見つかりません。")
            return None
    except Exception as e:
        print(f"❌ データベースエラー: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='ナンバーズ4モデルを最新の当選番号で更新',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 手動で当選番号を指定
  python numbers4/update_model.py 1234
  
  # DBから最新の当選番号を自動取得
  python numbers4/update_model.py --auto
  
  # 複数回の当選番号を一括更新
  python numbers4/update_model.py 1234 5678 9012
        """
    )
    parser.add_argument(
        'numbers',
        nargs='*',
        help='4桁の当選番号（複数指定可）'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='DBから最新の当選番号を自動取得して更新'
    )
    
    args = parser.parse_args()
    
    numbers_to_learn = []
    
    if args.auto:
        # 自動取得モード
        latest = get_latest_number_from_db()
        if latest:
            numbers_to_learn.append(latest)
        else:
            print("⚠️  自動取得に失敗しました。手動で番号を指定してください。")
            sys.exit(1)
    elif args.numbers:
        # 手動指定モード
        numbers_to_learn = args.numbers
    else:
        # 引数なし：使い方を表示
        parser.print_help()
        print("\n💡 ヒント: --auto オプションで最新の当選番号を自動取得できます。")
        sys.exit(0)
    
    # 学習実行
    print(f"\n🔄 モデル更新を開始します... ({len(numbers_to_learn)}件)")
    print("="*60)
    
    for num in numbers_to_learn:
        num = str(num).strip()
        if len(num) != 4 or not num.isdigit():
            print(f"⚠️  スキップ: '{num}' は4桁の数字ではありません。")
            continue
        
        print(f"\n📝 学習中: {num}")
        try:
            learn(num)
            print(f"✅ 完了: {num}")
        except Exception as e:
            print(f"❌ エラー: {num} - {e}")
    
    print("\n" + "="*60)
    print("🎉 モデル更新が完了しました！")
    print("💡 次回の予測には最新データが反映されます。")
    print("   実行: python numbers4/predict_ensemble.py")


if __name__ == '__main__':
    main()

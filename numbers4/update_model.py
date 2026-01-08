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
import pandas as pd
import sqlite3
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from numbers4.learn_from_predictions import learn
from numbers4.online_learning import evaluate_and_update
from numbers4.prediction_logic import (
    predict_from_basic_stats,
    predict_from_advanced_heuristics,
    predict_with_new_ml_model,
    predict_from_exploratory_heuristics,
    predict_from_extreme_patterns
)
from tools.utils import get_db_connection, load_all_numbers4_draws

load_dotenv()


def get_latest_number_from_db():
    """データベースから最新の当選番号を取得（SQLite対応版）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # draw_date と draw_number の降順で最新1件を取得
        # numbers4_draws テーブルのカラム構成に依存
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            ORDER BY draw_date DESC, draw_number DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        
        if row:
            # SQLiteのRowオブジェクトまたはタプル
            draw_number = row['draw_number'] if isinstance(row, sqlite3.Row) else row[0]
            draw_date = row['draw_date'] if isinstance(row, sqlite3.Row) else row[1]
            numbers = row['numbers'] if isinstance(row, sqlite3.Row) else row[2]
            
            print(f"📊 最新の抽選結果: 第{draw_number}回 ({draw_date}) = {numbers}")
            return (draw_number, numbers)
        else:
            print("❌ データベースに抽選結果が見つかりません。")
            return None
    except Exception as e:
        print(f"❌ データベースエラー: {e}")
        return None


def run_online_learning_for_draw(draw_number, actual_number):
    """指定された回のデータを使ってオンライン学習（重み更新）を実行"""
    print(f"\n🧠 オンライン学習（重み更新）を実行中: 第{draw_number}回...")
    
    try:
        # 全データを読み込み
        df = load_all_numbers4_draws()
        if 'winning_numbers' in df.columns:
            df = df.rename(columns={'winning_numbers': 'numbers'})
            
        # 対象回より前のデータのみをトレーニングデータとする
        if 'draw_number' in df.columns:
            # draw_numberが正しく取得できていればフィルタリング
            train_df = df[df['draw_number'] < draw_number].copy()
        else:
            # 万が一draw_numberがない場合は、全データから対象の番号を含む行を除外
            # (同じ番号が過去にあった場合に問題になるが、緊急避難的措置)
            train_df = df[df['numbers'] != actual_number].copy()
            
        if train_df.empty:
            print("⚠️  学習用データが不足しているため、重み更新をスキップします。")
            return

        # 予測を生成（シミュレーション）
        limit = 50
        predictions_by_model = {
            'basic_stats': predict_from_basic_stats(train_df, limit),
            'advanced_heuristics': predict_from_advanced_heuristics(train_df, limit),
            'ml_model_new': predict_with_new_ml_model(train_df, limit),
            'exploratory': predict_from_exploratory_heuristics(train_df, limit),
            'extreme_patterns': predict_from_extreme_patterns(train_df, limit),
        }
        
        # 重みを更新
        evaluate_and_update(predictions_by_model, actual_number, verbose=True)
        
    except Exception as e:
        print(f"⚠️  オンライン学習中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


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
        numbers_to_learn = [(None, num) for num in args.numbers]
    else:
        # 引数なし：使い方を表示
        parser.print_help()
        print("\n💡 ヒント: --auto オプションで最新の当選番号を自動取得できます。")
        sys.exit(0)
    
    # 学習実行
    print(f"\n🔄 モデル更新を開始します... ({len(numbers_to_learn)}件)")
    print("="*60)
    
    for item in numbers_to_learn:
        if isinstance(item, tuple):
            draw_num, num = item
        else:
            draw_num, num = None, str(item)
        
        num = str(num).strip()
        if len(num) != 4 or not num.isdigit():
            print(f"⚠️  スキップ: '{num}' は4桁の数字ではありません。")
            continue
        
        if draw_num:
            print(f"\n📝 学習中: 第{draw_num}回 = {num}")
        else:
            print(f"\n📝 学習中: {num}")
        
        try:
            # 1. 確率分布の学習
            learn(num, draw_num)
            
            # 2. 重みの学習
            if draw_num:
                run_online_learning_for_draw(draw_num, num)
            else:
                print("⚠️  回号が不明なため、重み更新は慎重に行います（DB登録済みの番号を除外して予測）")
                run_online_learning_for_draw(99999, num)
                
            print(f"✅ 完了: {num}")
        except Exception as e:
            print(f"❌ エラー: {num} - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("🎉 モデル更新が完了しました！")
    print("💡 次回の予測には最新データが反映されます。")
    print("   実行: python numbers4/predict_ensemble.py")


if __name__ == '__main__':
    main()

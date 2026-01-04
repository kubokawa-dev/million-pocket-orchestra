"""
予測履歴を管理するCLIツール（SQLite版）

使い方:
  # 予測履歴を表示
  python numbers4/manage_prediction_history.py list
  
  # 特定の予測の詳細を表示
  python numbers4/manage_prediction_history.py show <prediction_id>
  
  # 予測結果を更新（当選番号が判明した後）
  python numbers4/manage_prediction_history.py update <prediction_id> <actual_numbers>
  
  # 統計情報を表示
  python numbers4/manage_prediction_history.py stats
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection
from numbers4.save_prediction_history import (
    get_prediction_history,
    update_prediction_result
)


def list_predictions(limit: int = 20):
    """予測履歴を一覧表示"""
    print("\n" + "="*80)
    print("📊 予測履歴")
    print("="*80)
    
    history = get_prediction_history(limit)
    
    if not history:
        print("予測履歴がありません。")
        return
    
    for h in history:
        created_at = h['created_at']
        if isinstance(created_at, datetime):
            created_at = created_at.strftime('%Y-%m-%d %H:%M')
        
        print(f"\n[ID: {h['id']}] {created_at}")
        print(f"  対象: 第{h['target_draw_number']}回" if h['target_draw_number'] else "  対象: 未設定")
        
        if h['top_predictions']:
            top5 = h['top_predictions'][:5]
            print(f"  上位5予測: {', '.join([p['number'] for p in top5])}")
        
        if h['actual_numbers']:
            status_emoji = {
                'exact': '🎯',
                'partial': '🎲',
                'miss': '❌'
            }.get(h['hit_status'], '❓')
            print(f"  結果: {status_emoji} {h['actual_numbers']} ({h['hit_status']}, {h['hit_count']}桁一致)")
        else:
            print(f"  結果: ⏳ 未判明")


def show_prediction_detail(prediction_id: int):
    """特定の予測の詳細を表示"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # アンサンブル予測を取得
        cur.execute("""
            SELECT 
                id, created_at, target_draw_number, model_updated_at, model_events_count,
                ensemble_weights, predictions_count, top_predictions, model_predictions,
                actual_draw_number, actual_numbers, hit_status, hit_count, notes
            FROM numbers4_ensemble_predictions 
            WHERE id = ?
        """, (prediction_id,))
        
        row = cur.fetchone()
        if not row:
            print(f"❌ 予測ID {prediction_id} が見つかりません。")
            return
        
        print("\n" + "="*80)
        print(f"📊 予測詳細 [ID: {row[0]}]")
        print("="*80)
        
        print(f"\n作成日時: {row[1]}")
        print(f"対象抽選回: 第{row[2]}回" if row[2] else "対象抽選回: 未設定")
        print(f"予測候補数: {row[6]}件")
        
        print(f"\n【モデル情報】")
        print(f"  モデル更新日時: {row[3]}")
        print(f"  学習イベント数: {row[4]}回")
        
        print(f"\n【アンサンブル重み】")
        weights = json.loads(row[5])
        for model, weight in weights.items():
            print(f"  {model}: {weight}")
        
        print(f"\n【上位10予測】")
        top_predictions = json.loads(row[7])
        for pred in top_predictions[:10]:
            print(f"  {pred['rank']:2d}位: {pred['number']} (スコア: {pred['score']:.2f})")
        
        print(f"\n【モデル別予測】")
        model_predictions = json.loads(row[8])
        for model, data in model_predictions.items():
            print(f"  {model}: {data['count']}件")
            print(f"    上位: {', '.join(data['predictions'][:5])}")
        
        if row[10]:  # actual_numbers
            print(f"\n【結果】")
            print(f"  実際の抽選回: 第{row[9]}回")
            print(f"  当選番号: {row[10]}")
            print(f"  的中状況: {row[11]} ({row[12]}桁一致)")
        else:
            print(f"\n【結果】")
            print(f"  ⏳ 未判明")
        
        if row[13]:  # notes
            print(f"\n【備考】")
            print(f"  {row[13]}")
        
        # 予測候補の詳細を取得
        cur.execute("""
            SELECT rank, number, score, contributing_models
            FROM numbers4_prediction_candidates
            WHERE ensemble_prediction_id = ?
            ORDER BY rank
            LIMIT 20
        """, (prediction_id,))
        
        candidates = cur.fetchall()
        if candidates:
            print(f"\n【予測候補の詳細（上位20件）】")
            for rank, number, score, models_json in candidates:
                models = json.loads(models_json)
                print(f"  {rank:2d}位: {number} (スコア: {score:.2f}) - モデル: {', '.join(models)}")
        
    finally:
        conn.close()


def show_statistics():
    """予測統計を表示"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("\n" + "="*80)
        print("📈 予測統計")
        print("="*80)
        
        # 総予測回数
        cur.execute("SELECT COUNT(*) FROM numbers4_ensemble_predictions")
        total_predictions = cur.fetchone()[0]
        print(f"\n総予測回数: {total_predictions}回")
        
        # 結果判明済みの予測
        cur.execute("""
            SELECT COUNT(*), hit_status, AVG(hit_count)
            FROM numbers4_ensemble_predictions
            WHERE actual_numbers IS NOT NULL
            GROUP BY hit_status
        """)
        
        results = cur.fetchall()
        if results:
            print(f"\n【的中統計】")
            for count, status, avg_hits in results:
                avg_hits_val = avg_hits if avg_hits else 0
                print(f"  {status}: {count}回 (平均{avg_hits_val:.2f}桁一致)")
        
        # 最近の予測精度
        cur.execute("""
            SELECT 
                target_draw_number, actual_numbers, hit_status, hit_count,
                top_predictions
            FROM numbers4_ensemble_predictions
            WHERE actual_numbers IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recent = cur.fetchall()
        if recent:
            print(f"\n【最近10回の結果】")
            for target, actual, status, hits, top_json in recent:
                top_preds = json.loads(top_json)
                top3 = [p['number'] for p in top_preds[:3]]
                status_emoji = {'exact': '🎯', 'partial': '🎲', 'miss': '❌'}.get(status, '❓')
                print(f"  第{target}回: {actual} {status_emoji} ({hits}桁) - 予測: {', '.join(top3)}")
        
        # 最も的中率の高い番号パターン
        cur.execute("""
            SELECT number, COUNT(*) as hit_count
            FROM numbers4_prediction_candidates c
            JOIN numbers4_ensemble_predictions p ON c.ensemble_prediction_id = p.id
            WHERE p.actual_numbers = c.number
            GROUP BY number
            ORDER BY hit_count DESC
            LIMIT 5
        """)
        
        top_numbers = cur.fetchall()
        if top_numbers:
            print(f"\n【完全一致した予測番号】")
            for number, count in top_numbers:
                print(f"  {number}: {count}回")
        
    finally:
        conn.close()


def update_result(prediction_id: int, actual_numbers: str):
    """予測結果を更新"""
    if len(actual_numbers) != 4 or not actual_numbers.isdigit():
        print(f"❌ エラー: 当選番号は4桁の数字で指定してください。")
        return
    
    # 対象の抽選回を取得
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT target_draw_number 
            FROM numbers4_ensemble_predictions 
            WHERE id = ?
        """, (prediction_id,))
        
        row = cur.fetchone()
        if not row:
            print(f"❌ 予測ID {prediction_id} が見つかりません。")
            return
        
        target_draw = row[0]
        
        # 結果を更新
        update_prediction_result(prediction_id, target_draw, actual_numbers)
        
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='予測履歴を管理するCLIツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 予測履歴を表示（最新20件）
  python numbers4/manage_prediction_history.py list
  
  # 予測履歴を表示（最新50件）
  python numbers4/manage_prediction_history.py list --limit 50
  
  # 特定の予測の詳細を表示
  python numbers4/manage_prediction_history.py show 123
  
  # 予測結果を更新（当選番号が判明した後）
  python numbers4/manage_prediction_history.py update 123 1234
  
  # 統計情報を表示
  python numbers4/manage_prediction_history.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # list コマンド
    list_parser = subparsers.add_parser('list', help='予測履歴を一覧表示')
    list_parser.add_argument('--limit', type=int, default=20, help='表示件数（デフォルト: 20）')
    
    # show コマンド
    show_parser = subparsers.add_parser('show', help='予測の詳細を表示')
    show_parser.add_argument('prediction_id', type=int, help='予測ID')
    
    # update コマンド
    update_parser = subparsers.add_parser('update', help='予測結果を更新')
    update_parser.add_argument('prediction_id', type=int, help='予測ID')
    update_parser.add_argument('actual_numbers', type=str, help='実際の当選番号（4桁）')
    
    # stats コマンド
    stats_parser = subparsers.add_parser('stats', help='統計情報を表示')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if args.command == 'list':
        list_predictions(args.limit)
    elif args.command == 'show':
        show_prediction_detail(args.prediction_id)
    elif args.command == 'update':
        update_result(args.prediction_id, args.actual_numbers)
    elif args.command == 'stats':
        show_statistics()


if __name__ == '__main__':
    main()

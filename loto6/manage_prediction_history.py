"""
ロト6の予測履歴を管理するCLIツール

使い方:
  # 予測履歴を表示
  python loto6/manage_prediction_history.py list
  
  # 特定の予測の詳細を表示
  python loto6/manage_prediction_history.py show <prediction_id>
  
  # 予測結果を更新（当選番号が判明した後）
  python loto6/manage_prediction_history.py update <prediction_id> <actual_numbers> <actual_bonus_number>
  
  # 統計情報を表示
  python loto6/manage_prediction_history.py stats
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

from loto6.save_prediction_history import (
    get_prediction_history,
    update_prediction_result,
    get_db_connection
)


def list_predictions(limit: int = 20):
    """予測履歴を一覧表示"""
    print("\n" + "="*80)
    print("ロト6 予測履歴")
    print("="*80)
    
    history = get_prediction_history(limit)
    
    if not history:
        print("予測履歴がありません。")
        return
    
    for h in history:
        created_at = h['created_at']
        if isinstance(created_at, datetime):
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        hit_status = h['hit_status'] or '未判定'
        hit_count = h['hit_count'] or 0
        bonus_hit = h['bonus_hit']
        actual_numbers = h['actual_numbers'] or '未確定'
        actual_bonus = h['actual_bonus_number'] or '未確定'
        
        bonus_status = '的中' if bonus_hit else '外れ' if bonus_hit is not None else '未判定'
        
        print(f"\n予測ID: {h['id']}")
        print(f"   作成日時: {created_at}")
        print(f"   対象回号: {h['target_draw_number'] or '不明'}")
        print(f"   予測候補数: {h['predictions_count']}件")
        print(f"   的中状況: {hit_status} ({hit_count}/6桁)")
        print(f"   ボーナス数字: {bonus_status}")
        print(f"   実際の番号: {actual_numbers}")
        print(f"   実際のボーナス: {actual_bonus}")
        if h['notes']:
            print(f"   備考: {h['notes']}")


def show_prediction_detail(prediction_id: int):
    """特定の予測の詳細を表示"""
    print(f"\n予測ID {prediction_id} の詳細")
    print("="*80)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # アンサンブル予測の詳細を取得
        cur.execute("""
            SELECT created_at, target_draw_number, model_updated_at, model_events_count,
                   ensemble_weights, predictions_count, top_predictions, model_predictions,
                   actual_draw_number, actual_numbers, actual_bonus_number,
                   hit_status, hit_count, bonus_hit, notes
            FROM loto6_ensemble_predictions
            WHERE id = %s
        """, (prediction_id,))
        
        row = cur.fetchone()
        if not row:
            print(f"予測ID {prediction_id} が見つかりません。")
            return
        
        (created_at, target_draw_number, model_updated_at, model_events_count,
         ensemble_weights, predictions_count, top_predictions, model_predictions,
         actual_draw_number, actual_numbers, actual_bonus_number,
         hit_status, hit_count, bonus_hit, notes) = row
        
        print(f"作成日時: {created_at}")
        print(f"対象回号: {target_draw_number}")
        print(f"モデル更新日時: {model_updated_at}")
        print(f"学習イベント数: {model_events_count}")
        print(f"予測候補数: {predictions_count}")
        print(f"実際の回号: {actual_draw_number}")
        print(f"実際の番号: {actual_numbers}")
        print(f"実際のボーナス: {actual_bonus_number}")
        print(f"的中状況: {hit_status} ({hit_count}/6桁)")
        print(f"ボーナス的中: {'的中' if bonus_hit else '外れ' if bonus_hit is not None else '未判定'}")
        print(f"備考: {notes}")
        
        # アンサンブル重みを表示
        if ensemble_weights:
            weights = json.loads(ensemble_weights)
            print(f"\nアンサンブル重み:")
            for model, weight in weights.items():
                print(f"   {model}: {weight}")
        
        # 上位予測を表示
        if top_predictions:
            predictions = json.loads(top_predictions)
            print(f"\n上位予測結果:")
            for i, pred in enumerate(predictions[:10], 1):
                print(f"   {i:2d}位: {pred['number']} (スコア: {pred['score']:.3f})")
        
        # モデル別予測を表示
        if model_predictions:
            model_preds = json.loads(model_predictions)
            print(f"\nモデル別予測:")
            for model, preds in model_preds.items():
                print(f"   {model}: {', '.join(preds[:5])}")
        
        # 予測候補の詳細を取得
        cur.execute("""
            SELECT rank, number, score, contributing_models
            FROM loto6_prediction_candidates
            WHERE ensemble_prediction_id = %s
            ORDER BY rank
            LIMIT 20
        """, (prediction_id,))
        
        candidates = cur.fetchall()
        if candidates:
            print(f"\n予測候補詳細 (上位20件):")
            for rank, number, score, contributing_models in candidates:
                models = json.loads(contributing_models) if contributing_models else []
                print(f"   {rank:2d}位: {number} (スコア: {score:.3f}) - モデル: {', '.join(models)}")
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_prediction(prediction_id: int, actual_numbers: str, actual_bonus_number: int):
    """予測結果を更新"""
    print(f"\n予測ID {prediction_id} の結果を更新中...")
    print(f"実際の番号: {actual_numbers}")
    print(f"実際のボーナス数字: {actual_bonus_number}")
    
    try:
        update_prediction_result(prediction_id, actual_numbers, actual_bonus_number)
        print("更新完了！")
    except Exception as e:
        print(f"更新エラー: {e}")


def show_statistics():
    """統計情報を表示"""
    print("\nロト6 予測統計")
    print("="*80)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 基本統計
        cur.execute("SELECT COUNT(*) FROM loto6_ensemble_predictions")
        total_predictions = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM loto6_ensemble_predictions WHERE hit_status IS NOT NULL")
        evaluated_predictions = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM loto6_ensemble_predictions WHERE hit_status = 'exact'")
        exact_hits = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM loto6_ensemble_predictions WHERE hit_status = 'partial'")
        partial_hits = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM loto6_ensemble_predictions WHERE bonus_hit = true")
        bonus_hits = cur.fetchone()[0]
        
        print(f"総予測数: {total_predictions}件")
        print(f"評価済み: {evaluated_predictions}件")
        print(f"完全一致: {exact_hits}件")
        print(f"部分一致: {partial_hits}件")
        print(f"ボーナス的中: {bonus_hits}件")
        
        if evaluated_predictions > 0:
            exact_rate = (exact_hits / evaluated_predictions) * 100
            partial_rate = (partial_hits / evaluated_predictions) * 100
            bonus_rate = (bonus_hits / evaluated_predictions) * 100
            print(f"完全一致率: {exact_rate:.1f}%")
            print(f"部分一致率: {partial_rate:.1f}%")
            print(f"ボーナス的中率: {bonus_rate:.1f}%")
        
        # 的中桁数の分布
        cur.execute("""
            SELECT hit_count, COUNT(*) 
            FROM loto6_ensemble_predictions 
            WHERE hit_count IS NOT NULL 
            GROUP BY hit_count 
            ORDER BY hit_count DESC
        """)
        
        hit_distribution = cur.fetchall()
        if hit_distribution:
            print(f"\n的中桁数分布:")
            for hit_count, count in hit_distribution:
                print(f"   {hit_count}桁: {count}件")
        
        # 最近の予測結果
        cur.execute("""
            SELECT id, target_draw_number, hit_status, hit_count, bonus_hit, actual_numbers, actual_bonus_number
            FROM loto6_ensemble_predictions
            WHERE hit_status IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recent_results = cur.fetchall()
        if recent_results:
            print(f"\n最近の予測結果 (最新10件):")
            for pred_id, target_draw, hit_status, hit_count, bonus_hit, actual_numbers, actual_bonus in recent_results:
                bonus_status = 'B' if bonus_hit else '-'
                print(f"   ID{pred_id}: 第{target_draw}回 → {actual_numbers}({actual_bonus}) [{hit_status}, {hit_count}/6桁, ボーナス{bonus_status}]")
        
    except Exception as e:
        print(f"統計取得エラー: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description='ロト6の予測履歴管理')
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # list コマンド
    list_parser = subparsers.add_parser('list', help='予測履歴を一覧表示')
    list_parser.add_argument('--limit', type=int, default=20, help='表示件数 (デフォルト: 20)')
    
    # show コマンド
    show_parser = subparsers.add_parser('show', help='特定の予測の詳細を表示')
    show_parser.add_argument('prediction_id', type=int, help='予測ID')
    
    # update コマンド
    update_parser = subparsers.add_parser('update', help='予測結果を更新')
    update_parser.add_argument('prediction_id', type=int, help='予測ID')
    update_parser.add_argument('actual_numbers', type=str, help='実際の当選番号 (6桁)')
    update_parser.add_argument('actual_bonus_number', type=int, help='実際のボーナス数字')
    
    # stats コマンド
    subparsers.add_parser('stats', help='統計情報を表示')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_predictions(args.limit)
    elif args.command == 'show':
        show_prediction_detail(args.prediction_id)
    elif args.command == 'update':
        update_prediction(args.prediction_id, args.actual_numbers, args.actual_bonus_number)
    elif args.command == 'stats':
        show_statistics()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

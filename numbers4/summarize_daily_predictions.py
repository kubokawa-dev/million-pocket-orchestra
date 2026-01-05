"""
同じ抽選回号の複数予測をまとめてMarkdownで出力するスクリプト

使い方:
  # 最新の抽選回号の予測をまとめる
  python numbers4/summarize_daily_predictions.py
  
  # 特定の抽選回号を指定
  python numbers4/summarize_daily_predictions.py --draw 6500
  
  # 出力ファイルを指定
  python numbers4/summarize_daily_predictions.py --output predictions/summary.md
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection


def get_predictions_for_draw(target_draw_number: int) -> List[Dict]:
    """指定した抽選回号の全予測を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                id, created_at, target_draw_number,
                top_predictions, model_predictions, ensemble_weights,
                actual_numbers, hit_status, hit_count
            FROM numbers4_ensemble_predictions 
            WHERE target_draw_number = ?
            ORDER BY created_at ASC
        """, (target_draw_number,))
        
        predictions = []
        for row in cur.fetchall():
            predictions.append({
                'id': row[0],
                'created_at': row[1],
                'target_draw_number': row[2],
                'top_predictions': json.loads(row[3]) if row[3] else [],
                'model_predictions': json.loads(row[4]) if row[4] else {},
                'ensemble_weights': json.loads(row[5]) if row[5] else {},
                'actual_numbers': row[6],
                'hit_status': row[7],
                'hit_count': row[8]
            })
        
        return predictions
    finally:
        conn.close()


def get_latest_target_draw() -> Optional[int]:
    """最新の予測対象回号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT target_draw_number 
            FROM numbers4_ensemble_predictions 
            WHERE target_draw_number IS NOT NULL
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def aggregate_predictions(predictions: List[Dict]) -> Dict:
    """複数予測を集計"""
    number_stats = defaultdict(lambda: {
        'appearances': 0,
        'total_score': 0.0,
        'best_rank': 999,
        'ranks': [],
        'times': []
    })
    
    total_predictions = len(predictions)
    
    for pred in predictions:
        created_at = pred['created_at']
        if isinstance(created_at, str):
            # ISO形式の時刻をパース
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = created_at[:16]
        else:
            time_str = str(created_at)
        
        for top_pred in pred['top_predictions']:
            number = top_pred['number']
            rank = top_pred['rank']
            score = top_pred['score']
            
            stats = number_stats[number]
            stats['appearances'] += 1
            stats['total_score'] += score
            stats['best_rank'] = min(stats['best_rank'], rank)
            stats['ranks'].append(rank)
            stats['times'].append(time_str)
    
    # 平均スコア・平均順位を計算
    for number, stats in number_stats.items():
        stats['avg_score'] = stats['total_score'] / stats['appearances']
        stats['avg_rank'] = sum(stats['ranks']) / len(stats['ranks'])
        stats['appearance_rate'] = stats['appearances'] / total_predictions * 100
    
    return dict(number_stats)


def generate_markdown(
    target_draw_number: int,
    predictions: List[Dict],
    aggregated: Dict,
    top_n: int = 20
) -> str:
    """Markdownレポートを生成"""
    
    # 結果情報
    actual_numbers = predictions[0]['actual_numbers'] if predictions else None
    hit_status = predictions[0]['hit_status'] if predictions else None
    
    # 予測時間の範囲
    times = [p['created_at'] for p in predictions]
    first_time = min(times) if times else "N/A"
    last_time = max(times) if times else "N/A"
    
    # ソート: 出現回数 → 平均スコア → 最高順位
    sorted_numbers = sorted(
        aggregated.items(),
        key=lambda x: (-x[1]['appearances'], -x[1]['avg_score'], x[1]['best_rank'])
    )
    
    # Markdown生成
    md = []
    
    # ヘッダー
    md.append(f"# 🎰 Numbers4 第{target_draw_number}回 予測サマリー")
    md.append("")
    
    # メタ情報
    md.append("## 📋 予測情報")
    md.append("")
    md.append(f"| 項目 | 内容 |")
    md.append(f"|:---|:---|")
    md.append(f"| 対象回号 | 第{target_draw_number}回 |")
    md.append(f"| 予測回数 | {len(predictions)}回 |")
    
    # 時刻表示を整形
    def format_time(t):
        if isinstance(t, str):
            try:
                dt = datetime.fromisoformat(t.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M JST')
            except:
                return t[:16]
        return str(t)
    
    md.append(f"| 予測期間 | {format_time(first_time)} ～ {format_time(last_time)} |")
    md.append(f"| 集計候補数 | {len(aggregated)}種類 |")
    md.append("")
    
    # 結果（判明している場合）
    if actual_numbers:
        status_emoji = {
            'exact': '🎯 完全一致！',
            'box': '📦 ボックス一致',
            'partial': '🎲 部分一致',
            'miss': '❌ ハズレ'
        }.get(hit_status, '❓ 不明')
        
        md.append("## 🏆 抽選結果")
        md.append("")
        md.append(f"**当選番号: `{actual_numbers}`** {status_emoji}")
        md.append("")
        
        # 当選番号が予測に含まれていたかチェック
        if actual_numbers in aggregated:
            stats = aggregated[actual_numbers]
            md.append(f"> ✨ この番号は {stats['appearances']}/{len(predictions)}回 の予測で出現！")
            md.append(f"> 最高順位: {stats['best_rank']}位 / 平均順位: {stats['avg_rank']:.1f}位")
            md.append("")
    
    # 安定上位予測（メインのランキング）
    md.append("## 🔥 安定上位予測 TOP20")
    md.append("")
    md.append("複数回の予測で安定して上位に登場した番号をランキング！")
    md.append("")
    md.append("| 順位 | 番号 | 出現率 | 平均スコア | 最高順位 | 安定度 |")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for rank, (number, stats) in enumerate(sorted_numbers[:top_n], 1):
        appearance_rate = stats['appearance_rate']
        avg_score = stats['avg_score']
        best_rank = stats['best_rank']
        
        # 安定度の計算（出現率 × 平均順位の逆数）
        stability = appearance_rate * (21 - min(stats['avg_rank'], 20)) / 20
        
        # 絵文字でハイライト
        if rank <= 3:
            rank_emoji = ['🥇', '🥈', '🥉'][rank - 1]
        elif appearance_rate >= 80:
            rank_emoji = '⭐'
        else:
            rank_emoji = ''
        
        # 当選番号にマーク
        number_display = f"**{number}**" if actual_numbers and number == actual_numbers else number
        
        md.append(f"| {rank_emoji} {rank} | `{number_display}` | {appearance_rate:.0f}% ({stats['appearances']}/{len(predictions)}) | {avg_score:.2f} | {best_rank}位 | {stability:.1f} |")
    
    md.append("")
    
    # 予測時刻別の上位番号
    md.append("## ⏰ 時刻別 TOP3 予測")
    md.append("")
    md.append("| 予測時刻 | 1位 | 2位 | 3位 |")
    md.append("|:---:|:---:|:---:|:---:|")
    
    for pred in predictions:
        created_at = pred['created_at']
        if isinstance(created_at, str):
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = created_at[11:16]
        else:
            time_str = str(created_at)
        
        top3 = pred['top_predictions'][:3]
        top3_str = [f"`{p['number']}`" for p in top3]
        while len(top3_str) < 3:
            top3_str.append("-")
        
        md.append(f"| {time_str} | {top3_str[0]} | {top3_str[1]} | {top3_str[2]} |")
    
    md.append("")
    
    # 出現パターン分析
    md.append("## 📊 出現パターン分析")
    md.append("")
    
    # 常連番号（80%以上で出現）
    regulars = [(n, s) for n, s in sorted_numbers if s['appearance_rate'] >= 80]
    if regulars:
        md.append("### 🌟 常連番号（80%以上で出現）")
        md.append("")
        md.append(", ".join([f"`{n}`" for n, _ in regulars]))
        md.append("")
    
    # 新顔番号（1回のみ出現で上位）
    newcomers = [(n, s) for n, s in sorted_numbers if s['appearances'] == 1 and s['best_rank'] <= 5]
    if newcomers:
        md.append("### 🆕 注目の新顔（1回のみ出現・TOP5入り）")
        md.append("")
        md.append(", ".join([f"`{n}` (#{s['best_rank']})" for n, s in newcomers[:10]]))
        md.append("")
    
    # 各桁の頻出数字
    md.append("### 🔢 各桁の頻出数字")
    md.append("")
    
    digit_freq = [Counter() for _ in range(4)]
    for number, stats in sorted_numbers[:50]:  # 上位50番号で集計
        for i, d in enumerate(number):
            digit_freq[i][d] += stats['appearances']
    
    md.append("| 桁 | 1位 | 2位 | 3位 |")
    md.append("|:---:|:---:|:---:|:---:|")
    
    for i, freq in enumerate(digit_freq):
        top3 = freq.most_common(3)
        top3_str = [f"{d} ({c}回)" for d, c in top3]
        while len(top3_str) < 3:
            top3_str.append("-")
        md.append(f"| {i+1}桁目 | {top3_str[0]} | {top3_str[1]} | {top3_str[2]} |")
    
    md.append("")
    
    # フッター
    md.append("---")
    md.append("")
    md.append(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Million Pocket 🎰*")
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description='同じ抽選回号の複数予測をまとめてMarkdownで出力'
    )
    parser.add_argument(
        '--draw', '-d', type=int,
        help='対象の抽選回号（未指定時は最新）'
    )
    parser.add_argument(
        '--output', '-o', type=str,
        help='出力ファイルパス（未指定時は標準出力）'
    )
    parser.add_argument(
        '--top', '-t', type=int, default=20,
        help='表示する上位予測数（デフォルト: 20）'
    )
    
    args = parser.parse_args()
    
    # 対象回号を決定
    target_draw = args.draw
    if not target_draw:
        target_draw = get_latest_target_draw()
        if not target_draw:
            print("❌ 予測データが見つかりません。")
            sys.exit(1)
    
    print(f"📊 第{target_draw}回の予測を集計中...")
    
    # 予測データを取得
    predictions = get_predictions_for_draw(target_draw)
    
    if not predictions:
        print(f"❌ 第{target_draw}回の予測データが見つかりません。")
        sys.exit(1)
    
    print(f"   ✅ {len(predictions)}件の予測を発見")
    
    # 集計
    aggregated = aggregate_predictions(predictions)
    print(f"   ✅ {len(aggregated)}種類の番号を集計")
    
    # Markdown生成
    markdown = generate_markdown(target_draw, predictions, aggregated, args.top)
    
    # 出力
    if args.output:
        # ディレクトリを作成
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"   ✅ {args.output} に出力しました")
    else:
        print("\n" + "="*60)
        print(markdown)


if __name__ == '__main__':
    main()


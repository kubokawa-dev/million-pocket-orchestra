"""
JSONファイルから予測データを読み込んでMarkdownサマリーを生成

使い方:
  python numbers4/summarize_from_json.py --draw 6891 --output predictions/numbers4_6891.md
  python numbers4/summarize_from_json.py --date 20260105 --output predictions/summary.md  # 後方互換
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 共通ユーティリティからインポート
from numbers4.prediction_utils import (
    get_predictions_dir,
    load_predictions_by_draw,
    load_daily_predictions,
)


def aggregate_predictions(daily_data: Dict) -> Dict:
    """1日分の予測を集計"""
    predictions = daily_data.get('predictions', [])
    
    if not predictions:
        return {}
    
    number_stats = defaultdict(lambda: {
        'appearances': 0,
        'total_score': 0.0,
        'best_rank': 999,
        'ranks': [],
        'times': [],
        'similar_patterns': []  # 類似パターンを追加
    })
    
    total_predictions = len(predictions)
    
    for pred_entry in predictions:
        time_str = pred_entry.get('time_jst', pred_entry.get('time', '')[:16])
        
        for pred in pred_entry.get('top_predictions', []):
            number = pred['number']
            rank = pred['rank']
            score = pred['score']
            similar = pred.get('similar_patterns', [])  # 類似パターンを取得
            
            stats = number_stats[number]
            stats['appearances'] += 1
            stats['total_score'] += score
            stats['best_rank'] = min(stats['best_rank'], rank)
            stats['ranks'].append(rank)
            stats['times'].append(time_str)
            
            # 類似パターンを追加（重複排除）
            for sp in similar:
                if sp not in stats['similar_patterns']:
                    stats['similar_patterns'].append(sp)
    
    # 平均スコア・平均順位を計算
    for _number, stats in number_stats.items():
        stats['avg_score'] = stats['total_score'] / stats['appearances']
        stats['avg_rank'] = sum(stats['ranks']) / len(stats['ranks'])
        stats['appearance_rate'] = stats['appearances'] / total_predictions * 100
    
    return dict(number_stats)


def generate_markdown(daily_data: Dict, aggregated: Dict, top_n: int = 20) -> str:
    """Markdownレポートを生成"""
    
    target_draw_number = daily_data.get('target_draw_number', '???')
    predictions = daily_data.get('predictions', [])
    
    # 予測時間の範囲
    times = [p.get('time_jst', p.get('time', '')) for p in predictions]
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
    md.append("| 項目 | 内容 |")
    md.append("|:---|:---|")
    md.append(f"| 対象回号 | 第{target_draw_number}回 |")
    md.append(f"| 予測回数 | {len(predictions)}回 |")
    md.append(f"| 予測期間 | {first_time} ～ {last_time} |")
    md.append(f"| 集計候補数 | {len(aggregated)}種類 |")
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
        
        md.append(f"| {rank_emoji} {rank} | `{number}` | {appearance_rate:.0f}% ({stats['appearances']}/{len(predictions)}) | {avg_score:.2f} | {best_rank}位 | {stability:.1f} |")
    
    md.append("")
    
    # 予測時刻別の上位番号
    md.append("## ⏰ 時刻別 TOP3 予測")
    md.append("")
    md.append("| 予測時刻 | 1位 | 2位 | 3位 |")
    md.append("|:---:|:---:|:---:|:---:|")
    
    for pred_entry in predictions:
        time_str = pred_entry.get('time_jst', pred_entry.get('time', '')[:16])
        top3 = pred_entry.get('top_predictions', [])[:3]
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
    
    # 類似パターン提案セクション（新規追加）
    md.append("## 💡 上位予測 + 類似パターン")
    md.append("")
    md.append("各予測番号に対して、統計分析に基づく類似パターンを提案！")
    md.append("ボックスやセットで購入する際の参考にしてね！")
    md.append("")
    
    # 最新の予測から類似パターンを取得
    latest_predictions = predictions[-1].get('top_predictions', []) if predictions else []
    
    if latest_predictions:
        md.append("| 順位 | メイン予測 | スコア | 類似パターン（もしかしたらこれも？） |")
        md.append("|:---:|:---:|:---:|:---|")
        
        for pred in latest_predictions[:10]:  # 上位10件
            number = pred['number']
            score = pred['score']
            rank = pred['rank']
            similar = pred.get('similar_patterns', [])
            
            # 絵文字でハイライト
            if rank <= 3:
                rank_emoji = ['🥇', '🥈', '🥉'][rank - 1]
            else:
                rank_emoji = ''
            
            # 類似パターンを整形
            if similar:
                similar_str = ", ".join([f"`{sp['number']}`" for sp in similar[:3]])
            else:
                similar_str = "-"
            
            md.append(f"| {rank_emoji} {rank} | `{number}` | {score:.1f} | {similar_str} |")
        
        md.append("")
        
        # 類似パターンの詳細説明（上位5件）
        md.append("### 📝 類似パターン詳細（上位5件）")
        md.append("")
        
        for pred in latest_predictions[:5]:
            number = pred['number']
            similar = pred.get('similar_patterns', [])
            
            if similar:
                md.append(f"**`{number}`** の類似パターン:")
                md.append("")
                for sp in similar:
                    sp_number = sp.get('number', '')
                    sp_desc = sp.get('description', '')
                    md.append(f"- `{sp_number}`: {sp_desc}")
                md.append("")
    else:
        md.append("（類似パターンデータなし）")
        md.append("")
    
    # フッター
    md.append("---")
    md.append("")
    md.append(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Million Pocket 🎰*")
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description='JSONから予測データを読み込んでMarkdownサマリーを生成'
    )
    parser.add_argument(
        '--draw', type=int,
        help='対象抽選回号（優先）'
    )
    parser.add_argument(
        '--date', '-d', type=str,
        help='対象日（YYYYMMDD形式）- 後方互換性用'
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
    
    # 予測データを読み込み（回号優先、なければ日付）
    if args.draw:
        daily_data = load_predictions_by_draw(args.draw)
        print(f"🎯 第{args.draw}回の予測データを読み込み中...")
    else:
        daily_data = load_daily_predictions(args.date)
    
    if not daily_data:
        print("❌ 予測データが見つかりません")
        sys.exit(1)
    
    predictions = daily_data.get('predictions', [])
    print(f"📊 {len(predictions)}件の予測を発見")
    
    # 集計
    aggregated = aggregate_predictions(daily_data)
    print(f"   ✅ {len(aggregated)}種類の番号を集計")
    
    # Markdown生成
    markdown = generate_markdown(daily_data, aggregated, args.top)
    
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



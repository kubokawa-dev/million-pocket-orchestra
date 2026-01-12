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


def get_box_type(number: str) -> tuple:
    """
    番号のボックスタイプを判定
    Returns: (type_name, box_patterns_count, description)
    """
    digits = list(number)
    unique_count = len(set(digits))
    digit_counts = Counter(digits)
    max_count = max(digit_counts.values())
    
    if unique_count == 1:
        # 全部同じ（ゾロ目）: 1111
        return ("ゾロ目", 1, "ストレートのみ")
    elif unique_count == 2:
        if max_count == 3:
            # トリプル: 1112
            return ("トリプル", 4, "4通り")
        else:
            # ダブルダブル: 1122 or ダブル: 1123
            if max_count == 2 and list(digit_counts.values()).count(2) == 2:
                return ("ダブルダブル", 6, "6通り")
            else:
                return ("ダブル", 12, "12通り")
    elif unique_count == 3:
        # ダブル: 1123
        return ("ダブル", 12, "12通り")
    else:
        # シングル: 1234
        return ("シングル", 24, "24通り")


def calculate_budget_recommendations(daily_data: Dict, aggregated: Dict, budget: int = 1000) -> List[Dict]:
    """
    予算に基づいておすすめ番号を計算
    
    Args:
        daily_data: 予測データ
        aggregated: 集計データ
        budget: 予算（円）デフォルト1000円
    
    Returns:
        おすすめ番号のリスト
    """
    predictions = daily_data.get('predictions', [])
    price_per_ticket = 200  # 1口200円
    max_tickets = budget // price_per_ticket
    
    # 全候補を収集してスコアリング
    candidates = []
    
    # 1. メイン予測から候補を収集
    for number, stats in aggregated.items():
        box_type, box_count, box_desc = get_box_type(number)
        
        # 総合スコアを計算
        # - 出現率が高い = 安定している
        # - 平均スコアが高い = 予測精度が高い
        # - ボックス通り数が多い = 当選確率UP
        composite_score = (
            stats['appearance_rate'] * 0.3 +  # 出現率の重み
            stats['avg_score'] * 0.4 +         # 平均スコアの重み
            (21 - stats['best_rank']) * 2 +    # 最高順位の重み
            box_count * 0.5                     # ボックス通り数ボーナス
        )
        
        candidates.append({
            'number': number,
            'source': 'main',
            'composite_score': composite_score,
            'appearance_rate': stats['appearance_rate'],
            'avg_score': stats['avg_score'],
            'best_rank': stats['best_rank'],
            'box_type': box_type,
            'box_count': box_count,
            'box_desc': box_desc,
        })
    
    # 2. ML分布サンプリング(近傍探索)から候補を収集
    ml_sampling_patterns = {}
    for pred_entry in predictions:
        for pred in pred_entry.get('top_predictions', []):
            similar = pred.get('similar_patterns', [])
            for sp in similar:
                sp_desc = sp.get('description', '')
                if 'ML分布サンプリング(近傍探索)' in sp_desc:
                    sp_number = sp.get('number', '')
                    sp_score = sp.get('score', 0)
                    
                    if sp_number not in ml_sampling_patterns:
                        ml_sampling_patterns[sp_number] = {
                            'count': 0,
                            'scores': [],
                            'parent_numbers': []
                        }
                    ml_sampling_patterns[sp_number]['count'] += 1
                    ml_sampling_patterns[sp_number]['scores'].append(sp_score)
                    ml_sampling_patterns[sp_number]['parent_numbers'].append(pred['number'])
    
    for number, data in ml_sampling_patterns.items():
        box_type, box_count, box_desc = get_box_type(number)
        avg_ml_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        
        # 既にメイン予測にある場合はボーナスを追加
        if number in aggregated:
            main_stats = aggregated[number]
            # メイン予測とML近傍探索の両方に出現 = 超有力候補！
            composite_score = (
                main_stats['appearance_rate'] * 0.3 +
                main_stats['avg_score'] * 0.4 +
                (21 - main_stats['best_rank']) * 2 +
                box_count * 0.5 +
                data['count'] * 10  # ML近傍探索ボーナス（大きめ）
            )
            # 既存の候補を更新
            for c in candidates:
                if c['number'] == number:
                    c['composite_score'] = composite_score
                    c['ml_count'] = data['count']
                    c['source'] = 'both'  # 両方に出現
                    break
        else:
            # ML近傍探索のスコアリング（重みを大幅UP）
            composite_score = (
                data['count'] * 8 +                 # 出現回数の重み（UP）
                (-avg_ml_score) * 3 +               # MLスコア（負の値なので反転）
                box_count * 1.0                     # ボックス通り数ボーナス（UP）
            )
            
            candidates.append({
                'number': number,
                'source': 'ml_sampling',
                'composite_score': composite_score,
                'appearance_rate': 0,
                'avg_score': avg_ml_score,
                'best_rank': 999,
                'ml_count': data['count'],
                'box_type': box_type,
                'box_count': box_count,
                'box_desc': box_desc,
            })
    
    # スコアでソート
    candidates.sort(key=lambda x: -x['composite_score'])
    
    # ゾロ目を除外（当たりにくいので）
    candidates = [c for c in candidates if c['box_type'] != 'ゾロ目']
    
    # 多様性を確保するため、ボックスタイプのバランスを取る
    # ダブル（12通り）とシングル（24通り）を優先
    selected = []
    type_counts = {'シングル': 0, 'ダブル': 0, 'ダブルダブル': 0, 'トリプル': 0}
    
    # タイプ別の優先度と上限を設定
    type_priority = {
        'シングル': {'limit_ratio': 0.4, 'priority': 2},      # 24通りカバー
        'ダブル': {'limit_ratio': 0.4, 'priority': 1},        # 12通りカバー（6511タイプ）
        'ダブルダブル': {'limit_ratio': 0.15, 'priority': 3}, # 6通りカバー
        'トリプル': {'limit_ratio': 0.05, 'priority': 4},     # 4通りカバー
    }
    
    for candidate in candidates:
        if len(selected) >= max_tickets:
            break
        
        box_type = candidate['box_type']
        type_info = type_priority.get(box_type, {'limit_ratio': 0.1, 'priority': 5})
        
        # 各タイプの上限を設定
        type_limit = max(1, int(max_tickets * type_info['limit_ratio']) + 1)
        
        if type_counts.get(box_type, 0) < type_limit:
            selected.append(candidate)
            type_counts[box_type] = type_counts.get(box_type, 0) + 1
    
    # 枠が余っていたら、スコア順で追加
    for candidate in candidates:
        if len(selected) >= max_tickets:
            break
        if candidate not in selected:
            selected.append(candidate)
    
    return selected


def generate_markdown(daily_data: Dict, aggregated: Dict, top_n: int = 20, budget: int = 1000) -> str:
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
    
    # ========================================
    # 🔮 ML分布サンプリング(近傍探索) 全抽出セクション
    # ========================================
    md.append("## 🔮 ML分布サンプリング(近傍探索) 全リスト")
    md.append("")
    md.append("すべての予測から「ML分布サンプリング(近傍探索)」パターンを抽出！")
    md.append("機械学習モデルが示唆する隠れた有力候補たち！✨")
    md.append("")
    
    # 全予測からML分布サンプリング(近傍探索)を抽出
    ml_sampling_patterns = {}  # {番号: {'count': 出現回数, 'parent_numbers': [親番号リスト], 'scores': [スコアリスト]}}
    
    for pred_entry in predictions:
        for pred in pred_entry.get('top_predictions', []):
            parent_number = pred['number']
            similar = pred.get('similar_patterns', [])
            
            for sp in similar:
                sp_desc = sp.get('description', '')
                if 'ML分布サンプリング(近傍探索)' in sp_desc:
                    sp_number = sp.get('number', '')
                    sp_score = sp.get('score', 0)
                    
                    if sp_number not in ml_sampling_patterns:
                        ml_sampling_patterns[sp_number] = {
                            'count': 0,
                            'parent_numbers': [],
                            'scores': []
                        }
                    
                    ml_sampling_patterns[sp_number]['count'] += 1
                    if parent_number not in ml_sampling_patterns[sp_number]['parent_numbers']:
                        ml_sampling_patterns[sp_number]['parent_numbers'].append(parent_number)
                    ml_sampling_patterns[sp_number]['scores'].append(sp_score)
    
    if ml_sampling_patterns:
        # 出現回数でソート（多い順）
        sorted_ml_patterns = sorted(
            ml_sampling_patterns.items(),
            key=lambda x: (-x[1]['count'], min(x[1]['scores']))
        )
        
        md.append(f"**抽出数: {len(ml_sampling_patterns)}件**")
        md.append("")
        md.append("| 番号 | 出現回数 | 平均スコア | 関連予測番号 |")
        md.append("|:---:|:---:|:---:|:---|")
        
        for sp_number, data in sorted_ml_patterns:
            count = data['count']
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            parent_str = ", ".join([f"`{p}`" for p in data['parent_numbers'][:5]])
            if len(data['parent_numbers']) > 5:
                parent_str += f" 他{len(data['parent_numbers']) - 5}件"
            
            # 出現回数が多いものにハイライト
            if count >= 5:
                highlight = "🔥"
            elif count >= 3:
                highlight = "⭐"
            else:
                highlight = ""
            
            md.append(f"| {highlight} `{sp_number}` | {count}回 | {avg_score:.2f} | {parent_str} |")
        
        md.append("")
        
        # 上位10件の詳細
        md.append("### 🎯 注目のML近傍探索パターン TOP10")
        md.append("")
        
        for i, (sp_number, data) in enumerate(sorted_ml_patterns[:10], 1):
            count = data['count']
            scores = data['scores']
            parents = data['parent_numbers']
            
            md.append(f"**{i}. `{sp_number}`** - {count}回出現")
            md.append(f"   - スコア範囲: {min(scores):.2f} ～ {max(scores):.2f}")
            md.append(f"   - 関連予測: {', '.join([f'`{p}`' for p in parents[:10]])}")
            md.append("")
    else:
        md.append("（ML分布サンプリング(近傍探索)パターンなし）")
        md.append("")
    
    # ========================================
    # 🔥 魂予測セクション
    # ========================================
    md.append("## 🔥 魂予測 - ズバリ当選番号！")
    md.append("")
    md.append("「類似パターン」じゃない。**これが当たる番号だ！**")
    md.append("")
    
    try:
        from numbers4.soul_predictor import generate_soul_prediction
        soul_predictions, _ = generate_soul_prediction(budget=2000)
        
        if soul_predictions:
            total_coverage = sum(p['box_count'] for p in soul_predictions)
            md.append(f"**カバー範囲: {total_coverage}通り** (当選確率: {total_coverage/100:.2f}%)")
            md.append("")
            md.append("| 優先度 | 番号 | 買い方 | タイプ | 根拠 |")
            md.append("|:---:|:---:|:---:|:---:|:---|")
            
            for i, pred in enumerate(soul_predictions[:10], 1):
                if i <= 3:
                    emoji = ['🥇', '🥈', '🥉'][i-1]
                else:
                    emoji = f'{i}'
                
                sources = ', '.join(pred['sources'][:2])
                md.append(f"| {emoji} | `{pred['number']}` | {pred['buy_type']} | {pred['box_type']}({pred['box_count']}通り) | {sources} |")
            
            md.append("")
    except Exception as e:
        md.append(f"（魂予測の生成に失敗: {e}）")
        md.append("")
    
    # ========================================
    # 💰 予算別おすすめ購入プラン
    # ========================================
    md.append("## 💰 予算別おすすめ購入プラン")
    md.append("")
    md.append("予算に合わせた厳選番号！ボックス買いで当選確率UP！🎯")
    md.append("")
    
    # 1000円プラン（5口）
    recommendations_1000 = calculate_budget_recommendations(daily_data, aggregated, budget=1000)
    md.append("### 🎫 1000円プラン（5口）")
    md.append("")
    if recommendations_1000:
        md.append("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
        md.append("|:---:|:---:|:---:|:---:|:---|")
        
        for i, rec in enumerate(recommendations_1000[:5], 1):
            priority_emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i-1] if i <= 5 else f'{i}'
            
            if rec['source'] == 'ml_sampling':
                reason = f"ML近傍探索{rec.get('ml_count', 0)}回出現"
            else:
                reason = f"出現率{rec['appearance_rate']:.0f}%・最高{rec['best_rank']}位"
            
            md.append(f"| {priority_emoji} | `{rec['number']}` | ボックス | {rec['box_type']}({rec['box_desc']}) | {reason} |")
        
        md.append("")
        total_patterns = sum(r['box_count'] for r in recommendations_1000[:5])
        md.append(f"**カバー範囲: {total_patterns}通り** （10,000通り中 = 当選確率 約{total_patterns/100:.2f}%）")
        md.append("")
    
    # 2000円プラン（10口）
    recommendations_2000 = calculate_budget_recommendations(daily_data, aggregated, budget=2000)
    md.append("### 🎫 2000円プラン（10口）")
    md.append("")
    if recommendations_2000:
        md.append("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
        md.append("|:---:|:---:|:---:|:---:|:---|")
        
        for i, rec in enumerate(recommendations_2000[:10], 1):
            if i <= 3:
                priority_emoji = ['🥇', '🥈', '🥉'][i-1]
            else:
                priority_emoji = f'{i}'
            
            if rec['source'] == 'ml_sampling':
                reason = f"ML近傍探索{rec.get('ml_count', 0)}回出現"
            else:
                reason = f"出現率{rec['appearance_rate']:.0f}%・最高{rec['best_rank']}位"
            
            md.append(f"| {priority_emoji} | `{rec['number']}` | ボックス | {rec['box_type']}({rec['box_desc']}) | {reason} |")
        
        md.append("")
        total_patterns = sum(r['box_count'] for r in recommendations_2000[:10])
        md.append(f"**カバー範囲: {total_patterns}通り** （10,000通り中 = 当選確率 約{total_patterns/100:.2f}%）")
        md.append("")
    
    # 購入のコツ
    md.append("### 📝 購入のコツ")
    md.append("")
    md.append("1. **ボックス買い推奨** - ストレートより当選確率が高い！")
    md.append("2. **シングル（24通り）を優先** - 1口で24パターンカバー")
    md.append("3. **ダブル（12通り）も狙い目** - 6511みたいな番号")
    md.append("4. **ゾロ目は避ける** - 1111等は1通りしかない")
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
    parser.add_argument(
        '--budget', '-b', type=int, default=1000,
        help='購入予算（円）（デフォルト: 1000）'
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
    markdown = generate_markdown(daily_data, aggregated, args.top, args.budget)
    
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



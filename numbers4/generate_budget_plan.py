"""
予算別おすすめ購入プランを生成（v11.1 改善版）

ボックスタイプを考慮して、最大カバー範囲を実現する5口/10口プランを提案
"""
import json
import sys
import os
from typing import List, Dict, Tuple
from collections import Counter

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from tools.utils import get_db_connection


def get_box_type_info(number: str) -> Tuple[str, str, int]:
    """
    ボックスタイプとカバー範囲を判定
    
    Returns:
        (タイプ表記, 説明, カバー範囲)
    """
    counts = Counter(number)
    unique_count = len(counts)
    max_count = max(counts.values())
    
    if unique_count == 4:
        return "シングル(ABCD)", "4つの数字が全て異なる", 24
    elif unique_count == 3:
        return "ダブル(AABC)", "1つの数字が2回出現", 12
    elif unique_count == 2:
        if max_count == 3:
            return "トリプル(AAAB)", "1つの数字が3回出現", 4
        else:
            return "ダブルダブル(AABB)", "2つの数字が2回ずつ", 6
    elif unique_count == 1:
        return "クアッド(AAAA)", "全て同じ数字（ゾロ目）", 1
    else:
        return "不明", "不明", 0


def get_reason(row: Dict, rank: int) -> str:
    """購入理由を生成"""
    number = row['number']
    score = row.get('score', 0)
    box_type, _, coverage = get_box_type_info(number)
    
    reasons = []
    
    # ランク情報
    if rank <= 3:
        reasons.append(f"第{rank}位の最有力候補")
    elif rank <= 10:
        reasons.append(f"上位{rank}位")
    else:
        reasons.append(f"{rank}位にランクイン")
    
    # スコア情報
    if score >= 60:
        reasons.append("超高スコア")
    elif score >= 50:
        reasons.append("高スコア")
    
    # ボックス情報
    if coverage >= 12:
        reasons.append(f"{coverage}通りの広カバー")
    elif coverage >= 6:
        reasons.append(f"{coverage}通りカバー")
    
    return "・".join(reasons)


def calculate_score_with_coverage(row: Dict, rank: int) -> float:
    """
    カバー範囲を考慮したスコアを計算
    
    ランクが高く、カバー範囲が広いほど高スコア
    """
    number = row['number']
    base_score = row.get('score', 0)
    _, _, coverage = get_box_type_info(number)
    
    # ランクボーナス（上位ほど高い）
    rank_bonus = max(0, 100 - rank * 2)
    
    # カバレッジボーナス（広いほど高い）
    coverage_bonus = coverage * 2
    
    # 総合スコア
    total_score = base_score + rank_bonus + coverage_bonus
    
    return total_score


def generate_5_slot_plan(predictions: List[Dict]) -> List[Dict]:
    """
    5口プラン: カバー範囲を最大化しつつ、上位候補を厳選
    
    戦略:
    1. 上位3件は確定（信頼性重視）
    2. 残り2枠はカバー範囲が広い候補を優先
    """
    plan = []
    
    # 上位3件は確定
    for i, pred in enumerate(predictions[:3], 1):
        box_type, desc, coverage = get_box_type_info(pred['number'])
        plan.append({
            'priority': f"🥇 {i}" if i == 1 else f"🥈 {i}" if i == 2 else f"🥉 {i}",
            'number': pred['number'],
            'buy_method': "ボックス",
            'box_type': box_type,
            'coverage': coverage,
            'reason': get_reason(pred, i)
        })
    
    # 4～20位からカバー範囲の広い候補を2つ選ぶ
    candidates = []
    for i, pred in enumerate(predictions[3:20], 4):
        box_type, desc, coverage = get_box_type_info(pred['number'])
        score = calculate_score_with_coverage(pred, i)
        candidates.append({
            'rank': i,
            'number': pred['number'],
            'box_type': box_type,
            'coverage': coverage,
            'score': score,
            'reason': get_reason(pred, i)
        })
    
    # カバー範囲×スコアで降順ソート
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # 上位2件を追加（重複除去）
    added = set(p['number'] for p in plan)
    for cand in candidates:
        if cand['number'] not in added:
            plan.append({
                'priority': f"{'4️⃣' if len(plan) == 3 else '5️⃣'}",
                'number': cand['number'],
                'buy_method': "ボックス",
                'box_type': cand['box_type'],
                'coverage': cand['coverage'],
                'reason': cand['reason']
            })
            added.add(cand['number'])
            if len(plan) >= 5:
                break
    
    return plan


def generate_10_slot_plan(predictions: List[Dict]) -> List[Dict]:
    """
    10口プラン: より広範囲をカバー
    
    戦略:
    1. 上位5件は確定
    2. 残り5枠はカバー範囲重視＋多様性確保
    """
    plan = []
    
    # 上位5件は確定
    priority_emojis = ["🥇", "🥈", "🥉", "4", "5"]
    for i, pred in enumerate(predictions[:5], 1):
        box_type, desc, coverage = get_box_type_info(pred['number'])
        plan.append({
            'priority': f"{priority_emojis[i-1]} {i}" if i <= 3 else f"{priority_emojis[i-1]}",
            'number': pred['number'],
            'buy_method': "ボックス",
            'box_type': box_type,
            'coverage': coverage,
            'reason': get_reason(pred, i)
        })
    
    # 6～30位からカバー範囲の広い候補を5つ選ぶ
    candidates = []
    for i, pred in enumerate(predictions[5:30], 6):
        box_type, desc, coverage = get_box_type_info(pred['number'])
        score = calculate_score_with_coverage(pred, i)
        candidates.append({
            'rank': i,
            'number': pred['number'],
            'box_type': box_type,
            'coverage': coverage,
            'score': score,
            'reason': get_reason(pred, i)
        })
    
    # カバー範囲×スコアで降順ソート
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # 上位5件を追加（重複除去）
    added = set(p['number'] for p in plan)
    for cand in candidates:
        if cand['number'] not in added:
            plan.append({
                'priority': str(len(plan) + 1),
                'number': cand['number'],
                'buy_method': "ボックス",
                'box_type': cand['box_type'],
                'coverage': cand['coverage'],
                'reason': cand['reason']
            })
            added.add(cand['number'])
            if len(plan) >= 10:
                break
    
    return plan


def generate_budget_plans(target_draw_number: int = None):
    """
    最新の予測から予算別プランを生成
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 最新の予測を取得
    if target_draw_number:
        cur.execute("""
            SELECT id, target_draw_number, created_at, predictions_count
            FROM numbers4_ensemble_predictions
            WHERE target_draw_number = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (target_draw_number,))
    else:
        cur.execute("""
            SELECT id, target_draw_number, created_at, predictions_count
            FROM numbers4_ensemble_predictions
            ORDER BY created_at DESC
            LIMIT 1
        """)
    
    row = cur.fetchone()
    if not row:
        print("❌ 予測データが見つかりません")
        return None
    
    pred_id, target_draw, created_at, pred_count = row
    
    # 予測候補を取得（上位30件）
    cur.execute("""
        SELECT number, score, rank
        FROM numbers4_prediction_candidates
        WHERE ensemble_prediction_id = ?
        ORDER BY rank ASC
        LIMIT 30
    """, (pred_id,))
    
    predictions = []
    for number, score, rank in cur.fetchall():
        predictions.append({
            'number': number,
            'score': score,
            'rank': rank
        })
    
    conn.close()
    
    if not predictions:
        print("❌ 予測候補が見つかりません")
        return None
    
    # プラン生成
    plan_5 = generate_5_slot_plan(predictions)
    plan_10 = generate_10_slot_plan(predictions)
    
    # カバー範囲を計算
    total_coverage_5 = sum(p['coverage'] for p in plan_5)
    total_coverage_10 = sum(p['coverage'] for p in plan_10)
    
    return {
        'target_draw_number': target_draw,
        'created_at': created_at,
        'plan_5': {
            'budget': '1,000円',
            'slots': 5,
            'total_coverage': total_coverage_5,
            'probability': f"{total_coverage_5 / 10000 * 100:.2f}%",
            'recommendations': plan_5
        },
        'plan_10': {
            'budget': '2,000円',
            'slots': 10,
            'total_coverage': total_coverage_10,
            'probability': f"{total_coverage_10 / 10000 * 100:.2f}%",
            'recommendations': plan_10
        }
    }


def print_budget_plans(plans: Dict):
    """プランをコンソールに表示"""
    print("\n" + "="*60)
    print("💰 予算別おすすめ購入プラン")
    print("="*60)
    print(f"🎯 対象: 第{plans['target_draw_number']}回")
    print(f"📅 生成日時: {plans['created_at']}")
    
    # 5口プラン
    print("\n### 🎫 1,000円プラン（5口）")
    print(f"**カバー範囲: {plans['plan_5']['total_coverage']}通り** （当選確率 約{plans['plan_5']['probability']}）\n")
    print("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
    print("|:---:|:---:|:---:|:---:|:---|")
    for rec in plans['plan_5']['recommendations']:
        print(f"| {rec['priority']} | `{rec['number']}` | {rec['buy_method']} | {rec['box_type']} | {rec['reason']} |")
    
    # 10口プラン
    print("\n### 🎫 2,000円プラン（10口）")
    print(f"**カバー範囲: {plans['plan_10']['total_coverage']}通り** （当選確率 約{plans['plan_10']['probability']}）\n")
    print("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
    print("|:---:|:---:|:---:|:---:|:---|")
    for rec in plans['plan_10']['recommendations']:
        print(f"| {rec['priority']} | `{rec['number']}` | {rec['buy_method']} | {rec['box_type']} | {rec['reason']} |")
    
    print("\n### 📝 購入のコツ")
    print("1. **ボックス買い推奨** - ストレートより当選確率が高い！")
    print("2. **シングル（24通り）を優先** - 1口で24パターンカバー")
    print("3. **ダブル（12通り）も狙い目** - バランスが良い")
    print("4. **予算に余裕があれば10口プラン** - カバー範囲が2倍！")


def save_budget_plans_json(plans: Dict, output_path: str = None):
    """プランをJSONファイルに保存"""
    if not output_path:
        draw_number = plans['target_draw_number']
        output_path = os.path.join(ROOT_DIR, 'predictions', 'daily', f'budget_plan_{draw_number}.json')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 予算別プランを保存しました: {output_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='予算別おすすめ購入プランを生成')
    parser.add_argument('--draw', type=int, help='対象の抽選回号')
    parser.add_argument('--output', help='出力JSONファイルパス')
    
    args = parser.parse_args()
    
    plans = generate_budget_plans(target_draw_number=args.draw)
    
    if plans:
        print_budget_plans(plans)
        save_budget_plans_json(plans, output_path=args.output)
    else:
        sys.exit(1)

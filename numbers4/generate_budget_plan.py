"""
予算別おすすめ購入プランを生成 (v11.1 改善版)

ボックスタイプを考慮して、最大カバー範囲を実現する5口/10口プランを提案
JSONファイルから予測データを読み込み (DB接続不要)
"""
import json
import sys
import os
import glob
import traceback
from typing import List, Dict, Tuple, Optional
from collections import Counter
from datetime import datetime

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)


def get_box_type_info(number: str) -> Tuple[str, str, int]:
    """
    ボックスタイプとカバー範囲を判定
    
    Args:
        number: 4桁の数字文字列
    
    Returns:
        (タイプ表記, 説明, カバー範囲)
    """
    # 入力バリデーション
    if not number or not isinstance(number, str) or len(number) != 4:
        return "不明", "不明", 0
    
    if not number.isdigit():
        return "不明", "不明", 0
    
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
        return "クアッド(AAAA)", "全て同じ数字 (ゾロ目)", 1
    else:
        return "不明", "不明", 0


def get_reason(row: Dict, rank: int) -> str:
    """購入理由を生成"""
    number = row['number']
    score = row.get('score', 0)
    _box_type, _desc, coverage = get_box_type_info(number)
    
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
    
    return " / ".join(reasons)


def calculate_score_with_coverage(row: Dict, rank: int) -> float:
    """
    カバー範囲を考慮したスコアを計算
    
    ランクが高く、カバー範囲が広いほど高スコア
    """
    number = row['number']
    base_score = row.get('score', 0)
    _box_type, _desc, coverage = get_box_type_info(number)
    
    # ランクボーナス (上位ほど高い)
    rank_bonus = max(0, 100 - rank * 2)
    
    # カバレッジボーナス (広いほど高い)
    coverage_bonus = coverage * 2
    
    # 総合スコア
    total_score = base_score + rank_bonus + coverage_bonus
    
    return total_score


def format_priority(rank: int, use_emoji: bool = True) -> str:
    """
    優先度フォーマットを統一
    
    Args:
        rank: 順位 (1-indexed)
        use_emoji: 絵文字を使用するか
    
    Returns:
        フォーマットされた優先度文字列
    """
    if use_emoji:
        if rank == 1:
            return "🥇 1"
        elif rank == 2:
            return "🥈 2"
        elif rank == 3:
            return "🥉 3"
        elif rank == 4:
            return "4️⃣"
        elif rank == 5:
            return "5️⃣"
        else:
            return str(rank)
    else:
        return str(rank)


def generate_5_slot_plan(predictions: List[Dict]) -> List[Dict]:
    """
    5口プラン: カバー範囲を最大化しつつ、上位候補を厳選
    
    戦略:
    1. 上位3件は確定 (信頼性重視)
    2. 残り2枠はカバー範囲が広い候補を優先
    """
    plan = []
    
    # 上位3件は確定
    for i, pred in enumerate(predictions[:3], 1):
        box_type, _desc, coverage = get_box_type_info(pred['number'])
        plan.append({
            'priority': format_priority(i),
            'number': pred['number'],
            'buy_method': "ボックス",
            'box_type': box_type,
            'coverage': coverage,
            'reason': get_reason(pred, i)
        })
    
    # 4-20位からカバー範囲の広い候補を2つ選ぶ
    candidates = []
    for i, pred in enumerate(predictions[3:20], 4):
        box_type, _desc, coverage = get_box_type_info(pred['number'])
        score = calculate_score_with_coverage(pred, i)
        candidates.append({
            'rank': i,
            'number': pred['number'],
            'box_type': box_type,
            'coverage': coverage,
            'score': score,
            'reason': get_reason(pred, i)
        })
    
    # カバー範囲 x スコアで降順ソート
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # 上位2件を追加 (重複除去)
    added = set(p['number'] for p in plan)
    for cand in candidates:
        if cand['number'] not in added:
            plan.append({
                'priority': format_priority(len(plan) + 1),
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
    2. 残り5枠はカバー範囲重視 + 多様性確保
    """
    plan = []
    
    # 上位5件は確定
    for i, pred in enumerate(predictions[:5], 1):
        box_type, _desc, coverage = get_box_type_info(pred['number'])
        plan.append({
            'priority': format_priority(i),
            'number': pred['number'],
            'buy_method': "ボックス",
            'box_type': box_type,
            'coverage': coverage,
            'reason': get_reason(pred, i)
        })
    
    # 6-30位からカバー範囲の広い候補を5つ選ぶ
    candidates = []
    for i, pred in enumerate(predictions[5:30], 6):
        box_type, _desc, coverage = get_box_type_info(pred['number'])
        score = calculate_score_with_coverage(pred, i)
        candidates.append({
            'rank': i,
            'number': pred['number'],
            'box_type': box_type,
            'coverage': coverage,
            'score': score,
            'reason': get_reason(pred, i)
        })
    
    # カバー範囲 x スコアで降順ソート
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # 上位5件を追加 (重複除去)
    added = set(p['number'] for p in plan)
    for cand in candidates:
        if cand['number'] not in added:
            plan.append({
                'priority': format_priority(len(plan) + 1),
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


def load_predictions_from_json(target_draw_number: Optional[int] = None) -> Optional[Dict]:
    """
    JSONファイルから予測データを読み込む (DB接続不要)
    
    Args:
        target_draw_number: 対象の抽選回号 (Noneの場合は最新)
    
    Returns:
        予測データの辞書、見つからない場合はNone
    """
    predictions_dir = os.path.join(ROOT_DIR, 'predictions', 'daily')
    
    if target_draw_number:
        # 指定された回号のファイルを探す
        json_path = os.path.join(predictions_dir, f'numbers4_{target_draw_number}.json')
        if not os.path.exists(json_path):
            print(f"❌ 予測ファイルが見つかりません: {json_path}")
            return None
    else:
        # 最新のファイルを探す
        pattern = os.path.join(predictions_dir, 'numbers4_*.json')
        files = glob.glob(pattern)
        if not files:
            print("❌ 予測ファイルが見つかりません")
            return None
        
        # ファイル名から回号を抽出してソート
        def extract_draw_number(path: str) -> int:
            basename = os.path.basename(path)
            # numbers4_6896.json -> 6896
            try:
                return int(basename.replace('numbers4_', '').replace('.json', ''))
            except ValueError:
                return 0
        
        files.sort(key=extract_draw_number, reverse=True)
        json_path = files[0]
        target_draw_number = extract_draw_number(json_path)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'target_draw_number': target_draw_number,
            'json_path': json_path,
            'data': data
        }
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ JSONファイルの読み込みに失敗: {e}")
        traceback.print_exc()
        return None


def generate_budget_plans(target_draw_number: Optional[int] = None) -> Optional[Dict]:
    """
    最新の予測から予算別プランを生成 (JSONファイルから読み込み)
    
    Args:
        target_draw_number: 対象の抽選回号 (Noneの場合は最新)
    
    Returns:
        予算別プランの辞書、失敗時はNone
    """
    # JSONファイルから予測データを読み込む
    result = load_predictions_from_json(target_draw_number)
    if not result:
        return None
    
    target_draw = result['target_draw_number']
    data = result['data']
    
    # 予測候補を取得 (JSONの構造に応じて対応)
    raw_predictions = data.get('predictions', [])
    if not raw_predictions:
        print("❌ 予測候補が見つかりません")
        return None
    
    # 上位30件を取得
    predictions = []
    
    # predictions配列の最初の要素を確認
    first_pred = raw_predictions[0] if raw_predictions else {}
    
    # 新形式: predictions[0].top_predictions に予測がある場合
    if isinstance(first_pred, dict) and 'top_predictions' in first_pred:
        top_preds = first_pred.get('top_predictions', [])
        for pred in top_preds[:30]:
            predictions.append({
                'number': str(pred.get('number', '')),
                'score': float(pred.get('score', 0)),
                'rank': int(pred.get('rank', len(predictions) + 1))
            })
    # 旧形式: predictions 配列に直接予測がある場合
    else:
        for i, pred in enumerate(raw_predictions[:30], 1):
            if isinstance(pred, dict):
                number = pred.get('number', pred.get('prediction', ''))
                score = pred.get('score', 0)
            else:
                number = str(pred)
                score = 0
            
            predictions.append({
                'number': str(number),
                'score': float(score) if score else 0,
                'rank': i
            })
    
    if not predictions:
        print("❌ 予測候補が見つかりません")
        return None
    
    # プラン生成
    plan_5 = generate_5_slot_plan(predictions)
    plan_10 = generate_10_slot_plan(predictions)
    
    # カバー範囲を計算
    total_coverage_5 = sum(p['coverage'] for p in plan_5)
    total_coverage_10 = sum(p['coverage'] for p in plan_10)
    
    # 生成日時
    created_at = datetime.now().isoformat()
    
    return {
        'target_draw_number': target_draw,
        'created_at': created_at,
        'source_file': result['json_path'],
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


def print_budget_plans(plans: Dict) -> None:
    """プランをコンソールに表示"""
    print("\n" + "=" * 60)
    print("💰 予算別おすすめ購入プラン")
    print("=" * 60)
    print(f"🎯 対象: 第{plans['target_draw_number']}回")
    print(f"📅 生成日時: {plans['created_at']}")
    
    # 5口プラン
    print("\n### 🎫 1,000円プラン (5口)")
    print(f"**カバー範囲: {plans['plan_5']['total_coverage']}通り** (当選確率 約{plans['plan_5']['probability']})\n")
    print("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
    print("|:---:|:---:|:---:|:---:|:---|")
    for rec in plans['plan_5']['recommendations']:
        print(f"| {rec['priority']} | `{rec['number']}` | {rec['buy_method']} | {rec['box_type']} | {rec['reason']} |")
    
    # 10口プラン
    print("\n### 🎫 2,000円プラン (10口)")
    print(f"**カバー範囲: {plans['plan_10']['total_coverage']}通り** (当選確率 約{plans['plan_10']['probability']})\n")
    print("| 優先度 | 番号 | 買い方 | タイプ | 理由 |")
    print("|:---:|:---:|:---:|:---:|:---|")
    for rec in plans['plan_10']['recommendations']:
        print(f"| {rec['priority']} | `{rec['number']}` | {rec['buy_method']} | {rec['box_type']} | {rec['reason']} |")
    
    print("\n### 📝 購入のコツ")
    print("1. **ボックス買い推奨** - ストレートより当選確率が高い!")
    print("2. **シングル (24通り) を優先** - 1口で24パターンカバー")
    print("3. **ダブル (12通り) も狙い目** - バランスが良い")
    print("4. **予算に余裕があれば10口プラン** - カバー範囲が2倍!")


def save_budget_plans_json(plans: Dict, output_path: Optional[str] = None) -> None:
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

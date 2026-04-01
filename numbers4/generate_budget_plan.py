"""
予算別おすすめ購入プランを生成 (v15.0)

v15.0 改善:
- カバー率最大化モード: スコアよりABCD型(24通り)を最優先し、カバー数を最大化
- 分散購入戦略: 月間の購入スケジュールを生成（5回×2口で独立試行を増やす）
- ミニ購入導入: ボックス+ミニのハイブリッド戦略（ミニは1/100で当選しやすい）
- 期待値ベーススコアリング: 配当金額×確率でランキング
- 数字カバレッジ最適化: 各桁で0-9が均等にカバーされるよう最適化

同一ボックス類型（桁の並び替えで同じ multiset）は二重にカバーしない前提で
限界カバー最大化しつつ、アンサンブルスコアと順位でタイブレークする。
月3万円・1回1000円(5口)/最大2000円(10口)の運用メタを JSON に同梱。
JSONファイルから予測データを読み込み (DB接続不要)
"""
import json
import sys
import os
import glob
import traceback
import math
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import Counter

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# 共通ユーティリティからインポート
from numbers4.box_utils import get_box_type_info
from numbers4.permutation_pick import refine_top_predictions_numbers
from tools.utils import load_all_numbers4_draws

# 運用目安（購入判断用メタ。JSON に同梱）
DEFAULT_MONTHLY_BUDGET_YEN = 30_000
DEFAULT_PER_DRAW_YEN = 1_000
MAX_PER_DRAW_YEN = 2_000
YEN_PER_TICKET = 200


def monthly_budget_guide_meta() -> Dict:
    return {
        "max_yen_per_month": DEFAULT_MONTHLY_BUDGET_YEN,
        "default_per_draw_yen": DEFAULT_PER_DRAW_YEN,
        "max_per_draw_yen": MAX_PER_DRAW_YEN,
        "yen_per_ticket": YEN_PER_TICKET,
        "slots_for_1000yen": 5,
        "slots_for_2000yen": 10,
        "daily_full_month_hint": (
            f"毎日{DEFAULT_PER_DRAW_YEN}円×約30日 ≒ {DEFAULT_MONTHLY_BUDGET_YEN}円/月。"
            f"攻める日は{MAX_PER_DRAW_YEN}円(10口)にして他日を抑えると上限内に収めやすい。"
        ),
    }


def _box_fingerprint(number: str) -> str:
    """ボックス購入で同一となる multiset のキー（重複カバー判定用）"""
    if not number or len(number) != 4 or not number.isdigit():
        return ""
    return "".join(sorted(number))


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


def _greedy_box_plan(
    predictions: List[Dict],
    num_slots: int,
    pool_max: int = 45,
) -> Tuple[List[Dict], int]:
    """
    限界カバー（新しい multiset のみカウント）を最大化する貪欲プラン。

    同一 fingerprint（例: 1234 と 4321）はボックス上同じ集合のため、
    2口目以降は限界カバー0として優先度を下げる。
    """
    pool: List[Dict] = []
    for idx, pred in enumerate(predictions[:pool_max], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        box_type, _desc, coverage = get_box_type_info(num)
        if coverage <= 0:
            continue
        pool.append({
            "rank": idx,
            "number": num,
            "score": float(pred.get("score", 0)),
            "box_type": box_type,
            "coverage": coverage,
            "fingerprint": _box_fingerprint(num),
            "pred": pred,
        })

    selected: List[Dict] = []
    used_numbers: set = set()
    used_fp: set = set()
    unique_total = 0

    while len(selected) < num_slots:
        best = None
        best_key = None
        for cand in pool:
            if cand["number"] in used_numbers:
                continue
            fp = cand["fingerprint"]
            marginal = cand["coverage"] if fp not in used_fp else 0
            rank = cand["rank"]
            score = cand["score"]
            composite = score + (45.0 - min(rank, 45)) * 0.35
            key = (marginal, composite, -rank)
            if best_key is None or key > best_key:
                best_key = key
                best = cand
        if best is None:
            break
        fp = best["fingerprint"]
        marginal = best["coverage"] if fp not in used_fp else 0
        used_numbers.add(best["number"])
        used_fp.add(fp)
        unique_total += marginal

        pr = len(selected) + 1
        pred = best["pred"]
        row = {
            "priority": format_priority(pr),
            "number": best["number"],
            "buy_method": "ボックス",
            "box_type": best["box_type"],
            "coverage": best["coverage"],
            "marginal_coverage": marginal,
            "reason": get_reason(pred, best["rank"]),
        }
        if marginal == 0 and fp:
            row["reason"] = row["reason"] + " / 同一ボックス型の追加候補(モデル順)"
        selected.append(row)

    return selected, unique_total


# ============================================================
# v15.0: カバー率最大化モード（提案1）
# スコアを無視し、純粋にカバー通り数が最大になる候補を選ぶ
# ABCD型（24通り）> AABC型（12通り）> AABB型（6通り）の順で優先
# ============================================================

def _max_coverage_plan(
    predictions: List[Dict],
    num_slots: int,
    pool_max: int = 60,
) -> Tuple[List[Dict], int]:
    """
    カバー率最大化プラン: ボックスカバー数を最大化する。
    スコア順ではなく、カバー数の大きいボックスタイプを優先。
    同一fingerprint（ボックス重複）は排除。
    """
    pool: List[Dict] = []
    for idx, pred in enumerate(predictions[:pool_max], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        box_type, _desc, coverage = get_box_type_info(num)
        if coverage <= 0:
            continue
        pool.append({
            "rank": idx,
            "number": num,
            "score": float(pred.get("score", 0)),
            "box_type": box_type,
            "coverage": coverage,
            "fingerprint": _box_fingerprint(num),
            "pred": pred,
        })

    selected: List[Dict] = []
    used_fp: set = set()
    unique_total = 0

    while len(selected) < num_slots and pool:
        best = None
        best_key = None
        for cand in pool:
            if cand["fingerprint"] in used_fp:
                continue
            # カバー数を最優先、次にスコアでタイブレーク
            key = (cand["coverage"], cand["score"])
            if best_key is None or key > best_key:
                best_key = key
                best = cand
        if best is None:
            break
        used_fp.add(best["fingerprint"])
        unique_total += best["coverage"]
        pool.remove(best)

        pr = len(selected) + 1
        pred = best["pred"]
        selected.append({
            "priority": format_priority(pr),
            "number": best["number"],
            "buy_method": "ボックス",
            "box_type": best["box_type"],
            "coverage": best["coverage"],
            "marginal_coverage": best["coverage"],
            "reason": f"カバー最大化: {best['coverage']}通り / " + get_reason(pred, best["rank"]),
        })

    return selected, unique_total


# ============================================================
# v15.0: 数字カバレッジ最適化（提案5）
# 選んだ候補の各桁(0-9)が均等にカバーされるよう最適化
# ============================================================

def _digit_coverage_score(selected_numbers: List[str]) -> float:
    """選ばれた番号群の桁カバレッジスコア（高いほど均等）"""
    if not selected_numbers:
        return 0.0
    digit_counts = Counter()
    for num in selected_numbers:
        for ch in num:
            digit_counts[ch] += 1
    # 0-9の全数字に対して出現回数を計算
    counts = [digit_counts.get(str(d), 0) for d in range(10)]
    total = sum(counts)
    if total == 0:
        return 0.0
    # 理想は均等分布（各数字が total/10 回）
    ideal = total / 10.0
    # 均等度 = 1 - (標準偏差 / 理想値)
    variance = sum((c - ideal) ** 2 for c in counts) / 10.0
    std_dev = math.sqrt(variance)
    return max(0.0, 1.0 - std_dev / ideal)


def _max_coverage_with_digit_balance(
    predictions: List[Dict],
    num_slots: int,
    pool_max: int = 60,
) -> Tuple[List[Dict], int]:
    """
    カバー率最大化 + 数字カバレッジ最適化プラン（提案1+5の統合版）
    カバー数を最大化しつつ、各桁の0-9が均等になるよう調整。
    """
    pool: List[Dict] = []
    for idx, pred in enumerate(predictions[:pool_max], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        box_type, _desc, coverage = get_box_type_info(num)
        if coverage <= 0:
            continue
        pool.append({
            "rank": idx,
            "number": num,
            "score": float(pred.get("score", 0)),
            "box_type": box_type,
            "coverage": coverage,
            "fingerprint": _box_fingerprint(num),
            "pred": pred,
        })

    selected: List[Dict] = []
    selected_numbers: List[str] = []
    used_fp: set = set()
    unique_total = 0

    while len(selected) < num_slots and pool:
        best = None
        best_key = None
        for cand in pool:
            if cand["fingerprint"] in used_fp:
                continue
            # このcandを追加した場合のdigit coverageを計算
            test_numbers = selected_numbers + [cand["number"]]
            digit_score = _digit_coverage_score(test_numbers)
            # カバー数 × (1 + digit_score * 0.3) でバランス調整
            adjusted = cand["coverage"] * (1.0 + digit_score * 0.3)
            key = (adjusted, cand["score"])
            if best_key is None or key > best_key:
                best_key = key
                best = cand
        if best is None:
            break
        used_fp.add(best["fingerprint"])
        unique_total += best["coverage"]
        selected_numbers.append(best["number"])
        pool.remove(best)

        pr = len(selected) + 1
        pred = best["pred"]
        digit_score = _digit_coverage_score(selected_numbers)
        selected.append({
            "priority": format_priority(pr),
            "number": best["number"],
            "buy_method": "ボックス",
            "box_type": best["box_type"],
            "coverage": best["coverage"],
            "marginal_coverage": best["coverage"],
            "reason": f"カバー最大+数字均等 / " + get_reason(pred, best["rank"]),
        })

    return selected, unique_total


# ============================================================
# v15.0: ミニ購入プラン（提案2）
# ナンバーズ4ミニ（下2桁一致で当選、1/100の確率）
# ============================================================

def _generate_mini_plan(
    predictions: List[Dict],
    num_slots: int,
) -> Tuple[List[Dict], int]:
    """
    ミニ購入プラン: 下2桁のユニークペアが最大になるよう候補を選ぶ。
    ミニは下2桁の一致で当選（1/100）。
    """
    # 下2桁の出現頻度をスコア付きで集計
    tail_map: Dict[str, Dict] = {}
    for idx, pred in enumerate(predictions[:45], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        tail = num[2:]  # 下2桁
        if tail not in tail_map:
            tail_map[tail] = {
                "rank": idx,
                "source_number": num,
                "score": float(pred.get("score", 0)),
                "pred": pred,
            }

    # スコア順にソートして上位を選択
    sorted_tails = sorted(tail_map.items(), key=lambda x: x[1]["score"], reverse=True)

    selected: List[Dict] = []
    unique_tails = 0

    for tail, info in sorted_tails[:num_slots]:
        unique_tails += 1
        pr = len(selected) + 1
        selected.append({
            "priority": format_priority(pr),
            "number": info["source_number"],
            "buy_method": "ミニ",
            "box_type": f"下2桁: {tail}",
            "coverage": 1,  # ミニは1通り（下2桁の完全一致）
            "marginal_coverage": 1,
            "reason": f"ミニ(1/100) / 元番号{info['source_number']}の下2桁「{tail}」",
        })

    return selected, unique_tails


# ============================================================
# v15.0: 期待値ベーススコアリング（提案4）
# 配当金額 × 確率でランキング
# ナンバーズ4の平均配当: ストレート約100万円、ボックス約3-12万円、ミニ約1万円
# ============================================================

# 平均配当金額（円）の目安
AVERAGE_PAYOUTS = {
    "シングル(ABCD)": {"straight": 1_000_000, "box": 37_500},   # 100万/24通り ≈ 約4万
    "ダブル(AABC)":   {"straight": 1_000_000, "box": 75_000},   # 100万/12通り ≈ 約8万
    "ダブルダブル(AABB)": {"straight": 1_000_000, "box": 150_000},  # 100万/6 ≈ 16万
    "トリプル(AAAB)": {"straight": 1_000_000, "box": 250_000},  # 100万/4 ≈ 25万
    "クアッド(AAAA)": {"straight": 1_000_000, "box": 1_000_000},# ストレートと同じ
}


def _expected_value_plan(
    predictions: List[Dict],
    num_slots: int,
    pool_max: int = 60,
) -> Tuple[List[Dict], int, float]:
    """
    期待値ベースプラン: ボックス配当 × 当選確率(カバー数/10000) でランキング。
    人気の低い番号（= 高配当）を優先する傾向。

    Returns:
        (selected, unique_coverage, total_expected_value)
    """
    pool: List[Dict] = []
    for idx, pred in enumerate(predictions[:pool_max], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        box_type, _desc, coverage = get_box_type_info(num)
        if coverage <= 0:
            continue

        payout_info = AVERAGE_PAYOUTS.get(box_type, {"box": 50_000})
        box_payout = payout_info["box"]
        # 期待値 = 配当 × 確率 (1口200円のコストを差し引く)
        probability = coverage / 10_000
        ev = box_payout * probability - YEN_PER_TICKET

        pool.append({
            "rank": idx,
            "number": num,
            "score": float(pred.get("score", 0)),
            "box_type": box_type,
            "coverage": coverage,
            "fingerprint": _box_fingerprint(num),
            "expected_value": ev,
            "box_payout": box_payout,
            "pred": pred,
        })

    selected: List[Dict] = []
    used_fp: set = set()
    unique_total = 0
    total_ev = 0.0

    while len(selected) < num_slots and pool:
        best = None
        best_key = None
        for cand in pool:
            if cand["fingerprint"] in used_fp:
                continue
            key = (cand["expected_value"], cand["score"])
            if best_key is None or key > best_key:
                best_key = key
                best = cand
        if best is None:
            break
        used_fp.add(best["fingerprint"])
        unique_total += best["coverage"]
        total_ev += best["expected_value"]
        pool.remove(best)

        pr = len(selected) + 1
        pred = best["pred"]
        selected.append({
            "priority": format_priority(pr),
            "number": best["number"],
            "buy_method": "ボックス",
            "box_type": best["box_type"],
            "coverage": best["coverage"],
            "marginal_coverage": best["coverage"],
            "expected_value": round(best["expected_value"], 0),
            "box_payout": best["box_payout"],
            "reason": f"期待値{best['expected_value']:+.0f}円 / 配当目安{best['box_payout']:,}円 / " + get_reason(pred, best["rank"]),
        })

    return selected, unique_total, total_ev


# ============================================================
# v15.0: 分散購入戦略（提案3）
# 月間の購入スケジュールを生成
# 1回に10口より、5回×2口の分散でカバー率を最大化
# ============================================================

def _generate_distributed_plan(
    predictions: List[Dict],
    total_budget_yen: int = 2_000,
    tickets_per_session: int = 2,
) -> Dict:
    """
    分散購入プラン: 同一予算を複数回に分けて購入。
    独立試行を増やし、月間の当選確率を最大化。

    例: 2000円 → 2口×5回（5日に分散）
    各回で異なるボックスを選択し、累積カバー率を最大化。
    """
    total_tickets = total_budget_yen // YEN_PER_TICKET
    num_sessions = total_tickets // tickets_per_session

    # 全候補からカバー最大のものを session ごとに割り当て
    pool: List[Dict] = []
    for idx, pred in enumerate(predictions[:60], 1):
        num = str(pred.get("number", ""))
        if len(num) != 4 or not num.isdigit():
            continue
        box_type, _desc, coverage = get_box_type_info(num)
        if coverage <= 0:
            continue
        pool.append({
            "rank": idx,
            "number": num,
            "score": float(pred.get("score", 0)),
            "box_type": box_type,
            "coverage": coverage,
            "fingerprint": _box_fingerprint(num),
            "pred": pred,
        })

    # カバー数の大きい順にソート
    pool.sort(key=lambda x: (x["coverage"], x["score"]), reverse=True)

    sessions = []
    used_fp: set = set()
    cumulative_coverage = 0

    for session_idx in range(num_sessions):
        session_picks = []
        for _ in range(tickets_per_session):
            best = None
            for cand in pool:
                if cand["fingerprint"] in used_fp:
                    continue
                best = cand
                break
            if best is None:
                break
            used_fp.add(best["fingerprint"])
            cumulative_coverage += best["coverage"]
            pool.remove(best)
            session_picks.append({
                "number": best["number"],
                "buy_method": "ボックス",
                "box_type": best["box_type"],
                "coverage": best["coverage"],
                "reason": get_reason(best["pred"], best["rank"]),
            })

        if session_picks:
            session_coverage = sum(p["coverage"] for p in session_picks)
            sessions.append({
                "session": session_idx + 1,
                "budget": f"{tickets_per_session * YEN_PER_TICKET:,}円",
                "tickets": len(session_picks),
                "session_coverage": session_coverage,
                "picks": session_picks,
            })

    # 分散の効果を計算
    # 一括購入: 1 - (1 - p)^1  （1回の試行）
    # 分散購入: 1 - (1 - p_i) × (1 - p_j) × ... （独立試行の積）
    if sessions:
        # 各セッションでの「当たらない確率」を掛け合わせる
        miss_prob = 1.0
        for s in sessions:
            session_p = s["session_coverage"] / 10_000
            miss_prob *= (1.0 - session_p)
        monthly_hit_prob = 1.0 - miss_prob
    else:
        monthly_hit_prob = 0.0

    return {
        "strategy": "分散購入（独立試行最大化）",
        "total_budget": f"{total_budget_yen:,}円",
        "sessions": num_sessions,
        "tickets_per_session": tickets_per_session,
        "cumulative_unique_coverage": cumulative_coverage,
        "cumulative_probability": f"{cumulative_coverage / 10_000 * 100:.2f}%",
        "monthly_hit_probability": f"{monthly_hit_prob * 100:.3f}%",
        "schedule": sessions,
    }


# ============================================================
# v15.0: ハイブリッド戦略（ボックス + ミニ混合）
# ============================================================

def _generate_hybrid_plan(
    predictions: List[Dict],
    num_box_slots: int,
    num_mini_slots: int,
) -> Dict:
    """
    ハイブリッドプラン: ボックスとミニを組み合わせた購入戦略。
    ボックスで大きなカバーを確保 + ミニで当選確率を底上げ。
    """
    box_plan, box_coverage = _max_coverage_with_digit_balance(predictions, num_box_slots)
    mini_plan, mini_count = _generate_mini_plan(predictions, num_mini_slots)

    # ボックス当選確率
    box_prob = box_coverage / 10_000
    # ミニ当選確率（各1/100、ユニーク下2桁の数）
    mini_prob = min(mini_count / 100, 1.0)
    # いずれかが当たる確率 = 1 - (両方外れる確率)
    combined_prob = 1.0 - (1.0 - box_prob) * (1.0 - mini_prob)

    total_cost = (num_box_slots + num_mini_slots) * YEN_PER_TICKET

    return {
        "strategy": "ハイブリッド（ボックス＋ミニ）",
        "total_budget": f"{total_cost:,}円",
        "box_slots": num_box_slots,
        "mini_slots": num_mini_slots,
        "box_coverage": box_coverage,
        "box_probability": f"{box_prob * 100:.2f}%",
        "mini_unique_tails": mini_count,
        "mini_probability": f"{mini_prob * 100:.1f}%",
        "combined_probability": f"{combined_prob * 100:.2f}%",
        "box_recommendations": box_plan,
        "mini_recommendations": mini_plan,
    }


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

    # ensemble 上位候補の並びを、直近データの桁位置別出現に基づき同一ボックス内で再選択
    try:
        draws_df = load_all_numbers4_draws()
        if draws_df is not None and len(draws_df) > 0:
            predictions = refine_top_predictions_numbers(
                predictions, draws_df, recent_n=50
            )
    except Exception as e:
        print(f"⚠️ 予算プラン用の並び再選択をスキップ: {e}")
    
    # === v15.0: 複数プラン生成 ===

    # 1. 従来のスコアベースプラン（v12互換）
    plan_5_score, cov_5_score = _greedy_box_plan(predictions, 5)
    plan_10_score, cov_10_score = _greedy_box_plan(predictions, 10)

    # 2. カバー率最大化 + 数字カバレッジ最適化プラン（v15 推奨）
    plan_5_max, cov_5_max = _max_coverage_with_digit_balance(predictions, 5)
    plan_10_max, cov_10_max = _max_coverage_with_digit_balance(predictions, 10)

    # 3. ハイブリッドプラン（ボックス3口 + ミニ2口 = 1000円）
    hybrid_5 = _generate_hybrid_plan(predictions, num_box_slots=3, num_mini_slots=2)
    # ボックス5口 + ミニ5口 = 2000円
    hybrid_10 = _generate_hybrid_plan(predictions, num_box_slots=5, num_mini_slots=5)

    # 4. 期待値ベースプラン
    plan_5_ev, cov_5_ev, total_ev_5 = _expected_value_plan(predictions, 5)
    plan_10_ev, cov_10_ev, total_ev_10 = _expected_value_plan(predictions, 10)

    # 5. 分散購入プラン（2000円を2口×5回に分散）
    distributed_plan = _generate_distributed_plan(predictions, total_budget_yen=2_000, tickets_per_session=2)

    # v15推奨プランの選択: カバー率が高い方を採用
    if cov_5_max >= cov_5_score:
        best_plan_5, best_cov_5 = plan_5_max, cov_5_max
        best_plan_5_label = "v15カバー最大化+数字均等"
    else:
        best_plan_5, best_cov_5 = plan_5_score, cov_5_score
        best_plan_5_label = "v12スコアベース"

    if cov_10_max >= cov_10_score:
        best_plan_10, best_cov_10 = plan_10_max, cov_10_max
        best_plan_10_label = "v15カバー最大化+数字均等"
    else:
        best_plan_10, best_cov_10 = plan_10_score, cov_10_score
        best_plan_10_label = "v12スコアベース"

    created_at = datetime.now().isoformat()

    return {
        'target_draw_number': target_draw,
        'created_at': created_at,
        'source_file': result['json_path'],
        'planner_version': 'v15.0',
        'monthly_budget_guide': monthly_budget_guide_meta(),
        # === メインプラン（v15推奨: カバー率最大化） ===
        'plan_5': {
            'budget': '1,000円',
            'slots': 5,
            'total_coverage': best_cov_5,
            'coverage_note': f'{best_plan_5_label} / ボックス multiset 単位の重複を除いたユニーク通り数',
            'probability': f"{best_cov_5 / 10000 * 100:.2f}%",
            'recommendations': best_plan_5,
        },
        'plan_10': {
            'budget': '2,000円',
            'slots': 10,
            'total_coverage': best_cov_10,
            'coverage_note': f'{best_plan_10_label} / ボックス multiset 単位の重複を除いたユニーク通り数',
            'probability': f"{best_cov_10 / 10000 * 100:.2f}%",
            'recommendations': best_plan_10,
        },
        # === v15追加プラン ===
        'hybrid_5': hybrid_5,
        'hybrid_10': hybrid_10,
        'expected_value_5': {
            'budget': '1,000円',
            'slots': 5,
            'total_coverage': cov_5_ev,
            'total_expected_value': round(total_ev_5, 0),
            'probability': f"{cov_5_ev / 10000 * 100:.2f}%",
            'recommendations': plan_5_ev,
        },
        'expected_value_10': {
            'budget': '2,000円',
            'slots': 10,
            'total_coverage': cov_10_ev,
            'total_expected_value': round(total_ev_10, 0),
            'probability': f"{cov_10_ev / 10000 * 100:.2f}%",
            'recommendations': plan_10_ev,
        },
        'distributed_plan': distributed_plan,
    }


def _print_plan_table(recommendations: List[Dict]) -> None:
    """プランのテーブルを表示する共通関数"""
    print("| 優先度 | 番号 | 買い方 | タイプ | +通り | 理由 |")
    print("|:---:|:---:|:---:|:---:|:---:|:---|")
    for rec in recommendations:
        m = rec.get("marginal_coverage", rec.get("coverage", 0))
        print(
            f"| {rec['priority']} | `{rec['number']}` | {rec['buy_method']} | {rec['box_type']} | {m} | {rec['reason']} |"
        )


def print_budget_plans(plans: Dict) -> None:
    """プランをコンソールに表示"""
    print("\n" + "=" * 60)
    print("💰 予算別おすすめ購入プラン (v15.0)")
    print("=" * 60)
    print(f"🎯 対象: 第{plans['target_draw_number']}回")
    print(f"📅 生成日時: {plans['created_at']}")
    guide = plans.get("monthly_budget_guide") or monthly_budget_guide_meta()
    print("\n### 💳 月間の目安")
    print(
        f"- 上限 **{guide['max_yen_per_month']:,}円/月** / 基本 **{guide['default_per_draw_yen']:,}円・{guide['slots_for_1000yen']}口** / 最大 **{guide['max_per_draw_yen']:,}円・{guide['slots_for_2000yen']}口**"
    )
    print(f"- {guide.get('daily_full_month_hint', '')}")

    # ========== メインプラン（v15推奨） ==========
    print("\n" + "-" * 60)
    print("## 🏆 推奨プラン（カバー率最大化 + 数字均等化）")
    print("-" * 60)

    # 5口プラン
    print("\n### 🎫 1,000円プラン (5口)")
    p5 = plans['plan_5']
    print(
        f"**ユニークカバー: {p5['total_coverage']}通り** "
        f"(参考: 約{p5['probability']}) [{p5.get('coverage_note', '')}]\n"
    )
    _print_plan_table(p5['recommendations'])

    # 10口プラン
    print("\n### 🎫 2,000円プラン (10口)")
    p10 = plans['plan_10']
    print(
        f"**ユニークカバー: {p10['total_coverage']}通り** "
        f"(参考: 約{p10['probability']}) [{p10.get('coverage_note', '')}]\n"
    )
    _print_plan_table(p10['recommendations'])

    # ========== ハイブリッドプラン ==========
    hybrid_5 = plans.get('hybrid_5')
    hybrid_10 = plans.get('hybrid_10')
    if hybrid_5 or hybrid_10:
        print("\n" + "-" * 60)
        print("## 🎯 ハイブリッドプラン（ボックス＋ミニ）")
        print("-" * 60)

        if hybrid_5:
            print(f"\n### 🎫 1,000円 ハイブリッド（ボックス{hybrid_5['box_slots']}口 + ミニ{hybrid_5['mini_slots']}口）")
            print(f"**ボックス当選確率: {hybrid_5['box_probability']}** / **ミニ当選確率: {hybrid_5['mini_probability']}**")
            print(f"**いずれか当選確率: {hybrid_5['combined_probability']}**\n")
            print("#### ボックス:")
            _print_plan_table(hybrid_5['box_recommendations'])
            print("\n#### ミニ:")
            _print_plan_table(hybrid_5['mini_recommendations'])

        if hybrid_10:
            print(f"\n### 🎫 2,000円 ハイブリッド（ボックス{hybrid_10['box_slots']}口 + ミニ{hybrid_10['mini_slots']}口）")
            print(f"**ボックス当選確率: {hybrid_10['box_probability']}** / **ミニ当選確率: {hybrid_10['mini_probability']}**")
            print(f"**いずれか当選確率: {hybrid_10['combined_probability']}**\n")
            print("#### ボックス:")
            _print_plan_table(hybrid_10['box_recommendations'])
            print("\n#### ミニ:")
            _print_plan_table(hybrid_10['mini_recommendations'])

    # ========== 期待値プラン ==========
    ev5 = plans.get('expected_value_5')
    ev10 = plans.get('expected_value_10')
    if ev5 or ev10:
        print("\n" + "-" * 60)
        print("## 💹 期待値重視プラン（配当×確率でランキング）")
        print("-" * 60)

        if ev5:
            print(f"\n### 🎫 1,000円 期待値プラン")
            print(f"**合計期待値: {ev5['total_expected_value']:+,.0f}円** / カバー: {ev5['total_coverage']}通り ({ev5['probability']})\n")
            _print_plan_table(ev5['recommendations'])
        if ev10:
            print(f"\n### 🎫 2,000円 期待値プラン")
            print(f"**合計期待値: {ev10['total_expected_value']:+,.0f}円** / カバー: {ev10['total_coverage']}通り ({ev10['probability']})\n")
            _print_plan_table(ev10['recommendations'])

    # ========== 分散購入プラン ==========
    dist = plans.get('distributed_plan')
    if dist:
        print("\n" + "-" * 60)
        print("## 📅 分散購入プラン（独立試行で確率UP）")
        print("-" * 60)
        print(f"\n**戦略:** {dist['strategy']}")
        print(f"**予算:** {dist['total_budget']} → {dist['sessions']}回 × {dist['tickets_per_session']}口")
        print(f"**累積カバー:** {dist['cumulative_unique_coverage']}通り ({dist['cumulative_probability']})")
        print(f"**月間当選確率:** {dist['monthly_hit_probability']}")

        for s in dist.get('schedule', []):
            print(f"\n  回{s['session']}: {s['budget']} ({s['tickets']}口, +{s['session_coverage']}通り)")
            for p in s['picks']:
                print(f"    - `{p['number']}` {p['buy_method']} {p['box_type']} +{p['coverage']}通り")

    # ========== 購入のコツ ==========
    print("\n### 📝 購入のコツ (v15)")
    print("1. **推奨プラン**はABCD型(24通り)を優先し、カバー率を最大化しています")
    print("2. **ハイブリッド**はミニ(1/100)を混ぜることで「当たる体験」が増えます")
    print("3. **分散購入**は同じ予算でも複数回に分けると月間当選確率がUPします")
    print("4. **期待値プラン**は配当が高くなりやすい番号を優先しています")
    print("5. **確率は参考値**（実際の当せんは券種・ルールによる）")


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

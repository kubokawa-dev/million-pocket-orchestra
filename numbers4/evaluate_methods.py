"""
手法別予測の精度評価と重み更新スクリプト

各予測手法の精度を評価し、良い予測をした手法の重みを上げ、
悪い予測をした手法の重みを下げることで、翌日の予測精度を改善する

使い方:
  python numbers4/evaluate_methods.py --draw 6918
  python numbers4/evaluate_methods.py --draw 6918 --verbose
"""

import os
import sys
import json
import argparse
import glob
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.utils import get_db_connection

# 定数
METHODS_DIR = os.path.join(project_root, 'predictions', 'daily', 'methods')
WEIGHTS_FILE = os.path.join(project_root, 'numbers4', 'method_weights.json')

# 評価対象の手法一覧
ALL_METHODS = [
    'box_model',
    'ml_neighborhood', 
    'even_odd_pattern',
    'low_sum_specialist',
    'sequential_pattern',
    'cold_revival',
    'hot_pair',
    'box_pattern',
    'digit_freq_box',
    'global_frequency',
    'lightgbm',
    'state_chain',
    'adjacent_digit',  # v13.0 NEW! 隣接数字パターン
    'lgbm_box',        # v14.0 NEW! ボックスレベルLightGBM
    'repetition_pattern',  # v17.0 NEW! 繰り返しパターン特化
]


def get_default_method_weights() -> Dict[str, float]:
    """デフォルトの手法別重み"""
    return {
        'box_model': 15.0,
        'ml_neighborhood': 12.0,
        'even_odd_pattern': 8.0,
        'low_sum_specialist': 6.0,
        'sequential_pattern': 10.0,
        'cold_revival': 5.0,
        'hot_pair': 8.0,
        'box_pattern': 10.0,
        'digit_freq_box': 7.0,
        'global_frequency': 9.0,
        'lightgbm': 20.0,
        'state_chain': 8.0,
        'adjacent_digit': 10.0,  # v13.0 NEW! 隣接数字パターン
        'lgbm_box': 15.0,       # v14.0 NEW! ボックスレベルLightGBM
        'repetition_pattern': 18.0,  # v17.0 NEW! 繰り返しパターン特化
    }


def load_method_weights() -> Dict[str, float]:
    """保存された手法別重みを読み込む"""
    defaults = get_default_method_weights()
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            loaded = data.get('weights', {})
            # 既存値を優先しつつ、不足キーはデフォルトで補完
            merged = defaults.copy()
            merged.update(loaded)
            return merged
    return defaults


def save_method_weights(weights: Dict[str, float], metadata: dict = None):
    """手法別重みを保存"""
    data = {
        'weights': weights,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'metadata': metadata or {}
    }
    
    with open(WEIGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_actual_result(draw_number: int) -> Optional[str]:
    """当選番号を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT numbers FROM numbers4_draws 
            WHERE draw_number = ?
        """, (draw_number,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _parse_draw_date(draw_date: str) -> Optional[datetime]:
    """DBのdraw_date文字列をdatetimeに変換（複数フォーマット対応）。"""
    if not draw_date:
        return None
    raw = str(draw_date).strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def get_draw_weekday(draw_number: int) -> Optional[int]:
    """
    回号の曜日を返す（0=Monday ... 6=Sunday）。
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT draw_date FROM numbers4_draws
            WHERE draw_number = ?
        """, (draw_number,))
        row = cur.fetchone()
        if not row:
            return None
        draw_date = row[0] if not isinstance(row, dict) else row.get("draw_date")
        dt = _parse_draw_date(draw_date)
        return dt.weekday() if dt else None
    finally:
        conn.close()


def load_method_predictions(draw_number: int, method: str) -> List[str]:
    """指定手法の予測を読み込む"""
    predictions = []
    
    method_file = os.path.join(METHODS_DIR, method, f'numbers4_{draw_number}.json')
    
    if not os.path.exists(method_file):
        return predictions
    
    try:
        with open(method_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 全予測エントリから番号を収集（重複排除、順位順）
        seen = set()
        for pred_entry in data.get('predictions', []):
            for pred in pred_entry.get('top_predictions', []):
                number = pred.get('number', '')
                if number and number not in seen:
                    predictions.append(number)
                    seen.add(number)
        
    except Exception as e:
        print(f"⚠️ Error loading {method_file}: {e}")
    
    return predictions


def is_box_match(pred: str, actual: str) -> bool:
    """ボックス一致（順不同で数字が全て一致）をチェック"""
    return sorted(list(pred)) == sorted(list(actual))


def count_digit_matches(pred: str, actual: str) -> int:
    """何桁の数字が一致しているか（順不同）をカウント"""
    from collections import Counter
    pred_counter = Counter(pred)
    actual_counter = Counter(actual)
    return sum((actual_counter & pred_counter).values())


def count_position_matches(pred: str, actual: str) -> int:
    """位置一致数をカウント"""
    return sum(1 for a, p in zip(actual, pred) if a == p)


def evaluate_method(predictions: List[str], actual: str, top_k: int = 100) -> Dict:
    """
    手法の予測精度を評価（v2.0 改善版）
    
    改善点:
    - 順位ボーナス: 上位で当たるほど高評価
    - 複合スコア: 位置一致と数字一致を組み合わせ
    - 連続性ボーナス: 複数の良い予測があれば加点
    
    Returns:
        {
            'straight_rank': 完全一致の順位（なければNone）,
            'box_rank': ボックス一致の順位（なければNone）,
            'best_position_hits': 最大位置一致数,
            'best_digit_hits': 最大数字一致数,
            'good_predictions_count': 3桁以上一致の予測数,
            'score': 総合スコア（0-100）
        }
    """
    result = {
        'straight_rank': None,
        'box_rank': None,
        'best_position_hits': 0,
        'best_digit_hits': 0,
        'good_predictions_count': 0,  # NEW: 良い予測の数
        'score': 0.0
    }
    
    if not predictions:
        return result
    
    good_preds = []  # 3桁以上一致した予測を記録
    
    for i, pred in enumerate(predictions[:top_k]):
        rank = i + 1
        
        # ストレート一致
        if pred == actual and result['straight_rank'] is None:
            result['straight_rank'] = rank
        
        # ボックス一致
        if is_box_match(pred, actual) and result['box_rank'] is None:
            result['box_rank'] = rank
        
        # 位置一致数
        pos_hits = count_position_matches(pred, actual)
        if pos_hits > result['best_position_hits']:
            result['best_position_hits'] = pos_hits
        
        # 数字一致数
        digit_hits = count_digit_matches(pred, actual)
        if digit_hits > result['best_digit_hits']:
            result['best_digit_hits'] = digit_hits
        
        # 良い予測をカウント（3桁以上一致）
        if pos_hits >= 3 or digit_hits >= 3:
            good_preds.append((rank, pos_hits, digit_hits))
    
    result['good_predictions_count'] = len(good_preds)
    
    # スコア計算（v2.0 改善版）
    score = 0.0
    
    if result['straight_rank']:
        # ストレート一致: 高スコア（順位が高いほど良い）
        rank_bonus = (top_k - result['straight_rank'] + 1) / top_k
        score = 100.0 * rank_bonus
    elif result['box_rank']:
        # ボックス一致: 75%のスコア（70→75に改善）
        rank_bonus = (top_k - result['box_rank'] + 1) / top_k
        score = 75.0 * rank_bonus
    elif result['best_position_hits'] >= 3:
        # 3桁位置一致: 45%のスコア（40→45に改善）
        score = 45.0
    elif result['best_digit_hits'] >= 3:
        # 3桁数字一致: 35%のスコア（30→35に改善）
        score = 35.0
    elif result['best_position_hits'] >= 2:
        # 2桁位置一致: 18%のスコア（15→18に改善）
        score = 18.0
    elif result['best_digit_hits'] >= 2:
        # 2桁数字一致: 12%のスコア（10→12に改善）
        score = 12.0
    
    # NEW: 連続性ボーナス（複数の良い予測があれば加点）
    if len(good_preds) >= 3:
        score *= 1.15  # 3つ以上の良い予測: 15%ボーナス
    elif len(good_preds) >= 2:
        score *= 1.08  # 2つの良い予測: 8%ボーナス
    
    # スコアの上限を100に
    result['score'] = min(100.0, score)
    return result


def _list_candidate_draws(max_draw: int, lookback: int = 120) -> List[int]:
    """
    手法別予測JSONが存在しそうな回号候補を取得する（新形式 numbers4_{draw}.json）。
    """
    draws = set()
    start_draw = max(1, max_draw - lookback + 1)
    for method in ALL_METHODS:
        method_dir = os.path.join(METHODS_DIR, method)
        if not os.path.isdir(method_dir):
            continue
        pattern = os.path.join(method_dir, "numbers4_*.json")
        for path in glob.glob(pattern):
            name = os.path.basename(path)
            try:
                draw = int(name.replace("numbers4_", "").replace(".json", ""))
            except ValueError:
                continue
            if start_draw <= draw <= max_draw:
                draws.add(draw)
    return sorted(draws)


def collect_recent_performance(
    target_draw: int,
    top_k: int = 100,
    window: int = 30,
    lookback_scan: int = 120,
    half_life: float = 10.0,
) -> Tuple[Dict[str, Dict], List[int]]:
    """
    直近window回の評価を集約し、手法別の成績サマリを返す。

    Returns:
      (method_performance, evaluated_draws)
    """
    candidate_draws = _list_candidate_draws(target_draw, lookback=lookback_scan)
    # 実際に当選結果がある回だけ評価対象
    evaluated_draws: List[int] = []
    for d in candidate_draws:
        if get_actual_result(d):
            evaluated_draws.append(d)
    if window > 0:
        evaluated_draws = evaluated_draws[-window:]

    if not evaluated_draws:
        return {}, []

    # 最新回ほど重みを高くする
    newest = max(evaluated_draws)
    weighted_stats = {
        method: {
            "weight_sum": 0.0,
            "score_sum": 0.0,
            "top20_hit_sum": 0.0,
            "top100_hit_sum": 0.0,
            "digit_hits_sum": 0.0,
            "position_hits_sum": 0.0,
            "sample_count": 0,
        }
        for method in ALL_METHODS
    }

    for draw in evaluated_draws:
        actual = get_actual_result(draw)
        if not actual:
            continue
        age = newest - draw
        recency_weight = math.exp(-math.log(2) * age / max(half_life, 1e-6))

        for method in ALL_METHODS:
            preds = load_method_predictions(draw, method)
            if not preds:
                continue

            e = evaluate_method(preds, actual, top_k=top_k)
            top20_hit = 1.0 if (
                (e.get("straight_rank") and e["straight_rank"] <= 20)
                or (e.get("box_rank") and e["box_rank"] <= 20)
            ) else 0.0
            top100_hit = 1.0 if (e.get("straight_rank") or e.get("box_rank")) else 0.0

            st = weighted_stats[method]
            st["weight_sum"] += recency_weight
            st["score_sum"] += e["score"] * recency_weight
            st["top20_hit_sum"] += top20_hit * recency_weight
            st["top100_hit_sum"] += top100_hit * recency_weight
            st["digit_hits_sum"] += e["best_digit_hits"] * recency_weight
            st["position_hits_sum"] += e["best_position_hits"] * recency_weight
            st["sample_count"] += 1

    method_performance: Dict[str, Dict] = {}
    for method, st in weighted_stats.items():
        wsum = st["weight_sum"]
        if wsum <= 0:
            continue
        avg_score = st["score_sum"] / wsum
        top20_rate = st["top20_hit_sum"] / wsum
        top100_rate = st["top100_hit_sum"] / wsum
        avg_digit_hits = st["digit_hits_sum"] / wsum
        avg_position_hits = st["position_hits_sum"] / wsum

        # 当選直結重視の合成スコア（0-1想定）
        performance_index = (
            0.45 * (avg_score / 100.0) +
            0.25 * top20_rate +
            0.15 * top100_rate +
            0.10 * (avg_digit_hits / 4.0) +
            0.05 * (avg_position_hits / 4.0)
        )

        method_performance[method] = {
            "weighted_avg_score": avg_score,
            "top20_hit_rate": top20_rate,
            "top100_hit_rate": top100_rate,
            "avg_digit_hits": avg_digit_hits,
            "avg_position_hits": avg_position_hits,
            "performance_index": performance_index,
            "sample_count": st["sample_count"],
        }

    return method_performance, evaluated_draws


def collect_weekday_market_profile(
    evaluated_draws: List[int],
    top_k: int = 100,
    half_life: float = 20.0,
) -> Dict[int, Dict]:
    """
    曜日ごとの「当たりやすさ/荒れやすさ」プロファイルを作る。
    """
    if not evaluated_draws:
        return {}

    newest = max(evaluated_draws)
    weekday_bucket = defaultdict(lambda: {
        "weight_sum": 0.0,
        "peak_score_sum": 0.0,          # 各回の最高手法スコア(0-1)
        "top20_method_rate_sum": 0.0,   # top20ヒット手法比率
        "dispersion_sum": 0.0,          # 手法スコア分散
        "count": 0,
    })

    for draw in evaluated_draws:
        actual = get_actual_result(draw)
        wd = get_draw_weekday(draw)
        if not actual or wd is None:
            continue

        day_scores = []
        top20_hits = 0
        method_count = 0
        for method in ALL_METHODS:
            preds = load_method_predictions(draw, method)
            if not preds:
                continue
            e = evaluate_method(preds, actual, top_k=top_k)
            s = e.get("score", 0.0) / 100.0
            day_scores.append(s)
            method_count += 1
            if (
                (e.get("straight_rank") and e["straight_rank"] <= 20) or
                (e.get("box_rank") and e["box_rank"] <= 20)
            ):
                top20_hits += 1

        if method_count == 0 or not day_scores:
            continue

        age = newest - draw
        w = math.exp(-math.log(2) * age / max(half_life, 1e-6))
        peak_score = max(day_scores)
        top20_method_rate = top20_hits / method_count
        mean_s = sum(day_scores) / len(day_scores)
        disp = math.sqrt(sum((x - mean_s) ** 2 for x in day_scores) / len(day_scores))

        b = weekday_bucket[wd]
        b["weight_sum"] += w
        b["peak_score_sum"] += peak_score * w
        b["top20_method_rate_sum"] += top20_method_rate * w
        b["dispersion_sum"] += disp * w
        b["count"] += 1

    profile = {}
    for wd, b in weekday_bucket.items():
        if b["weight_sum"] <= 0:
            continue
        avg_peak = b["peak_score_sum"] / b["weight_sum"]
        avg_top20 = b["top20_method_rate_sum"] / b["weight_sum"]
        avg_disp = b["dispersion_sum"] / b["weight_sum"]
        # 曜日強度（高いほど荒れ・追従優先）
        intensity = 0.55 * avg_peak + 0.30 * avg_top20 + 0.15 * min(1.0, avg_disp * 2.0)
        profile[wd] = {
            "sample_count": b["count"],
            "avg_peak_score": avg_peak,
            "avg_top20_method_rate": avg_top20,
            "avg_method_dispersion": avg_disp,
            "intensity": intensity,
        }
    return profile


def update_method_weights(
    current_weights: Dict[str, float],
    evaluations: Dict[str, Dict],
    recent_performance: Optional[Dict[str, Dict]] = None,
    learning_rate: float = 0.10  # 0.08→0.10に増加（より敏感に反応）
) -> Dict[str, float]:
    """
    評価結果に基づいて手法別重みを更新（v2.0 改善版）
    
    改善点:
    - 適応的学習率: 成績に応じて学習率を調整
    - 相対評価: 他の手法との比較で重みを決定
    - ストレート/ボックス一致には特別ボーナス
    - 連続して良い成績の手法にはモメンタムボーナス
    """
    new_weights = current_weights.copy()
    if recent_performance is None:
        recent_performance = {}

    # 直近パフォーマンスの平均（相対比較基準）
    perf_values = [p["performance_index"] for p in recent_performance.values()]
    avg_perf = sum(perf_values) / len(perf_values) if perf_values else 0.0

    for method in ALL_METHODS:
        if method not in new_weights:
            new_weights[method] = 10.0

        curr = new_weights[method]
        recent = recent_performance.get(method)
        today = evaluations.get(method, {})

        # --- 1) 直近成績ベースの更新（メイン） ---
        # 平均より良ければ増、悪ければ減
        if recent:
            relative = recent["performance_index"] - avg_perf
            # 変化率を緩やかに制限（急変防止）
            delta_ratio = max(-0.30, min(0.30, relative * 2.0))
            curr *= (1.0 + learning_rate * delta_ratio)
        else:
            # サンプル不足手法は少しだけ減衰（データ不足時の過信を避ける）
            curr *= (1.0 - learning_rate * 0.05)

        # --- 2) 当日結果の即時反映（短期シグナル） ---
        if today:
            if today.get("straight_rank"):
                rank = today["straight_rank"]
                bonus = 1.0 + min(0.20, (101 - rank) / 100.0 * 0.20)
                curr *= bonus
            elif today.get("box_rank"):
                rank = today["box_rank"]
                bonus = 1.0 + min(0.12, (101 - rank) / 100.0 * 0.12)
                curr *= bonus
            else:
                # 当日ミスでも過剰に落としすぎない
                curr *= (1.0 - learning_rate * 0.03)

            if today.get("good_predictions_count", 0) >= 3:
                curr *= 1.03

        # 範囲クリップ
        new_weights[method] = max(1.0, min(60.0, curr))
    
    # 正規化（合計を元の合計に近づける）
    total_old = sum(current_weights.values())
    total_new = sum(new_weights.values())
    if total_new > 0:
        scale = total_old / total_new
        new_weights = {k: v * scale for k, v in new_weights.items()}
    
    return new_weights


def compute_adaptive_learning_rate(
    evaluations: Dict[str, Dict],
    recent_performance: Dict[str, Dict],
    target_weekday: Optional[int] = None,
    weekday_profile: Optional[Dict[int, Dict]] = None,
    base_lr: float = 0.10,
    lr_min: float = 0.05,
    lr_max: float = 0.20,
    dynamic_bounds: bool = True,
) -> Tuple[float, Dict[str, float]]:
    """
    直近成績と当日シグナルから適応的に learning_rate を算出する。

    考え方:
    - 成績のばらつきが大きい: 追従を速める（lr上げる）
    - 履歴カバレッジが低い: 不確実性が高い（lrやや上げる）
    - 当日ヒットが強い: シグナル強（lr上げる）
    - どれも弱い: ベース寄り or 低め
    """
    perf_values = [p.get("performance_index", 0.0) for p in recent_performance.values()]
    if perf_values:
        mean_perf = sum(perf_values) / len(perf_values)
        variance = sum((x - mean_perf) ** 2 for x in perf_values) / len(perf_values)
        std_perf = math.sqrt(max(0.0, variance))
        # 0.0〜1.0程度に丸める
        dispersion = min(1.0, std_perf / max(mean_perf, 1e-6))
    else:
        mean_perf = 0.0
        std_perf = 0.0
        dispersion = 0.0

    coverage = min(1.0, len(recent_performance) / max(len(ALL_METHODS), 1))
    uncertainty = 1.0 - coverage

    eval_scores = [e.get("score", 0.0) for e in evaluations.values()]
    today_peak = (max(eval_scores) / 100.0) if eval_scores else 0.0
    straight_hit = any(e.get("straight_rank") for e in evaluations.values())
    box_hit = any(e.get("box_rank") for e in evaluations.values())
    hit_bonus = 0.04 if straight_hit else (0.02 if box_hit else 0.0)

    # 相場レジーム（荒れ/安定）推定
    if dispersion >= 0.33 or today_peak >= 0.55 or straight_hit:
        regime = "volatile"
    elif dispersion <= 0.18 and today_peak <= 0.35 and not box_hit:
        regime = "stable"
    else:
        regime = "mixed"

    # 曜日バイアス（曜日ごとの相場傾向）
    weekday_regime = "neutral"
    weekday_bias = 0.0
    weekday_intensity = None
    weekday_samples = 0
    if weekday_profile is None:
        weekday_profile = {}
    if target_weekday is not None and target_weekday in weekday_profile:
        wp = weekday_profile[target_weekday]
        weekday_intensity = wp.get("intensity")
        weekday_samples = int(wp.get("sample_count", 0))
        # サンプルが少なすぎる場合は中立扱い
        if weekday_samples >= 4 and weekday_intensity is not None:
            if weekday_intensity >= 0.44:
                weekday_regime = "volatile_tilt"
                weekday_bias = 0.015
            elif weekday_intensity <= 0.30:
                weekday_regime = "stable_tilt"
                weekday_bias = -0.010

    # レジームに応じて lr 範囲を動的調整
    effective_lr_min = lr_min
    effective_lr_max = lr_max
    if dynamic_bounds:
        if regime == "volatile":
            # 荒れ相場: 追従を速める（範囲を上寄せ）
            effective_lr_min = max(0.04, lr_min * 1.15)
            effective_lr_max = min(0.30, lr_max * 1.25)
        elif regime == "stable":
            # 安定相場: 過剰反応を抑える（範囲を下寄せ）
            effective_lr_min = max(0.03, lr_min * 0.85)
            effective_lr_max = min(0.30, max(effective_lr_min + 0.02, lr_max * 0.80))
        else:
            # mixed は軽微調整
            effective_lr_min = lr_min
            effective_lr_max = lr_max

        # 曜日傾向で範囲を微調整
        if weekday_regime == "volatile_tilt":
            effective_lr_min = max(0.03, effective_lr_min * 1.05)
            effective_lr_max = min(0.30, effective_lr_max * 1.10)
        elif weekday_regime == "stable_tilt":
            effective_lr_min = max(0.03, effective_lr_min * 0.95)
            effective_lr_max = min(0.30, max(effective_lr_min + 0.02, effective_lr_max * 0.90))

    # 線形合成（直感的に調整しやすい係数）
    lr = (
        base_lr
        + 0.06 * dispersion
        + 0.03 * uncertainty
        + 0.03 * today_peak
        + hit_bonus
        + weekday_bias
    )
    lr = max(effective_lr_min, min(effective_lr_max, lr))

    details = {
        "base_lr": base_lr,
        "dispersion": dispersion,
        "uncertainty": uncertainty,
        "today_peak": today_peak,
        "hit_bonus": hit_bonus,
        "regime": regime,
        "target_weekday": target_weekday,
        "weekday_regime": weekday_regime,
        "weekday_bias": weekday_bias,
        "weekday_intensity": weekday_intensity,
        "weekday_samples": weekday_samples,
        "coverage": coverage,
        "mean_perf": mean_perf,
        "std_perf": std_perf,
        "dynamic_bounds": dynamic_bounds,
        "lr_min": lr_min,
        "lr_max": lr_max,
        "effective_lr_min": effective_lr_min,
        "effective_lr_max": effective_lr_max,
    }
    return lr, details


def main():
    parser = argparse.ArgumentParser(
        description='手法別予測の精度評価と重み更新'
    )
    parser.add_argument(
        '--draw', type=int, required=True,
        help='対象抽選回号'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='詳細を表示'
    )
    parser.add_argument(
        '--no-update', action='store_true',
        help='重み更新をスキップ'
    )
    parser.add_argument(
        '--top-k', type=int, default=100,
        help='評価対象のTop-K（デフォルト: 100）'
    )
    parser.add_argument(
        '--window', type=int, default=40,
        help='直近評価に使う回数（デフォルト: 40）'
    )
    parser.add_argument(
        '--half-life', type=float, default=20.0,
        help='直近評価の半減期（回数, デフォルト: 20.0）'
    )
    parser.add_argument(
        '--learning-rate', type=float, default=None,
        help='手動指定の学習率（指定時は自動LRを無効化）'
    )
    parser.add_argument(
        '--base-lr', type=float, default=0.10,
        help='自動LRの基準値（デフォルト: 0.10）'
    )
    parser.add_argument(
        '--lr-min', type=float, default=0.05,
        help='自動LRの下限（デフォルト: 0.05）'
    )
    parser.add_argument(
        '--lr-max', type=float, default=0.20,
        help='自動LRの上限（デフォルト: 0.20）'
    )
    parser.add_argument(
        '--no-dynamic-lr-bounds', action='store_true',
        help='相場レジームによるlr最小/最大の自動調整を無効化'
    )
    
    args = parser.parse_args()
    
    print(f"📊 手法別予測の精度評価: 第{args.draw}回")
    print("=" * 60)
    
    # 当選番号を取得
    actual = get_actual_result(args.draw)
    if not actual:
        print(f"❌ 第{args.draw}回の当選番号が見つかりません")
        sys.exit(1)
    
    print(f"🎰 当選番号: {actual}")
    print()
    
    # 現在の重みを読み込み
    current_weights = load_method_weights()
    
    # 各手法を評価
    evaluations = {}
    
    for method in ALL_METHODS:
        predictions = load_method_predictions(args.draw, method)
        
        if not predictions:
            if args.verbose:
                print(f"  {method:25s}: ⚠️ 予測データなし")
            continue
        
        evaluation = evaluate_method(predictions, actual, args.top_k)
        evaluations[method] = evaluation
        
        # 結果を表示
        if evaluation['straight_rank']:
            status = f"🎯 {evaluation['straight_rank']:3d}位 (ストレート!)"
        elif evaluation['box_rank']:
            status = f"📦 {evaluation['box_rank']:3d}位 (ボックス!)"
        elif evaluation['best_position_hits'] >= 3:
            status = f"🔥 {evaluation['best_position_hits']}桁位置一致"
        elif evaluation['best_digit_hits'] >= 3:
            status = f"🎲 {evaluation['best_digit_hits']}桁数字一致"
        elif evaluation['best_position_hits'] >= 2:
            status = f"📈 {evaluation['best_position_hits']}桁位置一致"
        else:
            status = f"❌ 予測外"
        
        print(f"  {method:25s}: {status:30s} (スコア: {evaluation['score']:.1f})")
    
    print()

    # 直近成績の集約（重み更新の主材料）
    recent_performance, recent_draws = collect_recent_performance(
        target_draw=args.draw,
        top_k=args.top_k,
        window=args.window,
        half_life=args.half_life,
    )
    weekday_profile = collect_weekday_market_profile(
        evaluated_draws=recent_draws,
        top_k=args.top_k,
        half_life=args.half_life,
    )
    target_weekday = get_draw_weekday(args.draw)
    if recent_draws:
        print(
            f"📈 直近成績集約: {len(recent_draws)}回 "
            f"(第{recent_draws[0]}回〜第{recent_draws[-1]}回, half_life={args.half_life})"
        )
    else:
        print("⚠️ 直近成績集約に使えるデータがありません（当日評価のみで更新）")
    if args.verbose and recent_performance:
        print("\n【直近成績（performance_index順）】")
        ranked_perf = sorted(
            recent_performance.items(),
            key=lambda x: x[1]["performance_index"],
            reverse=True
        )
        for method, perf in ranked_perf:
            print(
                f"  {method:25s}: idx={perf['performance_index']:.3f}, "
                f"top20={perf['top20_hit_rate']:.2%}, top100={perf['top100_hit_rate']:.2%}, "
                f"avg_score={perf['weighted_avg_score']:.1f}, samples={perf['sample_count']}"
            )
    if args.verbose and weekday_profile:
        weekday_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        print("\n【曜日別マーケット強度】")
        for wd in sorted(weekday_profile.keys()):
            p = weekday_profile[wd]
            label = weekday_name[wd] if 0 <= wd <= 6 else str(wd)
            print(
                f"  {label:3s}: intensity={p['intensity']:.3f}, "
                f"peak={p['avg_peak_score']:.3f}, top20_rate={p['avg_top20_method_rate']:.2%}, "
                f"samples={p['sample_count']}"
            )

    # 学習率を決定（手動指定 > 自動推定）
    if args.learning_rate is not None:
        chosen_lr = max(args.lr_min, min(args.lr_max, args.learning_rate))
        lr_details = {
            "mode": "manual",
            "requested_learning_rate": args.learning_rate,
            "applied_learning_rate": chosen_lr,
            "lr_min": args.lr_min,
            "lr_max": args.lr_max,
        }
    else:
        chosen_lr, auto_details = compute_adaptive_learning_rate(
            evaluations=evaluations,
            recent_performance=recent_performance,
            target_weekday=target_weekday,
            weekday_profile=weekday_profile,
            base_lr=args.base_lr,
            lr_min=args.lr_min,
            lr_max=args.lr_max,
            dynamic_bounds=(not args.no_dynamic_lr_bounds),
        )
        lr_details = {"mode": "adaptive", **auto_details, "applied_learning_rate": chosen_lr}

    print(f"⚙️ 適用learning_rate: {chosen_lr:.4f} ({lr_details['mode']})")
    if args.verbose:
        print(f"   details: {lr_details}")
    
    if not evaluations:
        print("⚠️ 評価可能な手法がありません")
        sys.exit(0)
    
    # 重みを更新
    if not args.no_update:
        print("🔧 重みを更新中...")
        new_weights = update_method_weights(
            current_weights=current_weights,
            evaluations=evaluations,
            recent_performance=recent_performance,
            learning_rate=chosen_lr,
        )
        
        if args.verbose:
            print("\n【重みの変化】")
            for method in sorted(current_weights.keys()):
                old_w = current_weights.get(method, 10.0)
                new_w = new_weights.get(method, 10.0)
                change = new_w - old_w
                sign = "+" if change >= 0 else ""
                print(f"  {method:25s}: {old_w:6.2f} → {new_w:6.2f} ({sign}{change:.2f})")
        
        # 保存
        metadata = {
            'draw_number': args.draw,
            'actual_number': actual,
            'evaluations': evaluations,
            'recent_window': args.window,
            'recent_draws': recent_draws,
            'recent_performance': recent_performance,
            'target_weekday': target_weekday,
            'weekday_profile': weekday_profile,
            'learning_rate': chosen_lr,
            'learning_rate_details': lr_details,
        }
        save_method_weights(new_weights, metadata)
        print("\n✅ 手法別重みを更新・保存しました")
    
    print("=" * 60)
    
    # サマリー
    best_method = max(evaluations.items(), key=lambda x: x[1]['score'])
    print(f"🏆 最優秀手法: {best_method[0]} (スコア: {best_method[1]['score']:.1f})")
    
    # ストレート/ボックス一致があれば特別表示
    for method, eval_result in evaluations.items():
        if eval_result['straight_rank']:
            print(f"🎉 {method} がストレート一致！（{eval_result['straight_rank']}位）")
        elif eval_result['box_rank']:
            print(f"📦 {method} がボックス一致！（{eval_result['box_rank']}位）")


if __name__ == '__main__':
    main()

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from tools.utils import get_db_connection


@dataclass(frozen=True)
class GovernanceBucket:
    slug: str
    bucket: str
    multiplier: float


def _multiplier_for_bucket(bucket: str) -> float:
    if bucket == "preferred":
        return 1.0
    if bucket == "watch":
        return 0.85
    if bucket == "deprioritized":
        return 0.55
    return 0.75


def classify_numbers4_metrics(hit_rate_pct: float, top10_pct: float) -> str:
    if top10_pct >= 18 or hit_rate_pct >= 35:
        return "preferred"
    if top10_pct <= 6 and hit_rate_pct <= 18:
        return "deprioritized"
    return "watch"


def classify_numbers3_metrics(hit_rate_pct: float, exact_hits: int, box_hits: int) -> str:
    if hit_rate_pct >= 25 or exact_hits >= 2:
        return "preferred"
    if hit_rate_pct <= 10 and exact_hits == 0 and box_hits <= 1:
        return "deprioritized"
    return "watch"


def _load_latest_top_predictions(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    predictions = payload.get("predictions") or []
    if not predictions:
        return []
    latest = predictions[-1] or {}
    rows = latest.get("top_predictions") or []
    out: List[str] = []
    for row in rows:
        number = str(row.get("number", "")).strip()
        if number:
            out.append(number)
    return out


def _normalize_number(number: str | None, digits: int) -> str | None:
    if number is None:
        return None
    raw = "".join(ch for ch in str(number) if ch.isdigit())
    if not raw or len(raw) > digits:
        return None
    return raw.zfill(digits)


def _box_key(number: str | None, digits: int) -> str | None:
    normalized = _normalize_number(number, digits)
    if not normalized:
        return None
    return "".join(sorted(normalized))


def _box_hit_rank(predictions: Sequence[str], winning: str, digits: int, limit: int) -> int | None:
    winning_key = _box_key(winning, digits)
    if not winning_key:
        return None
    for index, prediction in enumerate(predictions[:limit]):
        if _box_key(prediction, digits) == winning_key:
            return index + 1
    return None


def _has_exact_hit(predictions: Sequence[str], winning: str, digits: int, limit: int) -> bool:
    normalized_winning = _normalize_number(winning, digits)
    if not normalized_winning:
        return False
    return any(
        _normalize_number(prediction, digits) == normalized_winning
        for prediction in predictions[:limit]
    )


def apply_trust_first_weights(
    weights: Dict[str, float],
    governance: Dict[str, GovernanceBucket],
) -> Dict[str, float]:
    adjusted: Dict[str, float] = {}
    for slug, raw_weight in weights.items():
        bucket = governance.get(slug)
        multiplier = bucket.multiplier if bucket else _multiplier_for_bucket("unknown")
        adjusted[slug] = round(float(raw_weight) * multiplier, 4)
    return adjusted


def apply_trust_first_hot_models(
    hot_models: Iterable[Tuple[str, float]],
    governance: Dict[str, GovernanceBucket],
) -> List[Tuple[str, float]]:
    adjusted: List[Tuple[str, float]] = []
    for slug, score in hot_models:
        bucket = governance.get(slug)
        multiplier = bucket.multiplier if bucket else _multiplier_for_bucket("unknown")
        adjusted.append((slug, round(float(score) * multiplier, 4)))
    adjusted.sort(key=lambda item: item[1], reverse=True)
    return adjusted


def _load_recent_draws(table: str, limit: int) -> List[Tuple[int, str]]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT draw_number, numbers
            FROM {table}
            WHERE numbers IS NOT NULL AND TRIM(numbers) != ''
            ORDER BY draw_number DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        conn.close()

    return [(int(row["draw_number"]), str(row["numbers"])) for row in rows]


def compute_numbers4_governance(
    methods: Sequence[str],
    recent_limit: int = 30,
    predictions_root: str | None = None,
) -> Dict[str, GovernanceBucket]:
    base_dir = predictions_root or os.path.join("predictions", "daily", "methods")
    draws = _load_recent_draws("numbers4_draws", recent_limit)
    sample_size = max(len(draws), 1)
    result: Dict[str, GovernanceBucket] = {}

    for method in methods:
        hit_any = 0
        hit_top10 = 0
        for draw_number, winning in draws:
            file_path = os.path.join(base_dir, method, f"numbers4_{draw_number}.json")
            predictions = _load_latest_top_predictions(file_path)
            rank = _box_hit_rank(predictions, winning, digits=4, limit=20)
            if rank is not None:
                hit_any += 1
                if rank <= 10:
                    hit_top10 += 1

        hit_rate_pct = (hit_any / sample_size) * 100
        top10_pct = (hit_top10 / sample_size) * 100
        bucket = classify_numbers4_metrics(hit_rate_pct, top10_pct)
        result[method] = GovernanceBucket(
            slug=method,
            bucket=bucket,
            multiplier=_multiplier_for_bucket(bucket),
        )

    return result


def compute_numbers3_governance(
    methods: Sequence[str],
    recent_limit: int = 20,
    predictions_root: str | None = None,
) -> Dict[str, GovernanceBucket]:
    base_dir = predictions_root or os.path.join("predictions", "daily", "methods")
    draws = _load_recent_draws("numbers3_draws", recent_limit)
    sample_size = max(len(draws), 1)
    result: Dict[str, GovernanceBucket] = {}

    for method in methods:
        exact_hits = 0
        box_hits = 0
        for draw_number, winning in draws:
            file_path = os.path.join(base_dir, method, f"numbers3_{draw_number}.json")
            predictions = _load_latest_top_predictions(file_path)
            if _has_exact_hit(predictions, winning, digits=3, limit=20):
                exact_hits += 1
            if _box_hit_rank(predictions, winning, digits=3, limit=20) is not None:
                if not _has_exact_hit(predictions, winning, digits=3, limit=20):
                    box_hits += 1

        hit_rate_pct = ((exact_hits + box_hits) / sample_size) * 100
        bucket = classify_numbers3_metrics(hit_rate_pct, exact_hits, box_hits)
        result[method] = GovernanceBucket(
            slug=method,
            bucket=bucket,
            multiplier=_multiplier_for_bucket(bucket),
        )

    return result

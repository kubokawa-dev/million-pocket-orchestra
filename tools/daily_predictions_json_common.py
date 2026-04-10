"""
predictions/daily 配下の JSON を走査する共通処理（SQLite / PostgREST 取り込み用）。
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAILY = ROOT / "predictions" / "daily"


@dataclass(frozen=True)
class DailyPredictionRecord:
    target_draw_number: int
    doc_kind: str
    method_slug: str
    relative_path: str
    payload: object
    payload_sha256: str
    file_mtime: str


def classify_json_path_for_lottery(
    path: Path,
    *,
    lottery: str,
) -> tuple[str, int, str] | None:
    """(doc_kind, target_draw_number, method_slug) を返す。対象外は None。"""
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return None

    m = re.fullmatch(
        rf"predictions/daily/methods/([^/]+)/{re.escape(lottery)}_(\d+)\.json",
        rel,
    )
    if m:
        return ("method", int(m.group(2)), m.group(1))

    m = re.fullmatch(rf"predictions/daily/{re.escape(lottery)}_(\d+)\.json", rel)
    if m:
        return ("ensemble", int(m.group(1)), "")

    if lottery == "numbers4":
        m = re.fullmatch(r"predictions/daily/budget_plan_(\d+)\.json", rel)
        if m:
            return ("budget_plan", int(m.group(1)), "")
    elif lottery == "numbers3":
        m = re.fullmatch(r"predictions/daily/budget_plan_numbers3_(\d+)\.json", rel)
        if m:
            return ("budget_plan", int(m.group(1)), "")

    return None


def classify_json_path(path: Path) -> tuple[str, int, str] | None:
    """numbers4 既定の分類（後方互換）。"""
    return classify_json_path_for_lottery(path, lottery="numbers4")


def collect_daily_prediction_records_for_lottery(
    *,
    lottery: str,
    target_draw_number: int | None = None,
) -> tuple[list[DailyPredictionRecord], int]:
    """日次 JSON を読み込み、レコード一覧とスキップ数を返す。

    target_draw_number を指定したときはその回号のファイルだけ取り込む。
    """
    records: list[DailyPredictionRecord] = []
    skipped = 0

    if not DAILY.is_dir():
        return records, skipped

    for path in sorted(DAILY.rglob("*.json")):
        meta = classify_json_path_for_lottery(path, lottery=lottery)
        if not meta:
            skipped += 1
            continue
        doc_kind, draw, method_slug = meta
        if target_draw_number is not None and draw != target_draw_number:
            skipped += 1
            continue
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        try:
            obj = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            skipped += 1
            continue
        sha = hashlib.sha256(raw).hexdigest()
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        mtime_iso = mtime.replace(microsecond=0).isoformat()
        records.append(
            DailyPredictionRecord(
                target_draw_number=draw,
                doc_kind=doc_kind,
                method_slug=method_slug,
                relative_path=rel,
                payload=obj,
                payload_sha256=sha,
                file_mtime=mtime_iso,
            )
        )

    return records, skipped


def collect_daily_prediction_records(
    target_draw_number: int | None = None,
) -> tuple[list[DailyPredictionRecord], int]:
    """numbers4 既定の収集（後方互換）。"""
    return collect_daily_prediction_records_for_lottery(
        lottery="numbers4",
        target_draw_number=target_draw_number,
    )

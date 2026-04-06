#!/usr/bin/env python3
"""
Numbers4 の指定番号が、手法別予測に含まれるかを検証するツール。

主な用途:
- box_model / cold_revival などで、特定番号が候補にあるかをCIで確認
- 厳密一致(例: 4111) とボックス一致(例: 1411, 1141) を分けて可視化
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_DIR = ROOT / "predictions" / "daily"


def normalize_number(value: str) -> str:
    s = str(value).strip()
    if not s.isdigit():
        raise ValueError(f"number must be digits only: {value}")
    if len(s) > 4:
        raise ValueError(f"number must be 4 digits or less: {value}")
    return s.zfill(4)


def detect_latest_draw() -> int:
    files = sorted(PREDICTIONS_DIR.glob("numbers4_*.json"))
    if not files:
        raise RuntimeError("No numbers4_*.json found under predictions/daily")
    latest = files[-1].stem
    return int(latest.split("_", 1)[1])


def iter_top_predictions(method_file: Path) -> Iterable[dict]:
    data = json.loads(method_file.read_text(encoding="utf-8"))
    for batch in data.get("predictions", []):
        time_jst = batch.get("time_jst", "")
        time_utc = batch.get("time", "")
        for row in batch.get("top_predictions", []):
            number = normalize_number(str(row.get("number", "")))
            rank = int(row.get("rank", 9999))
            score = float(row.get("score", 0.0))
            yield {
                "time_jst": time_jst,
                "time_utc": time_utc,
                "rank": rank,
                "score": score,
                "number": number,
            }


def _check_single_number(draw: int, target_number: str, methods: list[str]) -> str:
    target_box = "".join(sorted(target_number))

    lines: list[str] = []
    lines.append(f"# Numbers4 ターゲット番号チェック")
    lines.append("")
    lines.append(f"- draw: `{draw}`")
    lines.append(f"- target_number: `{target_number}`")
    lines.append(f"- methods: `{', '.join(methods)}`")
    lines.append("")

    missing_methods: list[str] = []
    total_exact_hits = 0
    total_box_hits = 0

    for method in methods:
        path = PREDICTIONS_DIR / "methods" / method / f"numbers4_{draw}.json"
        if not path.exists():
            missing_methods.append(method)
            lines.append(f"## `{method}`")
            lines.append(f"- status: file not found")
            lines.append("")
            continue

        method_data = json.loads(path.read_text(encoding="utf-8"))
        batch_count = len(method_data.get("predictions", []))

        exact_hits: list[dict] = []
        box_hits: list[dict] = []
        for row in iter_top_predictions(path):
            if row["number"] == target_number:
                exact_hits.append(row)
            elif "".join(sorted(row["number"])) == target_box:
                box_hits.append(row)

        total_exact_hits += len(exact_hits)
        total_box_hits += len(box_hits)

        lines.append(f"## `{method}`")
        lines.append(f"- source: `{path.relative_to(ROOT)}`")
        lines.append(f"- prediction_batches: {batch_count}")

        if not exact_hits and not box_hits:
            lines.append("- result: not found in saved top predictions")
            lines.append("")
            continue

        if exact_hits:
            lines.append(f"- exact_hit_count: {len(exact_hits)}")
            best_exact = sorted(exact_hits, key=lambda x: x["rank"])[0]
            lines.append(
                f"- best_exact_rank: {best_exact['rank']} (time_jst: {best_exact['time_jst']}, score: {best_exact['score']:.1f})"
            )
        else:
            lines.append("- exact_hit_count: 0")

        if box_hits:
            lines.append(f"- box_hit_count: {len(box_hits)}")
            best_box = sorted(box_hits, key=lambda x: x["rank"])[0]
            lines.append(
                f"- best_box_rank: {best_box['rank']} (number: {best_box['number']}, time_jst: {best_box['time_jst']}, score: {best_box['score']:.1f})"
            )
        else:
            lines.append("- box_hit_count: 0")
        lines.append("")

    lines.append("## 判定")
    if total_exact_hits > 0:
        verdict = "exact_hit"
        reason = "指定番号そのものが候補に含まれています。"
    elif total_box_hits > 0:
        verdict = "box_only_hit"
        reason = "指定番号そのものは無いが、ボックス一致の候補があります。"
    else:
        verdict = "not_found"
        reason = "保存済みTOP候補では確認できませんでした。"
    lines.append(f"- verdict: `{verdict}`")
    lines.append(f"- reason: {reason}")
    lines.append(f"- total_exact_hits: {total_exact_hits}")
    lines.append(f"- total_box_hits: {total_box_hits}")
    if missing_methods:
        lines.append(f"- missing_methods: `{', '.join(missing_methods)}`")
    lines.append("")
    lines.append("> NOTE: この判定は各メソッドJSONに保存された `top_predictions` の範囲で行っています。")
    return "\n".join(lines) + "\n"


def _parse_numbers(number: str, numbers: str) -> list[str]:
    values: list[str] = []
    if number:
        values.append(number)
    if numbers:
        values.extend([s.strip() for s in numbers.split(",") if s.strip()])
    if not values:
        values = ["4111"]

    normalized: list[str] = []
    seen = set()
    for value in values:
        n = normalize_number(value)
        if n in seen:
            continue
        seen.add(n)
        normalized.append(n)
    return normalized


def check_numbers(draw: int, target_numbers: list[str], methods: list[str]) -> str:
    sections = []
    for n in target_numbers:
        sections.append(_check_single_number(draw=draw, target_number=n, methods=methods).strip())
    return "\n\n---\n\n".join(sections) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Numbers4 target number checker")
    parser.add_argument("--draw", type=int, default=None, help="対象回号（未指定なら最新）")
    parser.add_argument("--number", type=str, default="", help="検証する4桁番号（単体指定）")
    parser.add_argument("--numbers", type=str, default="", help="検証する4桁番号（カンマ区切り）")
    parser.add_argument(
        "--methods",
        type=str,
        default="box_model,cold_revival",
        help="カンマ区切りの手法名",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="出力Markdownファイル（未指定なら標準出力のみ）",
    )
    args = parser.parse_args()

    draw = args.draw if args.draw is not None else detect_latest_draw()
    target_numbers = _parse_numbers(number=args.number, numbers=args.numbers)
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    if not methods:
        raise ValueError("methods is empty")

    markdown = check_numbers(draw=draw, target_numbers=target_numbers, methods=methods)
    print(markdown)

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        print(f"saved: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

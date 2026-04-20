#!/usr/bin/env python3
"""
ロト6 MVP の手法別 JSON に、指定の本数字（＋任意でボーナス）が載っているかを検証する。

Numbers4 の tools/check_numbers4_target_number.py に相当。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_DIR = ROOT / "predictions" / "daily"


def parse_main(s: str) -> tuple[int, ...]:
    parts = [p.strip() for p in s.replace(" ", "").split(",") if p.strip()]
    nums: list[int] = []
    for p in parts:
        if not p.isdigit():
            raise ValueError(f"invalid main digit: {p}")
        n = int(p)
        if not (1 <= n <= 43):
            raise ValueError(f"main out of range 1-43: {n}")
        nums.append(n)
    if len(nums) != 6:
        raise ValueError(f"main must be exactly 6 numbers (got {len(nums)})")
    if len(set(nums)) != 6:
        raise ValueError("main numbers must be unique")
    return tuple(sorted(nums))


def detect_latest_draw() -> int:
    files = sorted(PREDICTIONS_DIR.glob("loto6_*.json"))
    if not files:
        raise RuntimeError("No loto6_*.json found under predictions/daily")
    stem = files[-1].stem
    return int(stem.split("_", 1)[1])


def iter_top_predictions(method_file: Path) -> Iterable[dict]:
    data = json.loads(method_file.read_text(encoding="utf-8"))
    for batch in data.get("predictions", []):
        time_jst = batch.get("time_jst", "")
        time_utc = batch.get("time", "")
        for row in batch.get("top_predictions", []):
            main = row.get("main") or []
            try:
                mains = tuple(sorted(int(x) for x in main))
            except (TypeError, ValueError):
                continue
            if len(mains) != 6:
                continue
            bonus = row.get("bonus")
            try:
                bi = int(bonus) if bonus is not None else None
            except (TypeError, ValueError):
                bi = None
            yield {
                "time_jst": time_jst,
                "time_utc": time_utc,
                "rank": int(row.get("rank", 9999)),
                "score": float(row.get("score", 0.0)),
                "main": mains,
                "bonus": bi,
            }


def _check_single_ticket(
    draw: int,
    target_main: tuple[int, ...],
    target_bonus: int | None,
    methods: list[str],
) -> str:
    lines: list[str] = []
    lines.append("### 照合詳細（MVP JSON）")
    lines.append("")
    lines.append(f"- draw: `{draw}`")
    lines.append(f"- target_main (sorted): `{','.join(str(x) for x in target_main)}`")
    if target_bonus is not None:
        lines.append(f"- target_bonus: `{target_bonus}` (一致も要求)")
    else:
        lines.append("- target_bonus: （未指定・本数字のみ照合）")
    lines.append(f"- methods: `{', '.join(methods)}`")
    lines.append("")

    missing: list[str] = []
    total_main_hits = 0
    total_full_hits = 0

    for method in methods:
        path = PREDICTIONS_DIR / "methods" / method / f"loto6_{draw}.json"
        if not path.exists():
            missing.append(method)
            lines.append(f"#### `{method}`")
            lines.append("- status: file not found")
            lines.append("")
            continue

        main_hits: list[dict] = []
        full_hits: list[dict] = []
        for row in iter_top_predictions(path):
            if row["main"] != target_main:
                continue
            main_hits.append(row)
            if target_bonus is None or row["bonus"] == target_bonus:
                full_hits.append(row)

        total_main_hits += len(main_hits)
        total_full_hits += len(full_hits)

        lines.append(f"#### `{method}`")
        lines.append(f"- source: `{path.relative_to(ROOT)}`")

        if not main_hits:
            lines.append("- result: 本数字の組み合わせは TOP 候補に見つかりませんでした")
            lines.append("")
            continue

        lines.append(f"- main_match_count: {len(main_hits)}")
        best_m = sorted(main_hits, key=lambda x: x["rank"])[0]
        lines.append(
            f"- best_main_rank: {best_m['rank']} (bonus {best_m['bonus']}, "
            f"time_jst: {best_m['time_jst']}, score: {best_m['score']:.1f})"
        )
        if target_bonus is not None:
            lines.append(f"- full_match_count (main+bonus): {len(full_hits)}")
            if full_hits:
                best_f = sorted(full_hits, key=lambda x: x["rank"])[0]
                lines.append(
                    f"- best_full_rank: {best_f['rank']} (time_jst: {best_f['time_jst']})"
                )
        lines.append("")

    lines.append("### 判定")
    if target_bonus is not None:
        if total_full_hits > 0:
            verdict = "full_hit"
            reason = "本数字＋ボーナスが一致する候補が見つかりました。"
        elif total_main_hits > 0:
            verdict = "main_only"
            reason = "本数字は一致するが、ボーナスは一致する候補がありませんでした。"
        else:
            verdict = "not_found"
            reason = "保存済み TOP 候補では確認できませんでした。"
    else:
        if total_main_hits > 0:
            verdict = "main_hit"
            reason = "本数字（6個の組）が候補に含まれています。"
        else:
            verdict = "not_found"
            reason = "保存済み TOP 候補では確認できませんでした。"

    lines.append(f"- verdict: `{verdict}`")
    lines.append(f"- reason: {reason}")
    lines.append(f"- total_main_matches: {total_main_hits}")
    if target_bonus is not None:
        lines.append(f"- total_full_matches: {total_full_hits}")
    if missing:
        lines.append(f"- missing_methods: `{', '.join(missing)}`")
    lines.append("")
    lines.append(
        "> NOTE: 各 `method` JSON の `top_predictions` の範囲での照合です（ロト6 MVP）。"
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Loto6 MVP target ticket checker")
    p.add_argument("--draw", type=int, default=None, help="対象回（未指定なら最新 loto6_*.json）")
    p.add_argument(
        "--main",
        type=str,
        required=True,
        help="照合する本数字6個（カンマ区切り、順不同）",
    )
    p.add_argument(
        "--bonus",
        type=int,
        default=None,
        help="照合するボーナス数字（省略時は本数字のみ）",
    )
    p.add_argument(
        "--methods",
        type=str,
        default="cold_six,hot_six,pair_cooccur",
        help="カンマ区切りの手法スラッグ",
    )
    p.add_argument("--output", type=str, default="", help="Markdown 出力先（省略で stdout のみ）")
    args = p.parse_args()

    draw = args.draw if args.draw is not None else detect_latest_draw()
    target_main = parse_main(args.main)
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    if not methods:
        raise SystemExit("methods is empty")

    md = _check_single_ticket(draw, target_main, args.bonus, methods)
    print(md)

    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        try:
            disp = out.relative_to(ROOT)
        except ValueError:
            disp = out
        print(f"saved: {disp}", file=sys.stderr)


if __name__ == "__main__":
    main()

"""
predictions/daily のロト6 MVP JSON から Markdown サマリーを生成する。

使い方:
  python tools/summarize_loto6_mvp_md.py
  python tools/summarize_loto6_mvp_md.py --draw 2093
  python tools/summarize_loto6_mvp_md.py --draw 2093 --output predictions/loto6_2093.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DAILY = ROOT / "predictions" / "daily"

EXPECTED_METHODS = (
    "cold_six",
    "hot_six",
    "pair_cooccur",
    "last_draw_shift",
    "sum_streak",
    "odd_even_cold",
    "zone_heat",
    "spread_wheel",
)


def latest_draw_from_files() -> int | None:
    best: int | None = None
    if not DAILY.is_dir():
        return None
    for p in DAILY.glob("loto6_*.json"):
        m = re.fullmatch(r"loto6_(\d+)\.json", p.name)
        if not m:
            continue
        n = int(m.group(1))
        if best is None or n > best:
            best = n
    return best


def fmt_main(main: object) -> str:
    if isinstance(main, list):
        return ",".join(str(x) for x in main)
    return str(main)


def append_budget_plan_section(
    lines: list[str],
    draw: int,
    tops: list[dict],
) -> None:
    """budget_plan_loto6 JSON があれば要約。無ければアンサンブル上位からインライン参考。"""
    budget_path = DAILY / f"budget_plan_loto6_{draw}.json"
    lines.append("## 予算プラン（MVP）")
    lines.append("")
    if budget_path.is_file():
        lines.append(f"- JSON: `{budget_path.relative_to(ROOT)}`（`doc_kind: budget_plan` で Supabase に取り込み）")
        try:
            bp = json.loads(budget_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            bp = {}
        for key, label in (("plan_5", "1000円相当"), ("plan_10", "2000円相当")):
            block = bp.get(key) or {}
            recs = block.get("recommendations") or []
            lines.append(f"### {label}")
            lines.append("")
            if not recs:
                lines.append("（候補なし）")
            else:
                for r in recs[:12]:
                    num = r.get("number", "")
                    rs = r.get("reason", "")
                    lines.append(f"- `{num}` — {rs}")
            lines.append("")
        return

    lines.append(
        f"- `budget_plan_loto6_{draw}.json` がまだ無いため、"
        "アンサンブル上位からインライン参考のみ表示します。"
    )
    lines.append("")
    lines.append("### 1000円イメージ（上位5通）")
    lines.append("")
    for i, row in enumerate(tops[:5], start=1):
        lines.append(
            f"{i}. 本数字 `{fmt_main(row.get('main'))}` ・ ボーナス `{row.get('bonus', '')}` "
            f"・ スコア {row.get('score', '')}"
        )
    lines.append("")
    lines.append("### 2000円イメージ（上位10通）")
    lines.append("")
    for i, row in enumerate(tops[:10], start=1):
        lines.append(
            f"{i}. `{fmt_main(row.get('main'))}` / bonus {row.get('bonus', '')} / {row.get('score', '')}"
        )
    lines.append("")


def main() -> None:
    p = argparse.ArgumentParser(description="Loto6 MVP JSON → Markdown")
    p.add_argument("--draw", type=int, default=None, help="対象回（省略時は最新 loto6_*.json）")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="出力パス（省略時は predictions/loto6_{draw}.md）",
    )
    args = p.parse_args()

    draw = args.draw if args.draw is not None else latest_draw_from_files()
    if draw is None:
        print("❌ predictions/daily/loto6_*.json が見つかりません")
        sys.exit(1)

    ens_path = DAILY / f"loto6_{draw}.json"
    if not ens_path.is_file():
        print(f"❌ アンサンブル JSON が無い: {ens_path}")
        sys.exit(1)

    missing = []
    for slug in EXPECTED_METHODS:
        mp = DAILY / "methods" / slug / f"loto6_{draw}.json"
        if not mp.is_file():
            missing.append(slug)

    if missing:
        print(f"⚠️ 未揃いの method（{len(missing)}）: {', '.join(missing)}")
        print("   サマリーは揃っている分だけ出力します")

    ens = json.loads(ens_path.read_text(encoding="utf-8"))
    preds = ens.get("predictions") or []
    last = preds[-1] if preds else {}
    tops = last.get("top_predictions") or []
    weights = last.get("ensemble_weights") or ens.get("ensemble_weights") or {}

    out_path = args.output or (ROOT / "predictions" / f"loto6_{draw}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# ロト6 第{draw}回 MVP 予測サマリー")
    lines.append("")
    lines.append(f"- ソース: `{ens_path.relative_to(ROOT)}`")
    lines.append(f"- 生成: `tools/summarize_loto6_mvp_md.py`")
    lines.append("")

    lines.append("## アンサンブル重み")
    lines.append("")
    if not weights:
        lines.append("（重みなし）")
    else:
        def _w(kv: tuple[str, object]) -> tuple[float, str]:
            v = kv[1]
            try:
                return (-float(v), kv[0])  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return (0.0, kv[0])

        for k, v in sorted(weights.items(), key=_w):
            lines.append(f"- `{k}`: {v}")
    lines.append("")

    lines.append("## アンサンブル上位")
    lines.append("")
    lines.append("| 順位 | 本数字 | ボーナス | スコア |")
    lines.append("| --- | --- | --- | --- |")
    for i, row in enumerate(tops[:18], start=1):
        mn = fmt_main(row.get("main"))
        bn = row.get("bonus", "")
        sc = row.get("score", "")
        lines.append(f"| {i} | {mn} | {bn} | {sc} |")
    lines.append("")

    lines.append("## 手法別（各ファイル先頭ランク抜粋）")
    lines.append("")
    for slug in EXPECTED_METHODS:
        mp = DAILY / "methods" / slug / f"loto6_{draw}.json"
        if not mp.is_file():
            continue
        try:
            data = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pr = (data.get("predictions") or [{}])[-1]
        tps = pr.get("top_predictions") or []
        first = tps[0] if tps else {}
        lines.append(f"### `{slug}`")
        lines.append("")
        lines.append(f"- 先頭: {fmt_main(first.get('main'))} / bonus {first.get('bonus', '')} / score {first.get('score', '')}")
        lines.append("")

    append_budget_plan_section(lines, draw, tops)

    body = "\n".join(lines) + "\n"
    out_path.write_text(body, encoding="utf-8")
    try:
        disp = out_path.relative_to(ROOT)
    except ValueError:
        disp = out_path
    print(f"✅ Wrote {disp} ({len(body)} bytes)")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()

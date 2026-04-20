"""
loto6 アンサンブル JSON から簡易 budget_plan JSON を生成する（Supabase doc_kind=budget_plan 用）。

出力: predictions/daily/budget_plan_loto6_{draw}.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DAILY = ROOT / "predictions" / "daily"


def jst_now_iso() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).replace(microsecond=0).isoformat()


def fmt_main(main: object) -> str:
    if isinstance(main, list):
        return ",".join(str(int(x)) for x in main)
    return str(main)


def main() -> None:
    p = argparse.ArgumentParser(description="Loto6 MVP → budget_plan_loto6_{draw}.json")
    p.add_argument("--draw", type=int, required=True, help="対象回号")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="出力パス（既定: predictions/daily/budget_plan_loto6_{draw}.json）",
    )
    args = p.parse_args()

    draw = args.draw
    ens_path = DAILY / f"loto6_{draw}.json"
    if not ens_path.is_file():
        print(f"❌ アンサンブル JSON が無い: {ens_path}")
        sys.exit(1)

    ens = json.loads(ens_path.read_text(encoding="utf-8"))
    preds = ens.get("predictions") or []
    last = preds[-1] if preds else {}
    tops = last.get("top_predictions") or []

    def recs(slice_: list[dict], *, start_rank: int) -> list[dict]:
        out: list[dict] = []
        for i, row in enumerate(slice_, start=start_rank):
            out.append(
                {
                    "priority": f"#{i}",
                    "number": fmt_main(row.get("main")),
                    "buy_method": "通常（参考）",
                    "reason": f"ensemble rank {row.get('rank', i)} / score {row.get('score', '')}",
                }
            )
        return out

    payload = {
        "target_draw_number": draw,
        "created_at": jst_now_iso(),
        "planner_version": "loto6-mvp-budget-1",
        "monthly_budget_guide": {
            "max_yen_per_month": 30_000,
            "default_per_draw_yen": 1_000,
            "max_per_draw_yen": 2_000,
            "yen_per_ticket": 200,
            "note": (
                "ロト6の実際の券種・口数・当せん金額は公式ルールに従ってください。"
                "ここは MVP アンサンブル上位を「複数候補の割り振り例」として並べた参考 JSON です。"
            ),
        },
        "plan_5": {
            "budget": "1,000円相当（上位5通を候補として列挙）",
            "slots": 5,
            "recommendations": recs(tops[:5], start_rank=1),
        },
        "plan_10": {
            "budget": "2,000円相当（上位10通を候補として列挙）",
            "slots": 10,
            "recommendations": recs(tops[:10], start_rank=1),
        },
    }

    out = args.output or (DAILY / f"budget_plan_loto6_{draw}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

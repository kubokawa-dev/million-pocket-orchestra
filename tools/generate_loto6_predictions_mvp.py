"""
ロト6 MVP 予測 JSON を predictions/daily に出力する。

手法（8）:
  cold_six, hot_six, pair_cooccur, last_draw_shift,
  sum_streak, odd_even_cold, zone_heat, spread_wheel
ensemble: 各手法の同一順位からラウンドロビンで合成。

使い方:
  python tools/generate_loto6_predictions_mvp.py
  python tools/generate_loto6_predictions_mvp.py --target-draw 2093
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.load_loto6_csv_to_postgres import load_all_csv_files  # noqa: E402

ENSEMBLE_WEIGHTS: dict[str, float] = {
    "cold_six": 15.0,
    "hot_six": 15.0,
    "pair_cooccur": 14.0,
    "last_draw_shift": 13.0,
    "sum_streak": 12.0,
    "odd_even_cold": 11.0,
    "zone_heat": 10.0,
    "spread_wheel": 10.0,
}


@dataclass(frozen=True)
class Draw:
    draw_number: int
    main: tuple[int, ...]
    bonus: int


def rows_to_draws(rows: list[tuple]) -> list[Draw]:
    out: list[Draw] = []
    for r in rows:
        dn = int(r[0])
        numstr = str(r[2] or "").strip()
        if not numstr:
            continue
        parts = tuple(sorted(int(x) for x in numstr.split(",") if x.strip()))
        if len(parts) != 6:
            continue
        bonus = int(r[3])
        out.append(Draw(dn, parts, bonus))
    return sorted(out, key=lambda d: d.draw_number)


def count_mains(draws: list[Draw], window: int) -> dict[int, int]:
    c = {i: 0 for i in range(1, 44)}
    for d in draws[-window:] if window > 0 else draws:
        for x in d.main:
            c[x] = c.get(x, 0) + 1
    return c


def count_bonus(draws: list[Draw], window: int) -> dict[int, int]:
    c = {i: 0 for i in range(1, 44)}
    for d in draws[-window:] if window > 0 else draws:
        c[d.bonus] = c.get(d.bonus, 0) + 1
    return c


def pair_cooccurrence_counts(draws: list[Draw], window: int) -> dict[tuple[int, int], int]:
    pc: dict[tuple[int, int], int] = defaultdict(int)
    for d in draws[-window:] if window > 0 else draws:
        m = sorted(d.main)
        for i in range(len(m)):
            for j in range(i + 1, len(m)):
                pc[(m[i], m[j])] += 1
    return pc


def mean_main_sum(draws: list[Draw], window: int) -> float:
    slice_ = draws[-window:] if window > 0 else draws
    if not slice_:
        return 129.0
    return sum(sum(d.main) for d in slice_) / len(slice_)


def cold_order(counts: dict[int, int]) -> list[int]:
    return sorted(range(1, 44), key=lambda x: (counts[x], x))


def hot_order(counts: dict[int, int]) -> list[int]:
    return sorted(range(1, 44), key=lambda x: (-counts[x], x))


def pick_bonus(main: set[int], bonus_freq: dict[int, int]) -> int:
    candidates = [b for b in range(1, 44) if b not in main]
    if not candidates:
        return 1
    return min(candidates, key=lambda b: (bonus_freq.get(b, 0), b))


def slice_six(order: list[int], start: int) -> tuple[int, ...]:
    out: list[int] = []
    for k in range(6):
        out.append(order[(start + k) % 43])
    return tuple(sorted(out))


def build_method_predictions(
    order: list[int],
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    tops: list[dict] = []
    for i in range(max_rank):
        main = slice_six(order, i)
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def greedy_cooccur_main(
    seed: int,
    pair_counts: dict[tuple[int, int], int],
) -> tuple[int, ...]:
    selected: set[int] = {seed}
    while len(selected) < 6:
        best_c: int | None = None
        best_s = -1
        for c in range(1, 44):
            if c in selected:
                continue
            s = 0
            for x in selected:
                a, b = (c, x) if c < x else (x, c)
                s += pair_counts.get((a, b), 0)
            if s > best_s or (s == best_s and (best_c is None or c < best_c)):
                best_s = s
                best_c = c
        if best_c is None:
            break
        selected.add(best_c)
    return tuple(sorted(selected))


def build_pair_cooccur_predictions(
    cold: list[int],
    pair_counts: dict[tuple[int, int], int],
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    tops: list[dict] = []
    for i in range(max_rank):
        seed = cold[i % 43]
        main = greedy_cooccur_main(seed, pair_counts)
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def build_last_draw_shift_predictions(
    last: Draw | None,
    cold: list[int],
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    tops: list[dict] = []
    if last is None:
        return build_method_predictions(cold, bonus_freq, score_base=score_base, score_step=score_step, max_rank=max_rank)

    last_sorted = tuple(sorted(last.main))
    for i in range(max_rank):
        base = list(last_sorted)
        j = i % 6
        for step in range(43):
            cand = cold[(i + step) % 43]
            others = {base[k] for k in range(6) if k != j}
            if cand not in others:
                base[j] = cand
                break
        main = tuple(sorted(base))
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def build_sum_streak_predictions(
    history: list[Draw],
    bonus_freq: dict[int, int],
    window: int,
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    mean_s = mean_main_sum(history, window)
    best_a = 1
    best_d = 10**9
    for a in range(1, 39):
        ts = 6 * a + 15
        d = abs(ts - mean_s)
        if d < best_d or (d == best_d and a < best_a):
            best_d = d
            best_a = a
    tops: list[dict] = []
    for i in range(max_rank):
        a = 1 + (best_a - 1 + i) % 38
        main = tuple(range(a, a + 6))
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def build_odd_even_cold_predictions(
    cold: list[int],
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    odds = [x for x in cold if x % 2 == 1]
    evens = [x for x in cold if x % 2 == 0]
    if len(odds) < 3:
        odds = [x for x in range(1, 44, 2)]
    if len(evens) < 3:
        evens = [x for x in range(2, 44, 2)]
    tops: list[dict] = []
    for i in range(max_rank):
        pool: list[int] = []
        for j in range(3):
            pool.append(odds[(i + j) % len(odds)])
        for j in range(3):
            pool.append(evens[(i + j) % len(evens)])
        pool = list(dict.fromkeys(pool))
        for x in cold:
            if len(pool) >= 6:
                break
            if x not in pool:
                pool.append(x)
        for x in range(1, 44):
            if len(pool) >= 6:
                break
            if x not in pool:
                pool.append(x)
        main = tuple(sorted(pool[:6]))
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def build_zone_heat_predictions(
    counts: dict[int, int],
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    z1 = sorted(range(1, 15), key=lambda x: (-counts[x], x))
    z2 = sorted(range(15, 30), key=lambda x: (-counts[x], x))
    z3 = sorted(range(30, 44), key=lambda x: (-counts[x], x))
    tops: list[dict] = []
    for i in range(max_rank):
        pool = [
            z1[i % len(z1)],
            z1[(i + 1) % len(z1)],
            z2[i % len(z2)],
            z2[(i + 1) % len(z2)],
            z3[i % len(z3)],
            z3[(i + 1) % len(z3)],
        ]
        pool = list(dict.fromkeys(pool))
        for z in (z1, z2, z3):
            for x in z:
                if len(pool) >= 6:
                    break
                if x not in pool:
                    pool.append(x)
        for x in range(1, 44):
            if len(pool) >= 6:
                break
            if x not in pool:
                pool.append(x)
        main = tuple(sorted(pool[:6]))
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def build_spread_wheel_predictions(
    bonus_freq: dict[int, int],
    *,
    score_base: float,
    score_step: float,
    max_rank: int = 24,
) -> list[dict]:
    tops: list[dict] = []
    step = 7
    for i in range(max_rank):
        start = 1 + (i % 43)
        s: list[int] = []
        x = start
        guard = 0
        while len(s) < 6 and guard < 100:
            guard += 1
            if 1 <= x <= 43 and x not in s:
                s.append(x)
            x = ((x - 1 + step) % 43) + 1
        while len(s) < 6:
            for t in range(1, 44):
                if t not in s:
                    s.append(t)
                    if len(s) >= 6:
                        break
        main = tuple(sorted(s[:6]))
        ms = set(main)
        bonus = pick_bonus(ms, bonus_freq)
        tops.append(
            {
                "rank": i + 1,
                "main": list(main),
                "bonus": bonus,
                "score": round(score_base - i * score_step, 2),
            }
        )
    return tops


def merge_ensemble_mains(rank_idx: int, all_mains: list[list[int]]) -> tuple[int, ...]:
    pool: list[int] = []
    for depth in range(6):
        for mi, ml in enumerate(all_mains):
            if len(pool) >= 6:
                return tuple(sorted(pool))
            if len(ml) != 6:
                continue
            pos = (depth + rank_idx + mi) % 6
            x = ml[pos]
            if x not in pool:
                pool.append(x)
    for x in range(1, 44):
        if len(pool) >= 6:
            break
        if x not in pool:
            pool.append(x)
    return tuple(sorted(pool[:6]))


def jst_now_iso() -> tuple[str, str]:
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.isoformat(), now.strftime("%H:%M")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--target-draw", type=int, default=None, help="予測対象回（省略時は CSV 最新+1）")
    p.add_argument("--window", type=int, default=96, help="頻度集計に使う過去回数")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "predictions" / "daily",
        help="ensemble の出力先ディレクトリ",
    )
    args = p.parse_args()

    rows = load_all_csv_files()
    draws = rows_to_draws(rows)
    if not draws:
        print("❌ loto6 CSV から有効な抽選行が読めませんでした")
        sys.exit(1)

    last_draw = draws[-1].draw_number
    target = args.target_draw if args.target_draw is not None else last_draw + 1
    if target <= last_draw:
        print(
            f"⚠️ 対象回 {target} は最終取込回 {last_draw} 以下です。次回以降の回号を指定してください。"
        )

    history = [d for d in draws if d.draw_number < target]
    if len(history) < 10:
        print(f"❌ 対象回 {target} より前の履歴が少なすぎます（{len(history)} 回）")
        sys.exit(1)

    counts = count_mains(history, args.window)
    bonus_freq = count_bonus(history, args.window)
    pair_counts = pair_cooccurrence_counts(history, args.window)
    cold = cold_order(counts)
    hot = hot_order(counts)
    last_completed = history[-1] if history else None

    cold_preds = build_method_predictions(cold, bonus_freq, score_base=100.0, score_step=0.5)
    hot_preds = build_method_predictions(hot, bonus_freq, score_base=100.0, score_step=0.5)
    pair_preds = build_pair_cooccur_predictions(
        cold, pair_counts, bonus_freq, score_base=99.0, score_step=0.5
    )
    nudge_preds = build_last_draw_shift_predictions(
        last_completed, cold, bonus_freq, score_base=98.0, score_step=0.5
    )
    sum_preds = build_sum_streak_predictions(
        history, bonus_freq, args.window, score_base=97.0, score_step=0.5
    )
    odd_preds = build_odd_even_cold_predictions(
        cold, bonus_freq, score_base=96.0, score_step=0.5
    )
    zone_preds = build_zone_heat_predictions(
        counts, bonus_freq, score_base=95.0, score_step=0.5
    )
    spread_preds = build_spread_wheel_predictions(
        bonus_freq, score_base=94.0, score_step=0.5
    )

    all_pred_lists = [
        cold_preds,
        hot_preds,
        pair_preds,
        nudge_preds,
        sum_preds,
        odd_preds,
        zone_preds,
        spread_preds,
    ]

    time_iso, time_jst = jst_now_iso()
    date_compact = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d")

    def method_payload(method_slug: str, tops: list[dict]) -> dict:
        return {
            "draw_number": target,
            "target_draw_number": target,
            "date": date_compact,
            "method": method_slug,
            "predictions": [
                {
                    "time": time_iso,
                    "time_jst": time_jst,
                    "method": method_slug,
                    "top_predictions": tops,
                }
            ],
        }

    method_specs: list[tuple[str, list[dict]]] = [
        ("cold_six", cold_preds),
        ("hot_six", hot_preds),
        ("pair_cooccur", pair_preds),
        ("last_draw_shift", nudge_preds),
        ("sum_streak", sum_preds),
        ("odd_even_cold", odd_preds),
        ("zone_heat", zone_preds),
        ("spread_wheel", spread_preds),
    ]

    ens_tops: list[dict] = []
    for i in range(24):
        mains_at_rank = [p[i]["main"] for p in all_pred_lists]
        merged = merge_ensemble_mains(i, mains_at_rank)
        ms = set(merged)
        ens_tops.append(
            {
                "rank": i + 1,
                "main": list(merged),
                "bonus": pick_bonus(ms, bonus_freq),
                "score": round(100.0 - i * 0.38, 2),
            }
        )

    ensemble_payload = {
        "draw_number": target,
        "target_draw_number": target,
        "date": date_compact,
        "predictions": [
            {
                "time": time_iso,
                "time_jst": time_jst,
                "ensemble_weights": dict(ENSEMBLE_WEIGHTS),
                "top_predictions": ens_tops,
            }
        ],
        "last_updated": time_iso,
    }

    out_dir: Path = args.out_dir
    write_json(out_dir / f"loto6_{target}.json", ensemble_payload)
    for slug, tops in method_specs:
        write_json(out_dir / "methods" / slug / f"loto6_{target}.json", method_payload(slug, tops))

    print(f"✅ 第 {target} 回向け MVP 予測（8手法 + ensemble）を書き出しました:")
    print(f"   {out_dir / f'loto6_{target}.json'}")
    for slug, _ in method_specs:
        print(f"   {out_dir / 'methods' / slug / f'loto6_{target}.json'}")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()

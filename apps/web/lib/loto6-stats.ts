import type { Loto6DrawRow } from "@/lib/loto6";

/** 統計用に draw の一部列だけあれば足りる */
export type Loto6DrawRowLite = Pick<
  Loto6DrawRow,
  "draw_number" | "draw_date" | "numbers" | "bonus_number"
>;

export type Loto6BallStat = {
  ball: number;
  mainCount: number;
  bonusCount: number;
};

/** 本数字・ボーナスの出現回数（直近 window 回、または全件） */
export function computeLoto6BallStats(
  rows: readonly Loto6DrawRowLite[],
  window: number | null,
): Loto6BallStat[] {
  const slice =
    window != null && window > 0
      ? rows.slice(-window)
      : [...rows];

  const mainC = new Map<number, number>();
  const bonusC = new Map<number, number>();
  for (let b = 1; b <= 43; b += 1) {
    mainC.set(b, 0);
    bonusC.set(b, 0);
  }

  for (const r of slice) {
    const parts = String(r.numbers ?? "")
      .split(",")
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => Number.isFinite(n) && n >= 1 && n <= 43);
    for (const n of parts) {
      mainC.set(n, (mainC.get(n) ?? 0) + 1);
    }
    const bn = r.bonus_number;
    if (typeof bn === "number" && bn >= 1 && bn <= 43) {
      bonusC.set(bn, (bonusC.get(bn) ?? 0) + 1);
    }
  }

  return Array.from({ length: 43 }, (_, i) => {
    const ball = i + 1;
    return {
      ball,
      mainCount: mainC.get(ball) ?? 0,
      bonusCount: bonusC.get(ball) ?? 0,
    };
  });
}

export function maxMainCount(stats: readonly Loto6BallStat[]): number {
  return stats.reduce((m, s) => Math.max(m, s.mainCount), 0);
}

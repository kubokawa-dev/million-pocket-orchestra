import type { MethodPredictionRow } from "./types";

export type ConsensusEntry = {
  number: string;
  supportCount: number;
  methods: string[];
  bestScore: number | null;
};

/** 各手法の上位いくつかから「複数モデルで出た番号」を集計 */
export function buildMethodConsensus(
  methodRows: MethodPredictionRow[],
  topKPerMethod: number,
): ConsensusEntry[] {
  const acc = new Map<
    string,
    { methods: Set<string>; bestScore: number | null }
  >();

  for (const m of methodRows) {
    const slice = m.topPredictions.slice(0, topKPerMethod);
    for (const p of slice) {
      const num = p.number?.trim();
      if (!num || num.length !== 4) continue;
      const cur = acc.get(num) ?? {
        methods: new Set<string>(),
        bestScore: null as number | null,
      };
      cur.methods.add(m.slug);
      if (p.score != null && Number.isFinite(p.score)) {
        cur.bestScore =
          cur.bestScore == null
            ? p.score
            : Math.max(cur.bestScore, p.score);
      }
      acc.set(num, cur);
    }
  }

  return [...acc.entries()]
    .filter(([, v]) => v.methods.size >= 2)
    .map(([number, v]) => ({
      number,
      supportCount: v.methods.size,
      methods: [...v.methods].sort((a, b) => a.localeCompare(b)),
      bestScore: v.bestScore,
    }))
    .sort(
      (a, b) =>
        b.supportCount - a.supportCount ||
        (b.bestScore ?? -1) - (a.bestScore ?? -1),
    );
}

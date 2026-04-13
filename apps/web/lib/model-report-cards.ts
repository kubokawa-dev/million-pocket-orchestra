import {
  computeBoxRankStats,
  METHOD_SLUGS_FOR_STATS,
} from "@/lib/numbers4-predictions/box-rank-stats";
import { formatEnsembleWeightKey } from "@/lib/numbers4-predictions/ensemble-weight-labels";
import { buildWinningModelHitsForDrawListNumbers3, fetchOfficialWinningDrawsBeforeTargetNumbers3, resolveNumbers3TargetDrawNumber } from "@/lib/numbers3-predictions/load-numbers3";

export type ModelReportCard = {
  slug: string;
  label: string;
  sampleSize: number;
  hitsAny: number;
  hitRatePct: number;
  top10Pct?: number;
  exactHits?: number;
  boxHits?: number;
};

export async function buildNumbers4ModelReportCards(
  lastN = 30,
  options?: { limit?: number },
): Promise<ModelReportCard[]> {
  const stats = await computeBoxRankStats({
    lastN,
    topK: 20,
    thresholds: [10, 20],
  });

  return stats.aggregates
    .filter((row) => row.key !== "ensemble")
    .map((row) => ({
      slug: row.key,
      label: row.label,
      sampleSize: row.n,
      hitsAny: row.hitsAny,
      hitRatePct: Number((row.n > 0 ? (row.hitsAny / row.n) * 100 : 0).toFixed(1)),
      top10Pct: Number((row.atOrBelow[10]?.pct ?? 0).toFixed(1)),
    }))
    .sort((a, b) => {
      const top10Diff = (b.top10Pct ?? 0) - (a.top10Pct ?? 0);
      if (top10Diff !== 0) return top10Diff;
      const hitDiff = b.hitRatePct - a.hitRatePct;
      if (hitDiff !== 0) return hitDiff;
      return a.slug.localeCompare(b.slug);
    })
    .slice(0, options?.limit ?? 6);
}

export async function buildNumbers3ModelReportCards(
  lastN = 20,
  options?: { limit?: number },
): Promise<ModelReportCard[]> {
  const targetDrawNumber = await resolveNumbers3TargetDrawNumber();
  const draws = await fetchOfficialWinningDrawsBeforeTargetNumbers3(targetDrawNumber, lastN);
  if (draws.length === 0) return [];

  const hits = await buildWinningModelHitsForDrawListNumbers3(draws);
  const counts = new Map<string, { exact: number; box: number }>();

  for (const slug of METHOD_SLUGS_FOR_STATS) {
    counts.set(slug, { exact: 0, box: 0 });
  }

  for (const row of hits) {
    for (const slug of row.exact_slugs) {
      const current = counts.get(slug) ?? { exact: 0, box: 0 };
      current.exact += 1;
      counts.set(slug, current);
    }
    for (const slug of row.box_only_slugs) {
      const current = counts.get(slug) ?? { exact: 0, box: 0 };
      current.box += 1;
      counts.set(slug, current);
    }
  }

  return [...counts.entries()]
    .map(([slug, value]) => {
      const hitsAny = value.exact + value.box;
      return {
        slug,
        label: formatEnsembleWeightKey(slug),
        sampleSize: draws.length,
        hitsAny,
        hitRatePct: Number(((hitsAny / draws.length) * 100).toFixed(1)),
        exactHits: value.exact,
        boxHits: value.box,
      };
    })
    .sort((a, b) => {
      const hitDiff = b.hitRatePct - a.hitRatePct;
      if (hitDiff !== 0) return hitDiff;
      const exactDiff = (b.exactHits ?? 0) - (a.exactHits ?? 0);
      if (exactDiff !== 0) return exactDiff;
      return a.slug.localeCompare(b.slug);
    })
    .slice(0, options?.limit ?? 6);
}

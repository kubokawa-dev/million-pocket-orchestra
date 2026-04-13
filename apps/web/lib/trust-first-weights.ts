import type { ModelGovernanceSummary } from "@/lib/model-governance";

type WeightEntry = [string, number];
type HotModelEntry = { model: string; score: number };

export type TrustAdjustedWeight = {
  slug: string;
  rawWeight: number;
  adjustedWeight: number;
  multiplier: number;
  bucket: "preferred" | "watch" | "deprioritized" | "unknown";
};

function buildBucketMap(summary: ModelGovernanceSummary): Map<string, TrustAdjustedWeight["bucket"]> {
  const map = new Map<string, TrustAdjustedWeight["bucket"]>();
  for (const item of summary.preferred) map.set(item.slug, "preferred");
  for (const item of summary.watchlist) map.set(item.slug, "watch");
  for (const item of summary.deprioritized) map.set(item.slug, "deprioritized");
  return map;
}

function multiplierForBucket(
  bucket: TrustAdjustedWeight["bucket"],
): number {
  if (bucket === "preferred") return 1;
  if (bucket === "watch") return 0.85;
  if (bucket === "deprioritized") return 0.55;
  return 0.75;
}

export function buildTrustAdjustedWeights(
  rawWeights: WeightEntry[],
  summary: ModelGovernanceSummary,
): TrustAdjustedWeight[] {
  const bucketMap = buildBucketMap(summary);

  return rawWeights
    .map(([slug, rawWeight]) => {
      const bucket = bucketMap.get(slug) ?? "unknown";
      const multiplier = multiplierForBucket(bucket);
      return {
        slug,
        rawWeight,
        adjustedWeight: Number((rawWeight * multiplier).toFixed(2)),
        multiplier,
        bucket,
      };
    })
    .sort((a, b) => b.adjustedWeight - a.adjustedWeight || a.slug.localeCompare(b.slug));
}

export function buildTrustAdjustedHotModels(
  rawHotModels: HotModelEntry[],
  summary: ModelGovernanceSummary,
): Array<HotModelEntry & Pick<TrustAdjustedWeight, "bucket" | "multiplier">> {
  const bucketMap = buildBucketMap(summary);

  return rawHotModels
    .map((item) => {
      const bucket = bucketMap.get(item.model) ?? "unknown";
      const multiplier = multiplierForBucket(bucket);
      return {
        ...item,
        score: Number((item.score * multiplier).toFixed(2)),
        bucket,
        multiplier,
      };
    })
    .sort((a, b) => b.score - a.score || a.model.localeCompare(b.model));
}

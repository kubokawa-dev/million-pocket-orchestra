/**
 * 複数回にわたる「ボックス一致の順位」集計（UI / サーバー用）。
 * evaluate_methods.py の ALL_METHODS と同じ並び。
 */

import { formatEnsembleWeightKey } from "./ensemble-weight-labels";
import {
  fetchNumbers4DrawResult,
  fetchRecentNumbers4DrawNumbersWithResults,
  getLatestEnsembleRun,
  loadNumbers4PredictionBundleForDraw,
} from "./load-6949";
import { digitsSortedKey, normalizeNumbers4 } from "./prediction-hit-utils";
import type { EnsemblePayload } from "./types";

/** numbers4/evaluate_methods.py の ALL_METHODS と揃える */
export const METHOD_SLUGS_FOR_STATS = [
  "box_model",
  "ml_neighborhood",
  "even_odd_pattern",
  "low_sum_specialist",
  "sequential_pattern",
  "cold_revival",
  "hot_pair",
  "box_pattern",
  "digit_freq_box",
  "global_frequency",
  "lightgbm",
  "state_chain",
  "adjacent_digit",
  "lgbm_box",
] as const;

export type MethodSlugForStats = (typeof METHOD_SLUGS_FOR_STATS)[number];

export const DEFAULT_BOX_RANK_THRESHOLDS = [1, 5, 10, 20, 50, 100] as const;

export type BoxRankSourceKey = "ensemble" | MethodSlugForStats;

export type PerDrawBoxRankRow = {
  drawNumber: number;
  winning: string | null;
  ranks: Record<BoxRankSourceKey, number | null>;
};

export type BoxRankAggregateRow = {
  key: BoxRankSourceKey;
  label: string;
  n: number;
  outOfRange: number;
  /** rank が null でない件数 */
  hitsAny: number;
  atOrBelow: Record<number, { count: number; pct: number }>;
};

export type BoxRankStatsResult = {
  lastN: number;
  topK: number;
  thresholds: number[];
  draws: number[];
  perDraw: PerDrawBoxRankRow[];
  aggregates: BoxRankAggregateRow[];
  hadSupabaseDraws: boolean;
};

/**
 * 先頭から topK 件のなかで、当選とボックス一致する最初の順位（1 始まり）。無ければ null。
 */
export function findBoxHitRank(
  orderedPredictions: string[],
  winningRaw: string,
  topK: number,
): number | null {
  const w = normalizeNumbers4(winningRaw);
  if (!w) return null;
  const wKey = digitsSortedKey(w);
  if (!wKey) return null;
  const cap = Math.min(topK, orderedPredictions.length);
  for (let i = 0; i < cap; i++) {
    const p = normalizeNumbers4(orderedPredictions[i]);
    if (!p || p.length !== 4) continue;
    if (digitsSortedKey(p) === wKey) return i + 1;
  }
  return null;
}

function orderedEnsembleNumbers(ensemble: EnsemblePayload | null): string[] {
  const run = getLatestEnsembleRun(ensemble);
  const tops = run?.top_predictions ?? [];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const t of tops) {
    const n = normalizeNumbers4(
      t.number != null ? String(t.number) : "",
    );
    if (!n || n.length !== 4 || seen.has(n)) continue;
    seen.add(n);
    out.push(n);
  }
  return out;
}

function labelForSource(key: BoxRankSourceKey): string {
  if (key === "ensemble") {
    return "アンサンブル（ensemble）";
  }
  return formatEnsembleWeightKey(key);
}

function summarizeRanks(
  rows: PerDrawBoxRankRow[],
  key: BoxRankSourceKey,
  thresholds: number[],
): BoxRankAggregateRow {
  const n = rows.length;
  const ranks = rows.map((r) => r.ranks[key]);
  const outOfRange = ranks.filter((x) => x == null).length;
  const hitsAny = n - outOfRange;
  const atOrBelow: Record<number, { count: number; pct: number }> = {};
  for (const t of thresholds) {
    const count = ranks.filter((x) => x != null && x <= t).length;
    atOrBelow[t] = {
      count,
      pct: n > 0 ? (100 * count) / n : 0,
    };
  }
  return {
    key,
    label: labelForSource(key),
    n,
    outOfRange,
    hitsAny,
    atOrBelow,
  };
}

export async function computeBoxRankStats(options: {
  lastN: number;
  topK: number;
  thresholds?: readonly number[];
}): Promise<BoxRankStatsResult> {
  const lastN = Math.min(200, Math.max(1, Math.floor(options.lastN)));
  const topK = Math.min(500, Math.max(1, Math.floor(options.topK)));
  const thresholds = (
    options.thresholds?.length
      ? [...options.thresholds]
      : [...DEFAULT_BOX_RANK_THRESHOLDS]
  )
    .map((x) => Math.floor(x))
    .filter((x) => x > 0)
    .sort((a, b) => a - b);

  const draws = await fetchRecentNumbers4DrawNumbersWithResults(lastN);
  const hadSupabaseDraws = draws.length > 0;

  const perDraw: PerDrawBoxRankRow[] = [];

  for (const drawNumber of draws) {
    const result = await fetchNumbers4DrawResult(drawNumber);
    const winning = result?.numbers
      ? (normalizeNumbers4(String(result.numbers)) ?? String(result.numbers))
      : null;

    const bundle = await loadNumbers4PredictionBundleForDraw(drawNumber);

    const ensList = orderedEnsembleNumbers(bundle?.ensemble ?? null);
    const rankEnsemble =
      winning != null
        ? findBoxHitRank(ensList, winning, topK)
        : null;

    const ranks = {} as Record<BoxRankSourceKey, number | null>;
    ranks.ensemble = rankEnsemble;

    for (const slug of METHOD_SLUGS_FOR_STATS) {
      const row = bundle?.methodRows.find((m) => m.slug === slug);
      const preds = row?.topPredictions.map((t) => t.number) ?? [];
      ranks[slug] =
        winning != null ? findBoxHitRank(preds, winning, topK) : null;
    }

    perDraw.push({ drawNumber, winning, ranks });
  }

  const sourceKeys: BoxRankSourceKey[] = [
    "ensemble",
    ...METHOD_SLUGS_FOR_STATS,
  ];
  const aggregates = sourceKeys.map((key) =>
    summarizeRanks(perDraw, key, thresholds),
  );

  return {
    lastN,
    topK,
    thresholds,
    draws,
    perDraw,
    aggregates,
    hadSupabaseDraws,
  };
}

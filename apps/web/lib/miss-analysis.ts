import {
  computeBoxRankStats,
  findBoxHitRank,
} from "@/lib/numbers4-predictions/box-rank-stats";
import {
  fetchOfficialWinningDrawsBeforeTarget,
  getLatestEnsembleRun as getLatestEnsembleRunNumbers4,
  loadNumbers4PredictionBundleForDraw,
  resolveTargetDrawNumber,
} from "@/lib/numbers4-predictions/load-6949";
import { classifyHit as classifyNumbers4Hit, normalizeNumbers4 } from "@/lib/numbers4-predictions/prediction-hit-utils";
import {
  fetchOfficialWinningDrawsBeforeTargetNumbers3,
  getLatestEnsembleRun as getLatestEnsembleRunNumbers3,
  loadNumbers3PredictionBundleForDraw,
  resolveNumbers3TargetDrawNumber,
} from "@/lib/numbers3-predictions/load-numbers3";
import { classifyHit as classifyNumbers3Hit, normalizeNumbers3 } from "@/lib/numbers3-predictions/prediction-hit-utils";

export type MissAnalysisSummary = {
  sampleSize: number;
  top10BoxRatePct: number;
  top20BoxRatePct: number;
  exactTop20RatePct: number;
  oneDigitOffTop1RatePct: number;
  averageFirstBoxRank: number | null;
};

function percentage(count: number, total: number): number {
  return Number((total > 0 ? (count / total) * 100 : 0).toFixed(1));
}

function average(values: number[]): number | null {
  if (values.length === 0) return null;
  return Number(
    (values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(1),
  );
}

function countSharedDigits(a: string, b: string): number {
  const counts = new Map<string, number>();
  for (const char of b) {
    counts.set(char, (counts.get(char) ?? 0) + 1);
  }

  let shared = 0;
  for (const char of a) {
    const remaining = counts.get(char) ?? 0;
    if (remaining > 0) {
      shared += 1;
      counts.set(char, remaining - 1);
    }
  }
  return shared;
}

export async function buildNumbers4MissAnalysis(
  lastN = 30,
): Promise<MissAnalysisSummary> {
  const targetDrawNumber = await resolveTargetDrawNumber();
  const draws = await fetchOfficialWinningDrawsBeforeTarget(targetDrawNumber, lastN);
  if (draws.length === 0) {
    return {
      sampleSize: 0,
      top10BoxRatePct: 0,
      top20BoxRatePct: 0,
      exactTop20RatePct: 0,
      oneDigitOffTop1RatePct: 0,
      averageFirstBoxRank: null,
    };
  }

  const boxStats = await computeBoxRankStats({ lastN: draws.length, topK: 20, thresholds: [10, 20] });
  const ensembleAggregate = boxStats.aggregates.find((row) => row.key === "ensemble");
  const top10BoxRatePct = Number((ensembleAggregate?.atOrBelow[10]?.pct ?? 0).toFixed(1));
  const top20BoxRatePct = Number((ensembleAggregate?.atOrBelow[20]?.pct ?? 0).toFixed(1));
  const boxRanks = boxStats.perDraw
    .map((row) => row.ranks.ensemble)
    .filter((rank): rank is number => rank != null);

  let exactTop20 = 0;
  let oneDigitOffTop1 = 0;

  for (const draw of draws) {
    const winning = normalizeNumbers4(draw.numbers);
    if (!winning) continue;
    const bundle = await loadNumbers4PredictionBundleForDraw(draw.draw_number);
    const run = getLatestEnsembleRunNumbers4(bundle?.ensemble ?? null);
    const predictions = (run?.top_predictions ?? [])
      .map((item) => normalizeNumbers4(item.number != null ? String(item.number) : ""))
      .filter((value): value is string => value != null);

    if (predictions.slice(0, 20).some((prediction) => classifyNumbers4Hit(prediction, winning) === "straight")) {
      exactTop20 += 1;
    }

    const top1 = predictions[0];
    if (top1 && classifyNumbers4Hit(top1, winning) === "none" && countSharedDigits(top1, winning) >= 3) {
      oneDigitOffTop1 += 1;
    }
  }

  return {
    sampleSize: draws.length,
    top10BoxRatePct,
    top20BoxRatePct,
    exactTop20RatePct: percentage(exactTop20, draws.length),
    oneDigitOffTop1RatePct: percentage(oneDigitOffTop1, draws.length),
    averageFirstBoxRank: average(boxRanks),
  };
}

export async function buildNumbers3MissAnalysis(
  lastN = 20,
): Promise<MissAnalysisSummary> {
  const targetDrawNumber = await resolveNumbers3TargetDrawNumber();
  const draws = await fetchOfficialWinningDrawsBeforeTargetNumbers3(targetDrawNumber, lastN);
  if (draws.length === 0) {
    return {
      sampleSize: 0,
      top10BoxRatePct: 0,
      top20BoxRatePct: 0,
      exactTop20RatePct: 0,
      oneDigitOffTop1RatePct: 0,
      averageFirstBoxRank: null,
    };
  }

  let top10Box = 0;
  let top20Box = 0;
  let exactTop20 = 0;
  let oneDigitOffTop1 = 0;
  const boxRanks: number[] = [];

  for (const draw of draws) {
    const winning = normalizeNumbers3(draw.numbers);
    if (!winning) continue;
    const bundle = await loadNumbers3PredictionBundleForDraw(draw.draw_number);
    const run = getLatestEnsembleRunNumbers3(bundle?.ensemble ?? null);
    const predictions = (run?.top_predictions ?? [])
      .map((item) => normalizeNumbers3(item.number != null ? String(item.number) : ""))
      .filter((value): value is string => value != null);

    const boxRank = findBoxHitRank(predictions, winning, 20);
    if (boxRank != null) {
      boxRanks.push(boxRank);
      top20Box += 1;
      if (boxRank <= 10) top10Box += 1;
    }

    if (predictions.slice(0, 20).some((prediction) => classifyNumbers3Hit(prediction, winning) === "straight")) {
      exactTop20 += 1;
    }

    const top1 = predictions[0];
    if (top1 && classifyNumbers3Hit(top1, winning) === "none" && countSharedDigits(top1, winning) >= 2) {
      oneDigitOffTop1 += 1;
    }
  }

  return {
    sampleSize: draws.length,
    top10BoxRatePct: percentage(top10Box, draws.length),
    top20BoxRatePct: percentage(top20Box, draws.length),
    exactTop20RatePct: percentage(exactTop20, draws.length),
    oneDigitOffTop1RatePct: percentage(oneDigitOffTop1, draws.length),
    averageFirstBoxRank: average(boxRanks),
  };
}

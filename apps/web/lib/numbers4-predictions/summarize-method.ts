import type { MethodSummaryRow } from "./types";

export function summarizeMethodPayload(payload: unknown): Omit<
  MethodSummaryRow,
  "slug"
> {
  if (!payload || typeof payload !== "object") {
    return { runs: 0, topNumber: null, lastTimeJst: null };
  }
  const p = payload as {
    predictions?: {
      time_jst?: string;
      top_predictions?: { number?: string }[];
    }[];
    prediction_count?: number;
  };
  const preds = p.predictions ?? [];
  const last = preds[preds.length - 1];
  const top = last?.top_predictions?.[0]?.number ?? null;
  return {
    runs: p.prediction_count ?? preds.length,
    topNumber: top,
    lastTimeJst: last?.time_jst ?? null,
  };
}

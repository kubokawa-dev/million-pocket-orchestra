import { normalizeNumbers4 } from "./prediction-hit-utils";
import type { MethodPredictionRow } from "./types";

type MethodPayloadSummary = Omit<MethodPredictionRow, "slug" | "relativePath">;

export function summarizeMethodPayload(payload: unknown): MethodPayloadSummary {
  if (!payload || typeof payload !== "object") {
    return {
      runs: 0,
      topNumber: null,
      lastTimeJst: null,
      topPredictions: [],
    };
  }
  const p = payload as {
    predictions?: {
      time_jst?: string;
      top_predictions?: { rank?: number; number?: string; score?: number }[];
    }[];
    prediction_count?: number;
  };
  const preds = p.predictions ?? [];
  const last = preds[preds.length - 1];
  const tops = last?.top_predictions ?? [];
  /** モデル別表示はカード内でさらにスライス。寄与モデル照合のため多めに保持 */
  const topPredictions = tops.slice(0, 96).map((row, i) => {
    const raw = row.number;
    const n =
      typeof raw === "string" || typeof raw === "number"
        ? normalizeNumbers4(String(raw))
        : null;
    return {
      rank: row.rank ?? i + 1,
      number: n ?? "",
      score:
        typeof row.score === "number" && Number.isFinite(row.score)
          ? row.score
          : null,
    };
  });

  const filtered = topPredictions.filter((x) => x.number.length === 4);
  const topNumber = filtered[0]?.number ?? null;

  return {
    runs: p.prediction_count ?? preds.length,
    topNumber,
    lastTimeJst: last?.time_jst ?? null,
    topPredictions: filtered,
  };
}

import { cache } from "react";

import { createStaticClient } from "@/lib/supabase/static";

import type {
  Loto6EnsemblePayload,
  Loto6EnsembleRun,
  Loto6MethodPayload,
  Loto6MethodRun,
  Loto6MethodRow,
  Loto6PredictionBundle,
} from "./types";

type DbDocRow = {
  doc_kind: string;
  method_slug: string | null;
  payload: unknown;
  relative_path: string | null;
};

function normalizeMethodRows(rows: Loto6MethodRow[]): Loto6MethodRow[] {
  return [...rows].sort((a, b) => a.slug.localeCompare(b.slug));
}

/**
 * 指定回を予測対象とした JSON バンドル（ensemble + method）を Supabase から読む。
 */
export const loadLoto6PredictionBundle = cache(
  async (targetDrawNumber: number): Promise<Loto6PredictionBundle | null> => {
    if (!Number.isFinite(targetDrawNumber) || targetDrawNumber < 1) return null;

    const supabase = createStaticClient();
    const { data: rows, error } = await supabase
      .from("loto6_daily_prediction_documents")
      .select("doc_kind, method_slug, payload, relative_path")
      .eq("target_draw_number", targetDrawNumber);

    if (error || !rows?.length) return null;

    let ensemble: Loto6EnsemblePayload | null = null;
    const methodRows: Loto6MethodRow[] = [];

    for (const row of rows as DbDocRow[]) {
      if (row.doc_kind === "ensemble") {
        ensemble = row.payload as Loto6EnsemblePayload;
      } else if (row.doc_kind === "method" && row.method_slug) {
        methodRows.push({
          slug: row.method_slug,
          relativePath: row.relative_path,
          payload: row.payload as Loto6MethodPayload,
        });
      }
    }

    return {
      targetDrawNumber,
      ensemble,
      methodRows: normalizeMethodRows(methodRows),
    };
  },
);

/** DB 上の最新取込回の「次の回号」（予測の表示ターゲット） */
export async function resolveNextLoto6TargetDrawNumber(): Promise<number | null> {
  const supabase = createStaticClient();
  const { data, error } = await supabase
    .from("loto6_draws")
    .select("draw_number")
    .order("draw_number", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error || data?.draw_number == null) return null;
  const n = data.draw_number;
  return typeof n === "number" && n > 0 ? n + 1 : null;
}

export function lastLoto6PredictionRun(
  payload: Loto6MethodPayload | Loto6EnsemblePayload,
): Loto6MethodRun | Loto6EnsembleRun | null {
  const preds = payload.predictions;
  if (!preds?.length) return null;
  return preds[preds.length - 1] ?? null;
}

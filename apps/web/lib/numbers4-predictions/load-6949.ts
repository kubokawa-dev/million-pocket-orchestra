import { promises as fs } from "node:fs";
import path from "node:path";

import { createClient } from "@/lib/supabase/server";

import {
  FALLBACK_BUDGET_6949,
  FALLBACK_ENSEMBLE_6949,
  FALLBACK_METHOD_ROWS,
} from "./fallback-6949";
import { summarizeMethodPayload } from "./summarize-method";
import type {
  BudgetPlanPayload,
  EnsemblePayload,
  EnsemblePredictionRun,
  MethodSummaryRow,
  PredictionBundle6949,
} from "./types";

async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function scanMethodSummaries6949(
  repoRoot: string,
): Promise<MethodSummaryRow[]> {
  const base = path.join(
    repoRoot,
    "predictions",
    "daily",
    "methods",
  );
  const rows: MethodSummaryRow[] = [];
  try {
    const entries = await fs.readdir(base, { withFileTypes: true });
    for (const ent of entries) {
      if (!ent.isDirectory()) continue;
      const fp = path.join(base, ent.name, "numbers4_6949.json");
      const payload = await readJsonFile<unknown>(fp);
      if (payload === null) continue;
      rows.push({
        slug: ent.name,
        ...summarizeMethodPayload(payload),
      });
    }
  } catch {
    /* methods ディレクトリなし */
  }
  return rows.sort((a, b) => a.slug.localeCompare(b.slug));
}

/**
 * 第6949回向けドキュメントを読み込む。
 * 優先: Supabase → リポジトリの predictions/daily → 内蔵フォールバック
 */
export async function loadNumbers4Predictions6949(): Promise<PredictionBundle6949> {
  const targetDrawNumber = 6949 as const;

  try {
    const supabase = await createClient();
    const { data: rows, error } = await supabase
      .from("numbers4_daily_prediction_documents")
      .select("doc_kind, method_slug, payload")
      .eq("target_draw_number", targetDrawNumber);

    if (!error && rows && rows.length > 0) {
      let ensemble: EnsemblePayload | null = null;
      let budgetPlan: BudgetPlanPayload | null = null;
      const methodRows: MethodSummaryRow[] = [];

      for (const row of rows) {
        if (row.doc_kind === "ensemble") {
          ensemble = row.payload as EnsemblePayload;
        } else if (row.doc_kind === "budget_plan") {
          budgetPlan = row.payload as BudgetPlanPayload;
        } else if (row.doc_kind === "method" && row.method_slug) {
          methodRows.push({
            slug: row.method_slug,
            ...summarizeMethodPayload(row.payload),
          });
        }
      }

      methodRows.sort((a, b) => a.slug.localeCompare(b.slug));

      return {
        source: "database",
        targetDrawNumber,
        ensemble,
        budgetPlan,
        methodRows,
      };
    }
  } catch {
    /* env 未設定など */
  }

  const repoRoot = path.join(process.cwd(), "..", "..");
  const ensemblePath = path.join(
    repoRoot,
    "predictions",
    "daily",
    "numbers4_6949.json",
  );
  const budgetPath = path.join(
    repoRoot,
    "predictions",
    "daily",
    "budget_plan_6949.json",
  );

  const [ensembleFile, budgetFile, methodRows] = await Promise.all([
    readJsonFile<EnsemblePayload>(ensemblePath),
    readJsonFile<BudgetPlanPayload>(budgetPath),
    scanMethodSummaries6949(repoRoot),
  ]);

  if (ensembleFile || budgetFile || methodRows.length > 0) {
    return {
      source: "repository_files",
      targetDrawNumber,
      ensemble: ensembleFile,
      budgetPlan: budgetFile,
      methodRows,
    };
  }

  return {
    source: "embedded",
    targetDrawNumber,
    ensemble: FALLBACK_ENSEMBLE_6949,
    budgetPlan: FALLBACK_BUDGET_6949,
    methodRows: FALLBACK_METHOD_ROWS,
  };
}

export function getLatestEnsembleRun(
  payload: EnsemblePayload | null,
): EnsemblePredictionRun | null {
  const preds = payload?.predictions;
  if (!preds?.length) return null;
  return preds[preds.length - 1] ?? null;
}

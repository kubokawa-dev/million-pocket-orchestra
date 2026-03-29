import { promises as fs } from "node:fs";
import path from "node:path";

import { createClient } from "@/lib/supabase/server";
import type { Numbers4DrawRow } from "@/lib/numbers4";

import {
  FALLBACK_BUDGET_6949,
  FALLBACK_ENSEMBLE_6949,
  FALLBACK_METHOD_ROWS,
  FALLBACK_TARGET_DRAW,
} from "./fallback-6949";
import { summarizeMethodPayload } from "./summarize-method";
import type {
  BudgetPlanPayload,
  EnsemblePayload,
  EnsemblePredictionRun,
  MethodPredictionRow,
  Numbers4PredictionBundle,
} from "./types";

async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function maxDrawFromFilesystem(repoRoot: string): Promise<number | null> {
  const daily = path.join(repoRoot, "predictions", "daily");
  try {
    const names = await fs.readdir(daily);
    let max = -1;
    const re = /^numbers4_(\d+)\.json$/;
    for (const name of names) {
      const m = name.match(re);
      if (m) max = Math.max(max, parseInt(m[1], 10));
    }
    return max >= 0 ? max : null;
  } catch {
    return null;
  }
}

async function maxDrawFromSupabase(): Promise<number | null> {
  try {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from("numbers4_daily_prediction_documents")
      .select("target_draw_number")
      .eq("doc_kind", "ensemble")
      .order("target_draw_number", { ascending: false })
      .limit(1);
    if (error || !data?.length) return null;
    const n = data[0].target_draw_number;
    return typeof n === "number" && n > 0 ? n : null;
  } catch {
    return null;
  }
}

/** DB・リポジトリのいずれかで最新とみなす対象回号 */
export async function resolveTargetDrawNumber(): Promise<number> {
  const repoRoot = path.join(process.cwd(), "..", "..");
  const [fromDb, fromFs] = await Promise.all([
    maxDrawFromSupabase(),
    maxDrawFromFilesystem(repoRoot),
  ]);
  const cands = [fromDb, fromFs].filter(
    (x): x is number => x != null && x > 0,
  );
  if (cands.length === 0) return FALLBACK_TARGET_DRAW;
  return Math.max(...cands);
}

type DbDocRow = {
  doc_kind: string;
  method_slug: string | null;
  payload: unknown;
  relative_path: string | null;
};

async function loadBundleFromDatabase(
  targetDrawNumber: number,
): Promise<
  Pick<
    Numbers4PredictionBundle,
    "ensemble" | "budgetPlan" | "methodRows"
  > | null
> {
  const supabase = await createClient();
  const { data: rows, error } = await supabase
    .from("numbers4_daily_prediction_documents")
    .select("doc_kind, method_slug, payload, relative_path")
    .eq("target_draw_number", targetDrawNumber);

  if (error || !rows?.length) return null;

  let ensemble: EnsemblePayload | null = null;
  let budgetPlan: BudgetPlanPayload | null = null;
  const methodRows: MethodPredictionRow[] = [];

  for (const row of rows as DbDocRow[]) {
    if (row.doc_kind === "ensemble") {
      ensemble = row.payload as EnsemblePayload;
    } else if (row.doc_kind === "budget_plan") {
      budgetPlan = row.payload as BudgetPlanPayload;
    } else if (row.doc_kind === "method" && row.method_slug) {
      methodRows.push({
        slug: row.method_slug,
        relativePath: row.relative_path,
        ...summarizeMethodPayload(row.payload),
      });
    }
  }

  methodRows.sort((a, b) => a.slug.localeCompare(b.slug));
  return { ensemble, budgetPlan, methodRows };
}

async function scanMethodsForDraw(
  repoRoot: string,
  drawNumber: number,
): Promise<MethodPredictionRow[]> {
  const base = path.join(repoRoot, "predictions", "daily", "methods");
  const fname = `numbers4_${drawNumber}.json`;
  const rows: MethodPredictionRow[] = [];
  try {
    const entries = await fs.readdir(base, { withFileTypes: true });
    for (const ent of entries) {
      if (!ent.isDirectory()) continue;
      const fp = path.join(base, ent.name, fname);
      const payload = await readJsonFile<unknown>(fp);
      if (payload === null) continue;
      const rel = path.relative(repoRoot, fp).split(path.sep).join("/");
      rows.push({
        slug: ent.name,
        relativePath: rel,
        ...summarizeMethodPayload(payload),
      });
    }
  } catch {
    /* methods なし */
  }
  return rows.sort((a, b) => a.slug.localeCompare(b.slug));
}

async function loadBundleFromFilesystem(
  repoRoot: string,
  drawNumber: number,
): Promise<Pick<Numbers4PredictionBundle, "ensemble" | "budgetPlan" | "methodRows">> {
  const ensemblePath = path.join(
    repoRoot,
    "predictions",
    "daily",
    `numbers4_${drawNumber}.json`,
  );
  const budgetPath = path.join(
    repoRoot,
    "predictions",
    "daily",
    `budget_plan_${drawNumber}.json`,
  );

  const [ensembleFile, budgetFile, methodRows] = await Promise.all([
    readJsonFile<EnsemblePayload>(ensemblePath),
    readJsonFile<BudgetPlanPayload>(budgetPath),
    scanMethodsForDraw(repoRoot, drawNumber),
  ]);

  return {
    ensemble: ensembleFile,
    budgetPlan: budgetFile,
    methodRows,
  };
}

async function tryLoadBundleForDraw(
  targetDrawNumber: number,
): Promise<Numbers4PredictionBundle | null> {
  try {
    const bundle = await loadBundleFromDatabase(targetDrawNumber);
    if (
      bundle &&
      (bundle.ensemble || bundle.budgetPlan || bundle.methodRows.length > 0)
    ) {
      return {
        source: "database",
        targetDrawNumber,
        ...bundle,
      };
    }
  } catch {
    /* env 未設定など */
  }

  const repoRoot = path.join(process.cwd(), "..", "..");
  const fsBundle = await loadBundleFromFilesystem(repoRoot, targetDrawNumber);
  if (
    fsBundle.ensemble ||
    fsBundle.budgetPlan ||
    fsBundle.methodRows.length > 0
  ) {
    return {
      source: "repository_files",
      targetDrawNumber,
      ...fsBundle,
    };
  }

  return null;
}

/** 指定回の予測 JSON / DB ドキュメント。無ければ null（内蔵デモには落とさない） */
export async function loadNumbers4PredictionBundleForDraw(
  targetDrawNumber: number,
): Promise<Numbers4PredictionBundle | null> {
  if (!Number.isFinite(targetDrawNumber) || targetDrawNumber < 1) return null;
  return tryLoadBundleForDraw(targetDrawNumber);
}

/**
 * 最新（または DB・ファイル上の最大）の対象回向けバンドルを読み込む。
 * 優先: Supabase（同一 target_draw_number）→ リポジトリ JSON → 内蔵フォールバック
 */
export async function loadNumbers4PredictionBundle(): Promise<Numbers4PredictionBundle> {
  const targetDrawNumber = await resolveTargetDrawNumber();
  const got = await tryLoadBundleForDraw(targetDrawNumber);
  if (got) return got;

  return {
    source: "embedded",
    targetDrawNumber: FALLBACK_TARGET_DRAW,
    ensemble: FALLBACK_ENSEMBLE_6949,
    budgetPlan: FALLBACK_BUDGET_6949,
    methodRows: FALLBACK_METHOD_ROWS,
  };
}

/** @deprecated `loadNumbers4PredictionBundle` を使用 */
export const loadNumbers4Predictions6949 = loadNumbers4PredictionBundle;

export async function fetchNumbers4DrawResult(
  drawNumber: number,
): Promise<{ numbers: string } | null> {
  const row = await fetchNumbers4DrawFullRow(drawNumber);
  if (!row?.numbers) return null;
  return { numbers: String(row.numbers) };
}

export async function fetchNumbers4DrawFullRow(
  drawNumber: number,
): Promise<Numbers4DrawRow | null> {
  try {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from("numbers4_draws")
      .select("*")
      .eq("draw_number", drawNumber)
      .maybeSingle();
    if (error || data == null) return null;
    return data as Numbers4DrawRow;
  } catch {
    return null;
  }
}

export function getLatestEnsembleRun(
  payload: EnsemblePayload | null,
): EnsemblePredictionRun | null {
  const preds = payload?.predictions;
  if (!preds?.length) return null;
  return preds[preds.length - 1] ?? null;
}

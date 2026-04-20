import { promises as fs } from "node:fs";
import path from "node:path";
import { cache } from "react";

import { createStaticClient } from "@/lib/supabase/static";

import type {
  Loto6BudgetPlanPayload,
  Loto6EnsemblePayload,
  Loto6EnsembleRun,
  Loto6MethodPayload,
  Loto6MethodRow,
  Loto6MethodRun,
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

async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function loadLoto6BundleFromDatabase(
  targetDrawNumber: number,
): Promise<Loto6PredictionBundle | null> {
  try {
    const supabase = createStaticClient();
    const { data: rows, error } = await supabase
      .from("loto6_daily_prediction_documents")
      .select("doc_kind, method_slug, payload, relative_path")
      .eq("target_draw_number", targetDrawNumber);

    if (error || !rows?.length) return null;

    let ensemble: Loto6EnsemblePayload | null = null;
    let budgetPlan: Loto6BudgetPlanPayload | null = null;
    const methodRows: Loto6MethodRow[] = [];

    for (const row of rows as DbDocRow[]) {
      if (row.doc_kind === "ensemble") {
        ensemble = row.payload as Loto6EnsemblePayload;
      } else if (row.doc_kind === "budget_plan") {
        budgetPlan = row.payload as Loto6BudgetPlanPayload;
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
      budgetPlan,
      methodRows: normalizeMethodRows(methodRows),
    };
  } catch {
    return null;
  }
}

async function scanLoto6MethodsForDraw(
  repoRoot: string,
  drawNumber: number,
): Promise<Loto6MethodRow[]> {
  const base = path.join(repoRoot, "predictions", "daily", "methods");
  const fname = `loto6_${drawNumber}.json`;
  const rows: Loto6MethodRow[] = [];
  try {
    const entries = await fs.readdir(base, { withFileTypes: true });
    for (const ent of entries) {
      if (!ent.isDirectory()) continue;
      const fp = path.join(base, ent.name, fname);
      const payload = await readJsonFile<Loto6MethodPayload>(fp);
      if (payload === null) continue;
      const rel = path.relative(repoRoot, fp).split(path.sep).join("/");
      rows.push({
        slug: ent.name,
        relativePath: rel,
        payload,
      });
    }
  } catch {
    /* methods なし */
  }
  return rows.sort((a, b) => a.slug.localeCompare(b.slug));
}

async function loadLoto6BundleFromFilesystem(
  repoRoot: string,
  drawNumber: number,
): Promise<Loto6PredictionBundle | null> {
  const ensemblePath = path.join(
    repoRoot,
    "predictions",
    "daily",
    `loto6_${drawNumber}.json`,
  );
  const budgetPath = path.join(
    repoRoot,
    "predictions",
    "daily",
    `budget_plan_loto6_${drawNumber}.json`,
  );

  const [ensembleFile, budgetFile, methodRows] = await Promise.all([
    readJsonFile<Loto6EnsemblePayload>(ensemblePath),
    readJsonFile<Loto6BudgetPlanPayload>(budgetPath),
    scanLoto6MethodsForDraw(repoRoot, drawNumber),
  ]);

  if (
    ensembleFile == null &&
    budgetFile == null &&
    methodRows.length === 0
  ) {
    return null;
  }

  return {
    targetDrawNumber: drawNumber,
    ensemble: ensembleFile,
    budgetPlan: budgetFile,
    methodRows: normalizeMethodRows(methodRows),
  };
}

function bundleHasPredictions(bundle: Loto6PredictionBundle): boolean {
  return (
    bundle.ensemble != null ||
    bundle.budgetPlan != null ||
    bundle.methodRows.length > 0
  );
}

/**
 * DB とリポジトリ JSON をマージ。ensemble / budget_plan は DB を優先し、
 * 欠けはファイルで補完。手法は slug 単位で DB があれば DB、なければファイル。
 */
function mergeLoto6Bundles(
  fromDb: Loto6PredictionBundle | null,
  fromFs: Loto6PredictionBundle | null,
  targetDrawNumber: number,
): Loto6PredictionBundle {
  const ensemble = fromDb?.ensemble ?? fromFs?.ensemble ?? null;
  const budgetPlan = fromDb?.budgetPlan ?? fromFs?.budgetPlan ?? null;
  const bySlug = new Map<string, Loto6MethodRow>();
  for (const row of fromFs?.methodRows ?? []) {
    bySlug.set(row.slug, row);
  }
  for (const row of fromDb?.methodRows ?? []) {
    bySlug.set(row.slug, row);
  }
  return {
    targetDrawNumber,
    ensemble,
    budgetPlan,
    methodRows: normalizeMethodRows([...bySlug.values()]),
  };
}

async function tryLoadLoto6PredictionBundle(
  targetDrawNumber: number,
): Promise<Loto6PredictionBundle | null> {
  const repoRoot = path.join(process.cwd(), "..", "..");
  const [fromDb, fromFs] = await Promise.all([
    loadLoto6BundleFromDatabase(targetDrawNumber),
    loadLoto6BundleFromFilesystem(repoRoot, targetDrawNumber),
  ]);
  const merged = mergeLoto6Bundles(fromDb, fromFs, targetDrawNumber);
  if (!bundleHasPredictions(merged)) return null;
  return merged;
}

/**
 * 指定回の予測バンドル。Supabase と `predictions/daily/*.json` を並列取得し、
 * 欠片をマージ（同一項目は DB 優先、手法は slug で DB が上書き）。
 */
export const loadLoto6PredictionBundle = cache(
  async (targetDrawNumber: number): Promise<Loto6PredictionBundle | null> => {
    if (!Number.isFinite(targetDrawNumber) || targetDrawNumber < 1) return null;
    return tryLoadLoto6PredictionBundle(targetDrawNumber);
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

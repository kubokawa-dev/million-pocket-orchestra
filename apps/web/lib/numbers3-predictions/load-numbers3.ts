import { promises as fs } from "node:fs";
import path from "node:path";
import { cache } from "react";

import { createStaticClient } from "@/lib/supabase/static";
import type { Numbers3DrawRow } from "@/lib/numbers3";

import {
  FALLBACK_BUDGET_NUMBERS3,
  FALLBACK_ENSEMBLE_NUMBERS3,
  FALLBACK_METHOD_ROWS_NUMBERS3,
  FALLBACK_NUMBERS3_TARGET_DRAW,
} from "./fallback-numbers3";
import { contributorsForEnsembleNumber } from "./ensemble-contributors";
import { normalizeNumbers3 } from "./prediction-hit-utils";
import { summarizeMethodPayload } from "./summarize-method";
import type {
  BudgetPlanPayload,
  EnsemblePayload,
  EnsemblePredictionRun,
  MethodPredictionRow,
  Numbers4DrawWinningModelHit,
  Numbers4PredictionBundle,
} from "../numbers4-predictions/types";

/** ナンバーズ3 UI 用（ペイロード形は numbers4 と共通） */
export type Numbers3PredictionBundle = Numbers4PredictionBundle;

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
    const re = /^numbers3_(\d+)\.json$/;
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
    const supabase = createStaticClient();
    const { data, error } = await supabase
      .from("numbers3_daily_prediction_documents")
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

/** DB・リポジトリのいずれかで最新とみなす対象回号（ナンバーズ3） */
export async function resolveNumbers3TargetDrawNumber(): Promise<number> {
  const repoRoot = path.join(process.cwd(), "..", "..");
  const [fromDb, fromFs] = await Promise.all([
    maxDrawFromSupabase(),
    maxDrawFromFilesystem(repoRoot),
  ]);
  const cands = [fromDb, fromFs].filter(
    (x): x is number => x != null && x > 0,
  );
  if (cands.length === 0) return FALLBACK_NUMBERS3_TARGET_DRAW;
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
    Numbers3PredictionBundle,
    "ensemble" | "budgetPlan" | "methodRows"
  > | null
> {
  const supabase = createStaticClient();
  const { data: rows, error } = await supabase
    .from("numbers3_daily_prediction_documents")
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
  const fname = `numbers3_${drawNumber}.json`;
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

type DbMethodDocRow = {
  target_draw_number: number;
  method_slug: string | null;
  payload: unknown;
  relative_path: string | null;
};

async function fetchMethodRowsGroupedByDraw(
  drawNumbers: number[],
): Promise<Map<number, MethodPredictionRow[]>> {
  const uniq = [...new Set(drawNumbers)].filter(
    (n) => Number.isFinite(n) && n > 0,
  ) as number[];
  const map = new Map<number, MethodPredictionRow[]>();
  for (const d of uniq) map.set(d, []);

  if (uniq.length === 0) return map;

  try {
    const supabase = createStaticClient();
    const { data, error } = await supabase
      .from("numbers3_daily_prediction_documents")
      .select("target_draw_number, method_slug, payload, relative_path")
      .eq("doc_kind", "method")
      .in("target_draw_number", uniq);

    if (!error && data?.length) {
      for (const row of data as DbMethodDocRow[]) {
        const tn = row.target_draw_number;
        if (!row.method_slug || !Number.isFinite(tn)) continue;
        const cur = map.get(tn) ?? [];
        cur.push({
          slug: row.method_slug,
          relativePath: row.relative_path,
          ...summarizeMethodPayload(row.payload),
        });
        map.set(tn, cur);
      }
      for (const tn of uniq) {
        const cur = map.get(tn) ?? [];
        cur.sort((a, b) => a.slug.localeCompare(b.slug));
        map.set(tn, cur);
      }
    }
  } catch {
    /* FS で補完 */
  }

  const repoRoot = path.join(process.cwd(), "..", "..");
  const missing = uniq.filter((d) => (map.get(d) ?? []).length === 0);
  const batchSize = 8;
  for (let i = 0; i < missing.length; i += batchSize) {
    const chunk = missing.slice(i, i + batchSize);
    const results = await Promise.all(
      chunk.map(async (d) => {
        const rows = await scanMethodsForDraw(repoRoot, d);
        return [d, rows] as const;
      }),
    );
    for (const [d, rows] of results) {
      map.set(d, rows);
    }
  }

  return map;
}

/**
 * 当選番号ごとに、各モデル候補（最大96件）へストレート／ボックスで入っていた slug を列挙する。
 */
export async function buildWinningModelHitsForDrawListNumbers3(
  draws: { draw_number: number; numbers: string | null | undefined }[],
): Promise<Numbers4DrawWinningModelHit[]> {
  const nums = draws.map((d) => d.draw_number);
  const methodMap = await fetchMethodRowsGroupedByDraw(nums);

  return draws.map((d) => {
    const norm = normalizeNumbers3(
      d.numbers != null ? String(d.numbers) : "",
    );
    const rows = methodMap.get(d.draw_number) ?? [];
    if (!norm || rows.length === 0) {
      return {
        draw_number: d.draw_number,
        numbers_normalized: norm,
        exact_slugs: [],
        box_only_slugs: [],
      };
    }
    const { exactSlugs, boxOnlySlugs } = contributorsForEnsembleNumber(
      norm,
      rows,
    );
    return {
      draw_number: d.draw_number,
      numbers_normalized: norm,
      exact_slugs: exactSlugs,
      box_only_slugs: boxOnlySlugs,
    };
  });
}

async function loadBundleFromFilesystem(
  repoRoot: string,
  drawNumber: number,
): Promise<Pick<Numbers3PredictionBundle, "ensemble" | "budgetPlan" | "methodRows">> {
  const ensemblePath = path.join(
    repoRoot,
    "predictions",
    "daily",
    `numbers3_${drawNumber}.json`,
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
): Promise<Numbers3PredictionBundle | null> {
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

export async function loadNumbers3PredictionBundleForDraw(
  targetDrawNumber: number,
): Promise<Numbers3PredictionBundle | null> {
  if (!Number.isFinite(targetDrawNumber) || targetDrawNumber < 1) return null;
  return tryLoadBundleForDraw(targetDrawNumber);
}

export async function loadNumbers3PredictionBundle(): Promise<Numbers3PredictionBundle> {
  const targetDrawNumber = await resolveNumbers3TargetDrawNumber();
  const got = await tryLoadBundleForDraw(targetDrawNumber);
  if (got) return got;

  return {
    source: "embedded",
    targetDrawNumber: FALLBACK_NUMBERS3_TARGET_DRAW,
    ensemble: FALLBACK_ENSEMBLE_NUMBERS3,
    budgetPlan: FALLBACK_BUDGET_NUMBERS3,
    methodRows: FALLBACK_METHOD_ROWS_NUMBERS3,
  };
}

export async function fetchNumbers3DrawResult(
  drawNumber: number,
): Promise<{ numbers: string } | null> {
  const row = await fetchNumbers3DrawFullRow(drawNumber);
  if (!row?.numbers) return null;
  return { numbers: String(row.numbers) };
}

export async function fetchNumbers3DrawFullRow(
  drawNumber: number,
): Promise<Numbers3DrawRow | null> {
  try {
    const supabase = createStaticClient();
    const { data, error } = await supabase
      .from("numbers3_draws")
      .select("*")
      .eq("draw_number", drawNumber)
      .maybeSingle();
    if (error || data == null) return null;
    return data as Numbers3DrawRow;
  } catch {
    return null;
  }
}

export async function fetchOfficialWinningDrawsBeforeTargetNumbers3(
  targetDrawNumber: number,
  limit: number,
): Promise<{ draw_number: number; numbers: string }[]> {
  if (!Number.isFinite(targetDrawNumber) || targetDrawNumber < 1) return [];
  if (!Number.isFinite(limit) || limit < 1) return [];
  try {
    const supabase = createStaticClient();
    const { data, error } = await supabase
      .from("numbers3_draws")
      .select("draw_number, numbers")
      .lt("draw_number", targetDrawNumber)
      .not("numbers", "is", null)
      .order("draw_number", { ascending: false })
      .limit(limit);
    if (error || !data?.length) return [];
    return data
      .filter(
        (r) =>
          r.draw_number != null &&
          r.numbers != null &&
          String(r.numbers).trim() !== "",
      )
      .map((r) => ({
        draw_number: Number(r.draw_number),
        numbers: String(r.numbers),
      }))
      .filter((r) => Number.isFinite(r.draw_number) && r.draw_number > 0);
  } catch {
    return [];
  }
}

export function getLatestEnsembleRun(
  payload: EnsemblePayload | null,
): EnsemblePredictionRun | null {
  const preds = payload?.predictions;
  if (!preds?.length) return null;
  return preds[preds.length - 1] ?? null;
}

export const getCachedNumbers3DrawFullRow = cache(fetchNumbers3DrawFullRow);

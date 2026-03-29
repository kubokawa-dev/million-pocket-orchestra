/** predictions/daily/numbers4_{n}.json の先頭付近と整合する想定の型（緩い） */

export type EnsembleTopPrediction = {
  rank?: number;
  number?: string;
  score?: number;
  similar_patterns?: { number?: string; description?: string; score?: number }[];
};

export type EnsemblePredictionRun = {
  time?: string;
  time_jst?: string;
  ensemble_weights?: Record<string, number>;
  top_predictions?: EnsembleTopPrediction[];
};

export type EnsemblePayload = {
  draw_number?: number;
  target_draw_number?: number;
  date?: string;
  predictions?: EnsemblePredictionRun[];
  last_updated?: string;
};

export type BudgetRecommendation = {
  priority?: string;
  number?: string;
  buy_method?: string;
  box_type?: string;
  coverage?: number;
  reason?: string;
};

export type BudgetPlanSlice = {
  budget?: string;
  slots?: number;
  total_coverage?: number;
  probability?: string;
  recommendations?: BudgetRecommendation[];
};

export type BudgetPlanPayload = {
  target_draw_number?: number;
  created_at?: string;
  plan_5?: BudgetPlanSlice;
  plan_10?: BudgetPlanSlice;
};

export type MethodTopPrediction = {
  rank?: number;
  number: string;
  score: number | null;
};

/** doc_kind=method に相当する行（UI・合意集計用） */
export type MethodPredictionRow = {
  slug: string;
  relativePath: string | null;
  runs: number;
  lastTimeJst: string | null;
  topNumber: string | null;
  topPredictions: MethodTopPrediction[];
};

export type Numbers4PredictionBundle = {
  source: "database" | "repository_files" | "embedded";
  targetDrawNumber: number;
  ensemble: EnsemblePayload | null;
  budgetPlan: BudgetPlanPayload | null;
  methodRows: MethodPredictionRow[];
};

/** @deprecated 互換名 */
export type PredictionBundle6949 = Numbers4PredictionBundle;

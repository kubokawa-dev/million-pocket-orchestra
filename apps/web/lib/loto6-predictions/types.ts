/** predictions/daily の loto6 JSON（ensemble・methods 配下）と整合する緩い型 */

export type Loto6TopPrediction = {
  rank?: number;
  main?: number[];
  bonus?: number | null;
  score?: number | null;
};

export type Loto6MethodRun = {
  time?: string;
  time_jst?: string;
  method?: string;
  top_predictions?: Loto6TopPrediction[];
};

export type Loto6MethodPayload = {
  draw_number?: number;
  target_draw_number?: number;
  date?: string;
  method?: string;
  predictions?: Loto6MethodRun[];
  prediction_count?: number;
};

export type Loto6EnsembleRun = {
  time?: string;
  time_jst?: string;
  ensemble_weights?: Record<string, number>;
  top_predictions?: Loto6TopPrediction[];
};

export type Loto6EnsemblePayload = {
  draw_number?: number;
  target_draw_number?: number;
  date?: string;
  predictions?: Loto6EnsembleRun[];
  last_updated?: string;
};

export type Loto6MethodRow = {
  slug: string;
  relativePath: string | null;
  payload: Loto6MethodPayload;
};

/** predictions/daily/budget_plan_loto6_{n}.json（MVP・簡易） */
export type Loto6BudgetRecommendation = {
  priority?: string;
  number?: string;
  buy_method?: string;
  reason?: string;
};

export type Loto6BudgetPlanSlice = {
  budget?: string;
  slots?: number;
  recommendations?: Loto6BudgetRecommendation[];
};

export type Loto6BudgetPlanPayload = {
  target_draw_number?: number;
  created_at?: string;
  planner_version?: string;
  monthly_budget_guide?: Record<string, unknown>;
  plan_5?: Loto6BudgetPlanSlice;
  plan_10?: Loto6BudgetPlanSlice;
};

export type Loto6PredictionBundle = {
  targetDrawNumber: number;
  ensemble: Loto6EnsemblePayload | null;
  budgetPlan: Loto6BudgetPlanPayload | null;
  methodRows: Loto6MethodRow[];
};

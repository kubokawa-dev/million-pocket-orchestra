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
  hot_models?: { model: string; score: number }[];
  recent_flow?: { draw: number; model: string; score: number }[];
  next_model_predictions?: { model: string; probability: number; count: number; total: number }[];
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
  /** v12: その口がユニーク通りに何通り足したか（同一ボックス型は0） */
  marginal_coverage?: number;
  reason?: string;
  /** v15: 期待値プランの期待値（円） */
  expected_value?: number;
  /** v15: ボックス配当の目安（円） */
  box_payout?: number;
};

export type BudgetPlanSlice = {
  budget?: string;
  slots?: number;
  total_coverage?: number;
  /** v12: ユニーク通りの意味づけ */
  coverage_note?: string;
  probability?: string;
  recommendations?: BudgetRecommendation[];
};

export type MonthlyBudgetGuideMeta = {
  max_yen_per_month?: number;
  default_per_draw_yen?: number;
  max_per_draw_yen?: number;
  yen_per_ticket?: number;
  slots_for_1000yen?: number;
  slots_for_2000yen?: number;
  daily_full_month_hint?: string;
};

/** v15: ハイブリッドプラン（ボックス＋ミニ） */
export type HybridPlanPayload = {
  strategy?: string;
  total_budget?: string;
  box_slots?: number;
  mini_slots?: number;
  box_coverage?: number;
  box_probability?: string;
  mini_unique_tails?: number;
  mini_probability?: string;
  combined_probability?: string;
  box_recommendations?: BudgetRecommendation[];
  mini_recommendations?: BudgetRecommendation[];
};

/** v15: 分散購入プランのセッション */
export type DistributedSession = {
  session?: number;
  budget?: string;
  tickets?: number;
  session_coverage?: number;
  picks?: BudgetRecommendation[];
};

/** v15: 分散購入プラン */
export type DistributedPlanPayload = {
  strategy?: string;
  total_budget?: string;
  sessions?: number;
  tickets_per_session?: number;
  cumulative_unique_coverage?: number;
  cumulative_probability?: string;
  monthly_hit_probability?: string;
  schedule?: DistributedSession[];
};

/** v15: 期待値プラン */
export type ExpectedValuePlanSlice = BudgetPlanSlice & {
  total_expected_value?: number;
};

/** v16: オールミニプラン */
export type AllMiniPlanPayload = {
  strategy?: string;
  total_budget?: string;
  slots?: number;
  per_draw_probability?: string;
  draws_per_month?: number;
  monthly_probability?: string;
  mini_payout_estimate?: string;
  recommendations?: BudgetRecommendation[];
};

/** v16: セット購入プラン */
export type SetPlanPayload = {
  strategy?: string;
  total_budget?: string;
  slots?: number;
  total_coverage?: number;
  probability?: string;
  recommendations?: BudgetRecommendation[];
};

/** v16: 月間シミュレーション戦略 */
export type MonthlyStrategy = {
  name?: string;
  budget_per_draw?: string;
  monthly_budget?: string;
  per_draw_probability?: string;
  monthly_probability?: string;
  monthly_probability_raw?: number;
  payout_type?: string;
};

/** v16: 月間確率シミュレーション */
export type MonthlySimulationPayload = {
  draws_per_month?: number;
  note?: string;
  strategies?: MonthlyStrategy[];
};

export type BudgetPlanPayload = {
  target_draw_number?: number;
  created_at?: string;
  planner_version?: string;
  monthly_budget_guide?: MonthlyBudgetGuideMeta;
  plan_5?: BudgetPlanSlice;
  plan_10?: BudgetPlanSlice;
  /** v15: ハイブリッドプラン（ボックス＋ミニ） */
  hybrid_5?: HybridPlanPayload;
  hybrid_10?: HybridPlanPayload;
  /** v15: 期待値プラン */
  expected_value_5?: ExpectedValuePlanSlice;
  expected_value_10?: ExpectedValuePlanSlice;
  /** v15: 分散購入プラン */
  distributed_plan?: DistributedPlanPayload;
  /** v16: オールミニプラン */
  all_mini_5?: AllMiniPlanPayload;
  /** v16: セット購入プラン */
  set_plan?: SetPlanPayload;
  set_plan_5?: SetPlanPayload;
  /** v16: 月間確率シミュレーション */
  monthly_simulation?: MonthlySimulationPayload;
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
  source: "database" | "repository_files" | "embedded" | "mixed";
  targetDrawNumber: number;
  ensemble: EnsemblePayload | null;
  budgetPlan: BudgetPlanPayload | null;
  methodRows: MethodPredictionRow[];
};

/** 当選番号が各 method の候補リスト（最大96件）に含まれていたかの集計 */
export type Numbers4DrawWinningModelHit = {
  draw_number: number;
  numbers_normalized: string | null;
  exact_slugs: string[];
  box_only_slugs: string[];
};

/** @deprecated 互換名 */
export type PredictionBundle6949 = Numbers4PredictionBundle;

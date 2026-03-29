import type {
  BudgetPlanPayload,
  EnsemblePayload,
  MethodSummaryRow,
} from "./types";

/** DB / リポジトリ JSON が無い環境用の最小データ */
export const FALLBACK_ENSEMBLE_6949: EnsemblePayload = {
  target_draw_number: 6949,
  draw_number: 6949,
  date: "demo",
  predictions: [
    {
      time_jst: "—",
      ensemble_weights: { demo: 1 },
      top_predictions: [
        {
          rank: 1,
          number: "1234",
          score: 42,
          similar_patterns: [],
        },
      ],
    },
  ],
};

export const FALLBACK_BUDGET_6949: BudgetPlanPayload = {
  target_draw_number: 6949,
  plan_5: {
    budget: "デモ",
    slots: 0,
    recommendations: [],
  },
  plan_10: {
    budget: "デモ",
    slots: 0,
    recommendations: [],
  },
};

export const FALLBACK_METHOD_ROWS: MethodSummaryRow[] = [];

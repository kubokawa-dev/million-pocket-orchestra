import type {
  BudgetPlanPayload,
  EnsemblePayload,
  MethodPredictionRow,
} from "../numbers4-predictions/types";

export const FALLBACK_NUMBERS3_TARGET_DRAW = 1;

/** DB / リポジトリ JSON が無い環境用の最小データ */
export const FALLBACK_ENSEMBLE_NUMBERS3: EnsemblePayload = {
  target_draw_number: 1,
  draw_number: 1,
  date: "demo",
  predictions: [
    {
      time_jst: "—",
      ensemble_weights: { demo: 1 },
      top_predictions: [
        {
          rank: 1,
          number: "123",
          score: 42,
          similar_patterns: [],
        },
      ],
    },
  ],
};

export const FALLBACK_BUDGET_NUMBERS3: BudgetPlanPayload = {
  target_draw_number: 1,
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

export const FALLBACK_METHOD_ROWS_NUMBERS3: MethodPredictionRow[] = [];

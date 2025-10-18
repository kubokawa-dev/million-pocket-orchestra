-- CreateTable: アンサンブル予測の実行履歴
CREATE TABLE IF NOT EXISTS "numbers4_ensemble_predictions" (
    "id" SERIAL NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "target_draw_number" INTEGER,
    "model_updated_at" TEXT,
    "model_events_count" INTEGER,
    "ensemble_weights" TEXT NOT NULL,
    "predictions_count" INTEGER NOT NULL,
    "top_predictions" TEXT NOT NULL,
    "model_predictions" TEXT NOT NULL,
    "actual_draw_number" INTEGER,
    "actual_numbers" TEXT,
    "hit_status" TEXT,
    "hit_count" INTEGER,
    "notes" TEXT,

    CONSTRAINT "numbers4_ensemble_predictions_pkey" PRIMARY KEY ("id")
);

-- CreateTable: 個別の予測候補の詳細
CREATE TABLE IF NOT EXISTS "numbers4_prediction_candidates" (
    "id" SERIAL NOT NULL,
    "ensemble_prediction_id" INTEGER NOT NULL,
    "rank" INTEGER NOT NULL,
    "number" TEXT NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "contributing_models" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "numbers4_prediction_candidates_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX IF NOT EXISTS "numbers4_ensemble_predictions_created_at_idx" 
    ON "numbers4_ensemble_predictions"("created_at");

CREATE INDEX IF NOT EXISTS "numbers4_ensemble_predictions_target_draw_number_idx" 
    ON "numbers4_ensemble_predictions"("target_draw_number");

CREATE INDEX IF NOT EXISTS "numbers4_prediction_candidates_ensemble_prediction_id_idx" 
    ON "numbers4_prediction_candidates"("ensemble_prediction_id");

CREATE INDEX IF NOT EXISTS "numbers4_prediction_candidates_number_idx" 
    ON "numbers4_prediction_candidates"("number");

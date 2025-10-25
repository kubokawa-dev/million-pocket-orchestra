-- CreateTable
CREATE TABLE "loto6_model_events" (
    "id" SERIAL NOT NULL,
    "event_ts" TEXT NOT NULL,
    "actual_number" TEXT NOT NULL,
    "predictions" TEXT NOT NULL,
    "hit_exact" INTEGER NOT NULL DEFAULT 0,
    "top_match" TEXT,
    "max_position_hits" INTEGER NOT NULL,
    "notes" TEXT,

    CONSTRAINT "loto6_model_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "loto6_predictions_log" (
    "id" SERIAL NOT NULL,
    "created_at" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "label" TEXT,
    "number" TEXT NOT NULL,
    "target_draw_number" INTEGER,

    CONSTRAINT "loto6_predictions_log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "loto6_ensemble_predictions" (
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
    "actual_bonus_number" INTEGER,
    "hit_status" TEXT,
    "hit_count" INTEGER,
    "bonus_hit" BOOLEAN,
    "notes" TEXT,

    CONSTRAINT "loto6_ensemble_predictions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "loto6_prediction_candidates" (
    "id" SERIAL NOT NULL,
    "ensemble_prediction_id" INTEGER NOT NULL,
    "rank" INTEGER NOT NULL,
    "number" TEXT NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "contributing_models" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "loto6_prediction_candidates_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "loto6_predictions_log_target_draw_number_idx" ON "loto6_predictions_log"("target_draw_number");

-- CreateIndex
CREATE INDEX "loto6_ensemble_predictions_created_at_idx" ON "loto6_ensemble_predictions"("created_at");

-- CreateIndex
CREATE INDEX "loto6_ensemble_predictions_target_draw_number_idx" ON "loto6_ensemble_predictions"("target_draw_number");

-- CreateIndex
CREATE INDEX "loto6_prediction_candidates_ensemble_prediction_id_idx" ON "loto6_prediction_candidates"("ensemble_prediction_id");

-- CreateIndex
CREATE INDEX "loto6_prediction_candidates_number_idx" ON "loto6_prediction_candidates"("number");

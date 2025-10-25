-- CreateTable
CREATE TABLE "numbers4_draws" (
    "draw_number" INTEGER NOT NULL,
    "draw_date" TEXT NOT NULL,
    "numbers" TEXT NOT NULL,

    CONSTRAINT "numbers4_draws_pkey" PRIMARY KEY ("draw_number")
);

-- CreateTable
CREATE TABLE "loto6_draws" (
    "draw_number" INTEGER NOT NULL,
    "draw_date" TEXT NOT NULL,
    "numbers" TEXT NOT NULL,
    "bonus_number" INTEGER NOT NULL,

    CONSTRAINT "loto6_draws_pkey" PRIMARY KEY ("draw_number")
);

-- CreateTable
CREATE TABLE "numbers4_model_events" (
    "id" SERIAL NOT NULL,
    "event_ts" TEXT NOT NULL,
    "actual_number" TEXT NOT NULL,
    "predictions" TEXT NOT NULL,
    "hit_exact" INTEGER NOT NULL DEFAULT 0,
    "top_match" TEXT,
    "max_position_hits" INTEGER NOT NULL,
    "notes" TEXT,

    CONSTRAINT "numbers4_model_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "numbers4_predictions_log" (
    "id" SERIAL NOT NULL,
    "created_at" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "label" TEXT,
    "number" TEXT NOT NULL,

    CONSTRAINT "numbers4_predictions_log_pkey" PRIMARY KEY ("id")
);

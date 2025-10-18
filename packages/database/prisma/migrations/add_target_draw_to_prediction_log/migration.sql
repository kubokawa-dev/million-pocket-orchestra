-- Add target_draw_number column to numbers4_predictions_log
ALTER TABLE "numbers4_predictions_log" 
ADD COLUMN IF NOT EXISTS "target_draw_number" INTEGER;

-- Create index for target_draw_number
CREATE INDEX IF NOT EXISTS "numbers4_predictions_log_target_draw_number_idx" 
ON "numbers4_predictions_log"("target_draw_number");

-- Update existing records with target_draw_number based on created_at
-- (最新の抽選回+1を設定する簡易的な方法)
UPDATE "numbers4_predictions_log" 
SET target_draw_number = (
    SELECT MAX(draw_number) + 1 
    FROM numbers4_draws 
    WHERE draw_date <= numbers4_predictions_log.created_at
)
WHERE target_draw_number IS NULL;

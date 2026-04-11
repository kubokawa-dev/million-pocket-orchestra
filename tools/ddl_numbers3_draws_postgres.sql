-- Supabase / PostgreSQL 用: numbers3_draws（numbers4_draws と同じ列構成）
-- SQL Editor で手動適用する場合の参考。通常は apps/web/supabase/migrations を利用。
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS draw_date TEXT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS numbers TEXT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier1_winners INTEGER;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier1_payout_yen BIGINT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier2_winners INTEGER;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier2_payout_yen BIGINT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier3_winners INTEGER;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier3_payout_yen BIGINT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier4_winners INTEGER;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS tier4_payout_yen BIGINT;

-- テーブルがまだ無い場合（マイグレーション推奨）:
-- CREATE TABLE numbers3_draws (
--   draw_number INTEGER PRIMARY KEY,
--   draw_date TEXT NOT NULL,
--   numbers TEXT NOT NULL,
--   tier1_winners INTEGER,
--   tier1_payout_yen BIGINT,
--   tier2_winners INTEGER,
--   tier2_payout_yen BIGINT,
--   tier3_winners INTEGER,
--   tier3_payout_yen BIGINT,
--   tier4_winners INTEGER,
--   tier4_payout_yen BIGINT
-- );

-- Supabase / PostgreSQL 用: numbers4_draws 案A（口数・払戻8列）
-- SQL Editor で実行するか: psql "$DATABASE_URL" -f tools/ddl_numbers4_draws_postgres.sql
--
-- 既存テーブルに列だけ足す場合:
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier1_winners INTEGER;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier1_payout_yen BIGINT;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier2_winners INTEGER;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier2_payout_yen BIGINT;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier3_winners INTEGER;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier3_payout_yen BIGINT;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier4_winners INTEGER;
ALTER TABLE numbers4_draws ADD COLUMN IF NOT EXISTS tier4_payout_yen BIGINT;

-- テーブルがまだ無い場合は（上の ALTER の前にコメントアウトして使う）:
-- CREATE TABLE numbers4_draws (
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

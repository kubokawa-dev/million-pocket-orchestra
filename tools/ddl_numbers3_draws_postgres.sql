-- Supabase / PostgreSQL 用: numbers3_draws（3列）
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS draw_date TEXT;
ALTER TABLE numbers3_draws ADD COLUMN IF NOT EXISTS numbers TEXT;

-- テーブルがまだ無い場合:
-- CREATE TABLE numbers3_draws (
--   draw_number INTEGER PRIMARY KEY,
--   draw_date TEXT NOT NULL,
--   numbers TEXT NOT NULL
-- );

-- Supabase / PostgreSQL 用: loto6_draws（月次 CSV 20列相当）
-- アプリの migration と揃える場合は apps/web/supabase/migrations を参照

create table if not exists public.loto6_draws (
  draw_number integer primary key,
  draw_date text not null,
  numbers text not null,
  bonus_number integer not null,
  tier1_winners integer,
  tier1_payout_yen bigint,
  tier2_winners integer,
  tier2_payout_yen bigint,
  tier3_winners integer,
  tier3_payout_yen bigint,
  tier4_winners integer,
  tier4_payout_yen bigint,
  tier5_winners integer,
  tier5_payout_yen bigint,
  carryover_yen bigint
);

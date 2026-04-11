-- numbers3_draws を numbers4_draws と同じ当選口数・払戻列に揃える（未設定は NULL）
alter table public.numbers3_draws add column if not exists tier1_winners integer;
alter table public.numbers3_draws add column if not exists tier1_payout_yen bigint;
alter table public.numbers3_draws add column if not exists tier2_winners integer;
alter table public.numbers3_draws add column if not exists tier2_payout_yen bigint;
alter table public.numbers3_draws add column if not exists tier3_winners integer;
alter table public.numbers3_draws add column if not exists tier3_payout_yen bigint;
alter table public.numbers3_draws add column if not exists tier4_winners integer;
alter table public.numbers3_draws add column if not exists tier4_payout_yen bigint;

-- ロト6 抽選結果（loto6/*.csv の全列に対応）
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

alter table public.loto6_draws enable row level security;

create policy "loto6_draws_select_authenticated"
  on public.loto6_draws for select
  to authenticated
  using (true);

create policy "loto6_draws_select_anon"
  on public.loto6_draws for select
  to anon
  using (true);

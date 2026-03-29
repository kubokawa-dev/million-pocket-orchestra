-- ナンバーズ4 抽選結果（CSV / lottery.db と同じ論理列）
create table if not exists public.numbers4_draws (
  draw_number integer primary key,
  draw_date text not null,
  numbers text not null,
  tier1_winners integer,
  tier1_payout_yen bigint,
  tier2_winners integer,
  tier2_payout_yen bigint,
  tier3_winners integer,
  tier3_payout_yen bigint,
  tier4_winners integer,
  tier4_payout_yen bigint
);

alter table public.numbers4_draws enable row level security;

create policy "numbers4_draws_select_authenticated"
  on public.numbers4_draws for select
  to authenticated
  using (true);

create policy "numbers4_draws_select_anon"
  on public.numbers4_draws for select
  to anon
  using (true);

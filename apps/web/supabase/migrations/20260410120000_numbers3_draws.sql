-- ナンバーズ3 抽選結果
create table if not exists public.numbers3_draws (
  draw_number integer primary key,
  draw_date text not null,
  numbers text not null
);

alter table public.numbers3_draws enable row level security;

create policy "numbers3_draws_select_authenticated"
  on public.numbers3_draws for select
  to authenticated
  using (true);

create policy "numbers3_draws_select_anon"
  on public.numbers3_draws for select
  to anon
  using (true);

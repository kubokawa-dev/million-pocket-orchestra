-- ロト6 日次予測 JSON（predictions/daily の loto6_*.json / methods/*/loto6_*.json）
create table if not exists public.loto6_daily_prediction_documents (
  id bigserial primary key,
  target_draw_number integer not null,
  doc_kind text not null check (doc_kind in ('ensemble', 'method')),
  method_slug text not null default '',
  relative_path text not null,
  payload jsonb not null,
  payload_sha256 text,
  file_mtime timestamptz,
  ingested_at timestamptz not null default now(),
  check (
    (doc_kind = 'method' and method_slug <> '')
    or (doc_kind = 'ensemble' and method_slug = '')
  ),
  unique (target_draw_number, doc_kind, method_slug)
);

create index if not exists idx_loto6_daily_docs_draw
  on public.loto6_daily_prediction_documents (target_draw_number);
create index if not exists idx_loto6_daily_docs_kind
  on public.loto6_daily_prediction_documents (doc_kind);
create index if not exists idx_loto6_daily_docs_payload
  on public.loto6_daily_prediction_documents using gin (payload);

alter table public.loto6_daily_prediction_documents enable row level security;

create policy "loto6_daily_docs_select_authenticated"
  on public.loto6_daily_prediction_documents for select
  to authenticated
  using (true);

create policy "loto6_daily_docs_select_anon"
  on public.loto6_daily_prediction_documents for select
  to anon
  using (true);

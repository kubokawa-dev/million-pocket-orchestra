-- loto6_daily_prediction_documents に doc_kind = budget_plan を追加（Numbers3/4 と同列の運用）

do $$
declare
  r record;
begin
  for r in
    select c.conname
    from pg_constraint c
    join pg_class t on c.conrelid = t.oid
    join pg_namespace n on t.relnamespace = n.oid
    where n.nspname = 'public'
      and t.relname = 'loto6_daily_prediction_documents'
      and c.contype = 'c'
  loop
    execute format(
      'alter table public.loto6_daily_prediction_documents drop constraint if exists %I',
      r.conname
    );
  end loop;
end $$;

alter table public.loto6_daily_prediction_documents
  add constraint loto6_daily_prediction_documents_doc_shape_check
  check (
    doc_kind in ('ensemble', 'method', 'budget_plan')
    and (
      (doc_kind = 'method' and btrim(method_slug) <> '')
      or (doc_kind = 'ensemble' and coalesce(method_slug, '') = '')
      or (doc_kind = 'budget_plan' and coalesce(method_slug, '') = '')
    )
  );

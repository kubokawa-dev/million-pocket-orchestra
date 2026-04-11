-- 20260412130000 でテーブル作成済みのプロジェクト向け: API 経由 UPSERT 用 GRANT（冪等）
grant all on table public.loto6_daily_prediction_documents to service_role;
grant select on table public.loto6_daily_prediction_documents to anon, authenticated;
grant usage, select on sequence public.loto6_daily_prediction_documents_id_seq to service_role;

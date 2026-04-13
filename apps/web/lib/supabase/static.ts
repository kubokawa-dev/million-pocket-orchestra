import { createClient as createSupabaseClient } from "@supabase/supabase-js";

import { requirePublicSupabaseConfig } from "@/lib/env";

/**
 * Cookie 不要の Supabase クライアント。
 * ISR / revalidate と互換性があり、公開データの読み取り専用。
 */
export function createStaticClient() {
  const { url, anonKey } = requirePublicSupabaseConfig();
  return createSupabaseClient(url, anonKey);
}

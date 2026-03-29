import { createClient } from "@supabase/supabase-js";

import { requireAdminSupabaseConfig } from "@/lib/env";

/** Route Handler / Server Action などサーバー限定。RLS をバイパスするので取り扱い注意 */
export function createAdminClient() {
  const { url, serviceRoleKey } = requireAdminSupabaseConfig();
  return createClient(url, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

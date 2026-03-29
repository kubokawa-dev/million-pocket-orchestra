import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

import { resolvePublicSupabaseConfig } from "@/lib/env";

/**
 * Auth セッションの Cookie をリフレッシュする（ローカル・リモートどちらの URL でも同じ）。
 * getUser() を呼ぶまでの間に他処理を挟まないこと（公式推奨）。
 */
export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  let publicConfig: ReturnType<typeof resolvePublicSupabaseConfig>;
  try {
    publicConfig = resolvePublicSupabaseConfig();
  } catch {
    return supabaseResponse;
  }
  if (!publicConfig) {
    return supabaseResponse;
  }

  const { url, anonKey } = publicConfig;

  const supabase = createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) =>
          request.cookies.set(name, value),
        );
        supabaseResponse = NextResponse.next({
          request,
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          supabaseResponse.cookies.set(name, value, options),
        );
      },
    },
  });

  await supabase.auth.getUser();

  return supabaseResponse;
}

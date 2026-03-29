import { z } from "zod";

/** `process.env` の値を trim し、未定義は空文字に正規化 */
const trimmedString = z.preprocess(
  (v: unknown) => (typeof v === "string" ? v.trim() : ""),
  z.string(),
);

const rawEnvSchema = z.object({
  NEXT_PUBLIC_SUPABASE_URL: trimmedString,
  NEXT_PUBLIC_SUPABASE_ANON_KEY: trimmedString,
  SUPABASE_SERVICE_ROLE_KEY: trimmedString,
});

const publicSupabaseSchema = z.object({
  url: z.string().url("NEXT_PUBLIC_SUPABASE_URL は有効な URL である必要があります"),
  anonKey: z
    .string()
    .min(1, "NEXT_PUBLIC_SUPABASE_ANON_KEY を空にできません"),
});

const adminSupabaseSchema = z.object({
  url: z.string().url("NEXT_PUBLIC_SUPABASE_URL は有効な URL である必要があります"),
  serviceRoleKey: z
    .string()
    .min(1, "SUPABASE_SERVICE_ROLE_KEY を空にできません"),
});

type RawEnv = z.infer<typeof rawEnvSchema>;

let cachedRaw: RawEnv | undefined;

function getRawEnv(): RawEnv {
  if (cachedRaw === undefined) {
    const parsed = rawEnvSchema.safeParse({
      NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
      NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY,
    });
    if (!parsed.success) {
      throw new Error(
        `環境変数の読み取りに失敗しました: ${parsed.error.issues.map((i) => i.message).join("; ")}`,
      );
    }
    cachedRaw = parsed.data;
  }
  return cachedRaw;
}

/**
 * URL と anon の両方が空なら null。どちらか一方だけ設定されている場合は Zod で検証エラー。
 * ミドルウェア等で Supabase 未設定を許容するときに使う。
 */
export function resolvePublicSupabaseConfig(): {
  url: string;
  anonKey: string;
} | null {
  const r = getRawEnv();
  if (!r.NEXT_PUBLIC_SUPABASE_URL && !r.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return null;
  }
  const ok = publicSupabaseSchema.safeParse({
    url: r.NEXT_PUBLIC_SUPABASE_URL,
    anonKey: r.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  });
  if (!ok.success) {
    const msg = ok.error.issues.map((e) => e.message).join("; ");
    throw new Error(
      `Supabase の公開用環境変数が不足しているか不正です: ${msg}`,
    );
  }
  return ok.data;
}

/** 公開用 URL / anon が揃っていない場合は例外 */
export function requirePublicSupabaseConfig(): {
  url: string;
  anonKey: string;
} {
  const c = resolvePublicSupabaseConfig();
  if (!c) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL または NEXT_PUBLIC_SUPABASE_ANON_KEY が未設定です",
    );
  }
  return c;
}

/** 管理クライアント用（service_role）。未設定や URL 不正なら例外 */
export function requireAdminSupabaseConfig(): {
  url: string;
  serviceRoleKey: string;
} {
  const r = getRawEnv();
  const ok = adminSupabaseSchema.safeParse({
    url: r.NEXT_PUBLIC_SUPABASE_URL,
    serviceRoleKey: r.SUPABASE_SERVICE_ROLE_KEY,
  });
  if (!ok.success) {
    const msg = ok.error.issues.map((e) => e.message).join("; ");
    throw new Error(
      `Supabase 管理用の環境変数が不足しているか不正です: ${msg}`,
    );
  }
  return ok.data;
}

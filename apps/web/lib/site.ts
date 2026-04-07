const DEFAULT_SITE_ORIGIN = "https://takarakuji-ai.space";

/**
 * 正規URL（OG・sitemap・canonical）。本番は `NEXT_PUBLIC_SITE_URL` で上書き可能。
 */
export function getSiteOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (!raw) return DEFAULT_SITE_ORIGIN;
  try {
    return new URL(raw).origin;
  } catch {
    return DEFAULT_SITE_ORIGIN;
  }
}

export function absoluteUrl(path: string): string {
  const origin = getSiteOrigin();
  if (!path || path === "/") return origin;
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${origin}${p}`;
}

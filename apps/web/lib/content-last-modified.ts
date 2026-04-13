import { blogPosts } from "@/lib/blog/posts";
import { blogPostsEn } from "@/lib/blog/posts-en";
import { resolvePublicSupabaseConfig } from "@/lib/env";
import { numbers4DrawDateToIsoDate } from "@/lib/numbers4-draw-page-seo";
import { createStaticClient } from "@/lib/supabase/static";

/** ブログ記事の最新更新日（公開日ベース） */
export function getLatestBlogLastModified(): Date {
  const dates = [
    ...blogPosts.map((p) => new Date(p.publishedAt).getTime()),
    ...blogPostsEn.map((p) => new Date(p.publishedAt).getTime()),
  ];
  const t = Math.max(0, ...dates);
  return new Date(t);
}

/** Supabase の最新抽選行の日付（無ければ null） */
export async function getLatestNumbers4DrawLastModified(): Promise<Date | null> {
  try {
    let hasConfig = false;
    try {
      hasConfig = resolvePublicSupabaseConfig() !== null;
    } catch {
      return null;
    }
    if (!hasConfig) return null;
    const supabase = createStaticClient();
    const { data, error } = await supabase
      .from("numbers4_draws")
      .select("draw_date")
      .order("draw_number", { ascending: false })
      .limit(1)
      .maybeSingle();
    if (error || data?.draw_date == null) return null;
    const iso = numbers4DrawDateToIsoDate(String(data.draw_date));
    return iso ? new Date(`${iso}T12:00:00.000Z`) : null;
  } catch {
    return null;
  }
}

/** サイトハブ系ページの sitemap lastmod 用（ブログと抽選データの新しい方） */
export async function resolveSiteHubLastModified(
  fallback: Date,
): Promise<Date> {
  const blogMod = getLatestBlogLastModified();
  const drawMod = await getLatestNumbers4DrawLastModified();
  const t = Math.max(
    fallback.getTime(),
    blogMod.getTime(),
    drawMod?.getTime() ?? 0,
  );
  return new Date(t);
}

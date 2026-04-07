import type { MetadataRoute } from "next";

import { blogPosts } from "@/lib/blog/posts";
import { numbers4DrawDateToIsoDate } from "@/lib/numbers4-draw-page-seo";
import { resolvePublicSupabaseConfig } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";
import { getSiteOrigin } from "@/lib/site";

const STATIC_PATHS: {
  path: string;
  changeFrequency: NonNullable<MetadataRoute.Sitemap[number]["changeFrequency"]>;
  priority: number;
}[] = [
    { path: "", changeFrequency: "weekly", priority: 1 },
    { path: "/numbers4", changeFrequency: "daily", priority: 0.95 },
    { path: "/numbers4/result", changeFrequency: "daily", priority: 0.9 },
    { path: "/numbers4/stats", changeFrequency: "daily", priority: 0.85 },
    { path: "/numbers4/trend", changeFrequency: "daily", priority: 0.85 },
    { path: "/blog", changeFrequency: "weekly", priority: 0.75 },
    { path: "/faq", changeFrequency: "monthly", priority: 0.7 },
  ];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const origin = getSiteOrigin();
  const lastModified = new Date();

  const entries: MetadataRoute.Sitemap = STATIC_PATHS.map(
    ({ path, changeFrequency, priority }) => ({
      url: path === "" ? origin : `${origin}${path}`,
      lastModified,
      changeFrequency,
      priority,
    }),
  );

  for (const post of blogPosts) {
    entries.push({
      url: `${origin}/blog/${post.slug}`,
      lastModified: new Date(post.publishedAt),
      changeFrequency: "monthly",
      priority: 0.65,
    });
  }

  let hasSupabase = false;
  try {
    hasSupabase = resolvePublicSupabaseConfig() !== null;
  } catch {
    return entries;
  }

  if (!hasSupabase) return entries;

  try {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from("numbers4_draws")
      .select("draw_number, draw_date")
      .order("draw_number", { ascending: false });

    if (error || !data?.length) return entries;

    for (const row of data) {
      const iso = numbers4DrawDateToIsoDate(
        row.draw_date != null ? String(row.draw_date) : undefined,
      );
      entries.push({
        url: `${origin}/numbers4/result/${row.draw_number}`,
        lastModified: iso ? new Date(`${iso}T12:00:00.000Z`) : lastModified,
        changeFrequency: "weekly",
        priority: 0.55,
      });
    }
  } catch {
    // ビルド時に Supabase 未接続などの場合は静的URLのみ
  }

  return entries;
}

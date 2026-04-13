import type { MetadataRoute } from "next";

import { blogPosts } from "@/lib/blog/posts";
import { blogPostsEn } from "@/lib/blog/posts-en";
import {
  getLatestBlogLastModified,
  resolveSiteHubLastModified,
} from "@/lib/content-last-modified";
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
  { path: "/numbers3", changeFrequency: "daily", priority: 0.94 },
  { path: "/numbers3/result", changeFrequency: "daily", priority: 0.89 },
    { path: "/numbers4", changeFrequency: "daily", priority: 0.95 },
    { path: "/numbers4/result", changeFrequency: "daily", priority: 0.9 },
  { path: "/loto6", changeFrequency: "daily", priority: 0.9 },
  { path: "/loto6/result", changeFrequency: "daily", priority: 0.88 },
  { path: "/loto6/stats", changeFrequency: "daily", priority: 0.82 },
    { path: "/numbers4/stats", changeFrequency: "daily", priority: 0.85 },
    { path: "/numbers4/trend", changeFrequency: "daily", priority: 0.85 },
    { path: "/investors", changeFrequency: "monthly", priority: 0.74 },
    { path: "/blog", changeFrequency: "weekly", priority: 0.75 },
    { path: "/faq", changeFrequency: "monthly", priority: 0.7 },
    { path: "/responsible-use", changeFrequency: "monthly", priority: 0.68 },
    { path: "/terms", changeFrequency: "monthly", priority: 0.66 },
    { path: "/data-sources", changeFrequency: "monthly", priority: 0.62 },
    { path: "/en", changeFrequency: "monthly", priority: 0.88 },
    { path: "/en/blog", changeFrequency: "weekly", priority: 0.82 },
    { path: "/zh", changeFrequency: "monthly", priority: 0.85 },
    { path: "/ko", changeFrequency: "monthly", priority: 0.85 },
    { path: "/es", changeFrequency: "monthly", priority: 0.85 },
    { path: "/hi", changeFrequency: "monthly", priority: 0.85 },
    { path: "/ar", changeFrequency: "monthly", priority: 0.85 },
  ];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const origin = getSiteOrigin();
  const lastModified = new Date();
  const blogLastMod = getLatestBlogLastModified();
  const hubLastMod = await resolveSiteHubLastModified(lastModified);

  // Pages that have multilingual alternates
  const allLangAlternates: Record<string, string> = {
    ja: origin,
    en: `${origin}/en`,
    zh: `${origin}/zh`,
    ko: `${origin}/ko`,
    es: `${origin}/es`,
    hi: `${origin}/hi`,
    ar: `${origin}/ar`,
  };

  const hreflangMap: Record<string, Record<string, string>> = {
    "": allLangAlternates,
    "/en": allLangAlternates,
    "/zh": allLangAlternates,
    "/ko": allLangAlternates,
    "/es": allLangAlternates,
    "/hi": allLangAlternates,
    "/ar": allLangAlternates,
    "/blog": {
      ja: `${origin}/blog`,
      en: `${origin}/en/blog`,
    },
    "/en/blog": {
      ja: `${origin}/blog`,
      en: `${origin}/en/blog`,
    },
  };

  const entries: MetadataRoute.Sitemap = STATIC_PATHS.map(
    ({ path, changeFrequency, priority }) => {
      const isBlogIndex = path === "/blog" || path === "/en/blog";
      const lastMod = isBlogIndex ? blogLastMod : hubLastMod;
      return {
        url: path === "" ? origin : `${origin}${path}`,
        lastModified: lastMod,
        changeFrequency,
        priority,
        ...(hreflangMap[path]
          ? { alternates: { languages: hreflangMap[path] } }
          : {}),
      };
    },
  );

  for (const post of blogPosts) {
    entries.push({
      url: `${origin}/blog/${post.slug}`,
      lastModified: new Date(post.publishedAt),
      changeFrequency: "monthly",
      priority: 0.65,
    });
  }

  for (const post of blogPostsEn) {
    entries.push({
      url: `${origin}/en/blog/${post.slug}`,
      lastModified: new Date(post.publishedAt),
      changeFrequency: "monthly",
      priority: 0.7,
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
    const { data: n3Data, error: n3Error } = await supabase
      .from("numbers3_draws")
      .select("draw_number, draw_date")
      .order("draw_number", { ascending: false });

    if (!n3Error && n3Data?.length) {
      for (const row of n3Data) {
        const n3Date = row.draw_date != null ? String(row.draw_date) : "";
        const n3Iso = /^\d{4}\/\d{2}\/\d{2}$/.test(n3Date)
          ? n3Date.replaceAll("/", "-")
          : n3Date;
        entries.push({
          url: `${origin}/numbers3/result/${row.draw_number}`,
          lastModified: n3Iso ? new Date(`${n3Iso}T12:00:00.000Z`) : lastModified,
          changeFrequency: "weekly",
          priority: 0.54,
        });
      }
    }

    const { data, error } = await supabase
      .from("numbers4_draws")
      .select("draw_number, draw_date")
      .order("draw_number", { ascending: false });

    if (!error && data?.length) {
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
    }

    const { data: l6Data, error: l6Error } = await supabase
      .from("loto6_draws")
      .select("draw_number, draw_date")
      .order("draw_number", { ascending: false });

    if (!l6Error && l6Data?.length) {
      for (const row of l6Data) {
        const d = row.draw_date != null ? String(row.draw_date) : "";
        const l6Iso = /^\d{4}\/\d{2}\/\d{2}$/.test(d)
          ? d.replaceAll("/", "-")
          : d;
        entries.push({
          url: `${origin}/loto6/result/${row.draw_number}`,
          lastModified: l6Iso ? new Date(`${l6Iso}T12:00:00.000Z`) : lastModified,
          changeFrequency: "weekly",
          priority: 0.52,
        });
      }
    }
  } catch {
    // ビルド時に Supabase 未接続などの場合は静的URLのみ
  }

  return entries;
}

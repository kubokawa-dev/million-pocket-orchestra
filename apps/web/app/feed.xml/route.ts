import { blogPosts } from "@/lib/blog/posts";
import { blogPostsEn } from "@/lib/blog/posts-en";
import { getSiteOrigin } from "@/lib/site";

export function GET() {
  const origin = getSiteOrigin();
  const allPosts = [
    ...blogPosts.map((p) => ({ ...p, lang: "ja", urlPrefix: "/blog" })),
    ...blogPostsEn.map((p) => ({ ...p, lang: "en", urlPrefix: "/en/blog" })),
  ].sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));

  const latestDate = allPosts[0]?.publishedAt ?? new Date().toISOString().slice(0, 10);

  const items = allPosts
    .map(
      (post) => `    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${origin}${post.urlPrefix}/${post.slug}</link>
      <guid isPermaLink="true">${origin}${post.urlPrefix}/${post.slug}</guid>
      <description><![CDATA[${post.description}]]></description>
      <pubDate>${new Date(post.publishedAt).toUTCString()}</pubDate>
      <dc:language>${post.lang}</dc:language>
    </item>`,
    )
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>宝くじAI / Takarakuji AI</title>
    <link>${origin}</link>
    <description>ナンバーズ4の当選番号・予測・統計に関するブログ記事。Numbers4 results, predictions, and statistics blog.</description>
    <language>ja</language>
    <lastBuildDate>${new Date(latestDate).toUTCString()}</lastBuildDate>
    <atom:link href="${origin}/feed.xml" rel="self" type="application/rss+xml"/>
${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

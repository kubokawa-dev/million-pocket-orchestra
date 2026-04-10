export type BlogPostEn = {
  slug: string;
  title: string;
  description: string;
  publishedAt: string;
  bodyMarkdown: string;
};

export const blogPostsEn: BlogPostEn[] = [
  {
    slug: "what-is-numbers4-japan",
    title: "What is Numbers4? A short guide for international readers",
    description:
      "Japan’s Numbers4 game in plain English: how draws work, what you see on this site, and how it differs from official sources.",
    publishedAt: "2026-04-07",
    bodyMarkdown: `
## What is Numbers4?

**Numbers4** (ナンバーズ4) is a numbers-style lottery game in Japan. Players pick a four-digit number (0000–9999). Draws produce winning numbers and prize tiers published by the official operator. Rules, cut-off times, and payouts are defined by the official game; **always confirm details on official channels** before buying a ticket.

## What Takarakuji AI shows

This site is an **unofficial** dashboard. It helps you:

- Browse **past winning numbers** in a table (\`/numbers4/result\`).
- Open **per-draw pages** that combine results with **model predictions** (for transparency and research).
- Explore **aggregate statistics** (\`/numbers4/stats\`) and **short-term model trends** (\`/numbers4/trend\`).

The primary UI is **Japanese**, but the data is numeric and structured, so many screens are usable with translation tools.

## Official vs. this site

| Topic | Official sources | This site |
| --- | --- | --- |
| Authority | Lottery operator / bank channels | None (fan / analytics project) |
| Results | Legally binding | Synced from public data; verify officially |
| Predictions | Not provided here as “official” | Experimental models only |

## Responsible use

Predictions are **not** guarantees. The site does **not** encourage gambling. Use predictions as **research or entertainment**, not as financial advice.

## Next reads

- [Where to verify official results](/en/blog/where-to-verify-official-numbers4-results)
- [How to read the results list](/en/blog/how-to-read-the-results-list)
- [Predictions, stats, and trend pages](/en/blog/predictions-stats-and-trend-pages)
`.trim(),
  },
  {
    slug: "how-to-read-the-results-list",
    title: "How to read the Numbers4 results list on Takarakuji AI",
    description:
      "Navigate the results index, pagination, per-draw prediction hubs, and mobile-friendly tables—explained in English.",
    publishedAt: "2026-04-07",
    bodyMarkdown: `
## Open the results index

Go to **\`/numbers4/result\`** (from the Numbers4 hub or the site navigation). You will see a **table of past draws** with winning numbers and related fields that we import from public results.

## Pagination and latest draw

The list may be **paginated**. Use the on-screen controls to move backward in time. The latest draw is also highlighted from the Numbers4 landing page (\`/numbers4\`).

## Per-draw prediction hub

From a row, open the **draw detail** view. After official numbers are ingested, the page can show **daily predictions** (ensemble, per-method, budget tiers, etc.) alongside the result. This is meant for **comparison and learning**, not for claiming edge in the game.

## Mobile layout

Wide tables support **horizontal scrolling** so you can see every column on a phone without squashing digits.

## Double-check on official sites

Before acting on any number, confirm it on the operator’s pages. See [where to verify official Numbers4 results](/en/blog/where-to-verify-official-numbers4-results).

## Disclaimer

This site **does not promote** buying lottery tickets. Content is informational. Official results and rules always win if there is any mismatch.
`.trim(),
  },
  {
    slug: "predictions-stats-and-trend-pages",
    title: "Predictions dashboard, stats, and trend pages—what they mean",
    description:
      "How the per-draw dashboard, box-rank statistics, and Hot Model trend view differ—and how to interpret them carefully.",
    publishedAt: "2026-04-07",
    bodyMarkdown: `
## Three pillars of the Numbers4 zone

1. **Per-draw dashboard** — Everything about **one** draw: multiple models, ensemble, and (when available) match highlights against the official number.  
2. **Stats** (\`/numbers4/stats\`) — Aggregates **where** winning box combinations appeared inside each model’s ranked list over a recent window.  
3. **Trend** (\`/numbers4/trend\`) — Surfaces models that look comparatively strong **recently**, based on the same imported data.

## Predictions dashboard

You will see outputs from different approaches (machine learning, frequency-style heuristics, pattern-style methods, etc.). The **ensemble** blends multiple models; comparing it to individuals helps you understand **dispersion**, not “which model is magic.”

## Stats page—how to read it

We summarize **box matches** and their **ranks** inside prediction lists. This is **descriptive**: it tells you how past draws lined up with past lists. It is **not** a promise of future performance. Lottery outcomes are high-variance by nature.

## Trend page—how to read it

Trends use a **short rolling window**. A model can look hot or cold due to **random swings**. Treat trends as a **compass for exploration**, not a betting system.

## Data pipeline

Predictions come from scheduled jobs (JSON). Official draw results are synced into this site before display. There can be short delays between the official announcement and on-screen updates.

## Summary workflow

1. **Results list** — track history.  
2. **Per-draw page** — inspect predictions for a single draw.  
3. **Stats / trend** — compare models with healthy skepticism.  

Happy exploring—and remember to verify anything important with **official** sources.

## Verify payouts and numbers officially

For authoritative results (not this dashboard), follow [where to verify official Numbers4 results](/en/blog/where-to-verify-official-numbers4-results).
`.trim(),
  },
  {
    slug: "where-to-verify-official-numbers4-results",
    title: "Where to verify official Numbers4 results (Japan)",
    description:
      "Authoritative winning numbers and rules live on Mizuho Bank and the official takarakuji portal—not on Takarakuji AI. Short checklist for international readers.",
    publishedAt: "2026-04-08",
    bodyMarkdown: `
## Why verify officially?

Takarakuji AI mirrors **public draw data** for convenience. Only **official channels** decide whether a ticket wins, how prizes are paid, and the final published numbers for Japan’s authorized lottery products.

## Primary official sources

Use pages on **official domains** only. Avoid copycat or unofficial “mirror” sites if the domain looks wrong.

1. **Mizuho Bank — Numbers4 winning numbers (Japanese UI)**  
   [mizuhobank.co.jp — Numbers4 check](https://www.mizuhobank.co.jp/takarakuji/check/numbers/numbers4/index.html)

2. **Official takarakuji portal — winning-number hub (Japanese UI)**  
   [takarakuji-official.jp — check corner](https://www.takarakuji-official.jp/check/)

If a bookmark breaks, open the bank’s or portal’s **top page** and navigate to “当せん番号” / Numbers4 from there instead of trusting third-party links alone.

## How Takarakuji AI fits in

- We **do not** process claims or payouts.  
- There can be a **short delay** between the official announcement and on-site updates.  
- If any value disagrees, **the official site wins**.

## Language note

Most official flows are in **Japanese**. Browser translation helps, but for tickets, taxes, or disputes, rely on **official Japanese text** or ask an **authorized retailer** in Japan.

## Not legal advice

Rules and URLs can change. This post is **informational** for readers trying to find the right front door—not a substitute for official terms.

## Related guides

- [What is Numbers4?](/en/blog/what-is-numbers4-japan)
- [How to read the results list on this site](/en/blog/how-to-read-the-results-list)
`.trim(),
  },
];

export function getAllEnBlogSlugs(): string[] {
  return blogPostsEn.map((p) => p.slug);
}

export function getEnPostBySlug(slug: string): BlogPostEn | undefined {
  return blogPostsEn.find((p) => p.slug === slug);
}

export function getEnPostsSortedByDate(): BlogPostEn[] {
  return [...blogPostsEn].sort((a, b) =>
    b.publishedAt.localeCompare(a.publishedAt),
  );
}

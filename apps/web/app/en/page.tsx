import type { Metadata } from "next";
import Link from "next/link";

import { HomeLanding } from "@/components/home-landing";
import { buttonVariants } from "@/components/ui/button-variants";
import { getEnPostsSortedByDate } from "@/lib/blog/posts-en";
import { homeLandingCopyEn } from "@/lib/home-landing-copy";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { cn } from "@/lib/utils";

const enFaq = [
  {
    question: "What is Takarakuji AI?",
    answer:
      "An unofficial web app focused on Japan’s Numbers4 lottery: browse official draw results, explore statistics and trends, and compare multiple daily prediction models. The in-app UI is mostly Japanese; this English landing helps international visitors and launch traffic (e.g. Product Hunt) get oriented quickly.",
  },
  {
    question: "Is this official or affiliated with the lottery?",
    answer:
      "No. It is not affiliated with Mizuho Bank, the Japan Lottery, or any operator. Always verify results with official sources before relying on them.",
  },
  {
    question: "Do predictions guarantee wins?",
    answer:
      "No. Predictions are experimental and based on public historical data. They are for research and entertainment only, not financial or gambling advice.",
  },
  {
    question: "Where can I see winning numbers?",
    answer:
      "Use the results indexes at /numbers3/result, /numbers4/result, and /loto6/result (plus per-draw pages linked from each hub). Primary UI labels are in Japanese.",
  },
] as const;

const pageDescription =
  "Unofficial Numbers4 (Japan) dashboard: winning numbers, multi-model daily predictions, stats, and trends — English landing; most app screens are in Japanese.";

export const metadata: Metadata = {
  title: "Takarakuji AI — Numbers4 dashboard (English)",
  description: pageDescription,
  keywords: [
    "Takarakuji AI",
    "Takarakuji",
    "Numbers4",
    "Numbers 4",
    "Japan lottery",
    "Japanese lottery",
    "lottery results",
    "winning numbers",
    "draw results",
    "lottery statistics",
    "prediction models",
    "machine learning lottery",
    "unofficial lottery dashboard",
    "verify official results",
    "ナンバーズ4",
    "宝くじ",
  ],
  alternates: {
    canonical: "/en",
    languages: {
      ja: absoluteUrl("/"),
      en: absoluteUrl("/en"),
      zh: absoluteUrl("/zh"),
      ko: absoluteUrl("/ko"),
      es: absoluteUrl("/es"),
      hi: absoluteUrl("/hi"),
      ar: absoluteUrl("/ar"),
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: ["ja_JP", "ar_SA"],
    url: absoluteUrl("/en"),
    title: "Takarakuji AI — Numbers4 results, models & trends",
    description:
      "Unofficial Numbers4 hub for Japan: draws, analytics, and multiple prediction models in one dashboard. Not affiliated with any lottery operator.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Takarakuji AI — Numbers4",
    description: pageDescription,
  },
};

export default function EnglishOverviewPage() {
  const origin = getSiteOrigin();
  const enPosts = getEnPostsSortedByDate();
  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "en",
    mainEntity: enFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/en#webpage`,
    url: `${origin}/en`,
    name: "Takarakuji AI — English home",
    description: pageDescription,
    inLanguage: "en",
    isPartOf: { "@id": `${origin}/#website` },
    about: {
      "@type": "Thing",
      name: "Numbers4",
      description:
        "A numbers-style lottery game in Japan (four digits). This site is unofficial.",
    },
  };

  return (
    <div lang="en" className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }}
      />
      <HomeLanding copy={homeLandingCopyEn} />

      <section className="border-border/60 mx-auto w-full max-w-2xl border-t px-4 py-14 sm:px-6">
        <h2 className="text-foreground font-heading text-lg font-semibold">
          English guides (blog)
        </h2>
        <p className="text-muted-foreground mt-2 text-sm leading-relaxed sm:text-base">
          Longer explainers for international readers and search/LLM context.{" "}
          <Link
            href="/en/blog"
            className="text-primary font-medium underline-offset-4 hover:underline"
          >
            All English articles →
          </Link>
        </p>
        <ul className="text-muted-foreground mt-4 list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
          {enPosts.map((post) => (
            <li key={post.slug}>
              <Link
                href={`/en/blog/${post.slug}`}
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                {post.title}
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="mx-auto w-full max-w-2xl px-4 pb-20 sm:px-6">
        <h2 className="text-foreground font-heading text-lg font-semibold">FAQ</h2>
        <div className="mt-4 space-y-6">
          {enFaq.map((item) => (
            <div key={item.question} className="space-y-2">
              <h3 className="text-foreground text-base font-medium">
                {item.question}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
                {item.answer}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-10">
          <Link
            href="/numbers4"
            className={cn(
              buttonVariants({ size: "lg" }),
              "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500",
            )}
          >
            Open Numbers4 hub
          </Link>
        </div>
      </section>
    </div>
  );
}

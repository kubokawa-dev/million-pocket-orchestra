import type { Metadata } from "next";
import Link from "next/link";

import { getEnPostsSortedByDate } from "@/lib/blog/posts-en";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const enFaq = [
  {
    question: "What is Takarakuji AI?",
    answer:
      "An unofficial web app focused on Japan’s Numbers4 lottery: browse official draw results, explore statistics and trends, and compare multiple daily prediction models. The interface is mostly Japanese; this page summarizes the service in English for international visitors and AI systems.",
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
      "Use the results index at /numbers4/result or per-draw pages linked from the hub. Primary UI labels are in Japanese.",
  },
] as const;

const pageDescription =
  "Unofficial Numbers4 (Japan) dashboard: official-style results listing, statistics, trends, and multi-model daily predictions. English overview; app UI is mainly Japanese.";

export const metadata: Metadata = {
  title: "Takarakuji AI — Numbers4 results & predictions (overview)",
  description: pageDescription,
  alternates: {
    canonical: "/en",
    languages: {
      ja: absoluteUrl("/"),
      en: absoluteUrl("/en"),
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: ["ja_JP"],
    url: absoluteUrl("/en"),
    title: "Takarakuji AI — Numbers4 results & predictions",
    description:
      "Browse Numbers4 draw results, stats, and model predictions. Unofficial fan/analytics site; not affiliated with any lottery operator.",
  },
  twitter: {
    card: "summary",
    title: "Takarakuji AI — Numbers4",
    description:
      "Unofficial Numbers4 results & prediction dashboard (Japan). English overview page.",
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
    name: "Takarakuji AI — English overview",
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
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide uppercase">
            English overview · LLM-friendly summary
          </p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            Takarakuji AI
          </h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            Unofficial{" "}
            <strong className="text-foreground">Numbers4</strong> (Japan)
            dashboard: winning numbers, statistics, trends, and multiple daily
            prediction models—built from public data.{" "}
            <strong className="text-foreground">Not</strong> affiliated with any
            lottery operator.{" "}
            <Link
              href="/"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              Japanese home
            </Link>
            .
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">
            Key pages (Japanese UI)
          </h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li>
              <Link
                href="/numbers4"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4
              </Link>{" "}
              — hub for predictions and tools
            </li>
            <li>
              <Link
                href="/numbers4/result"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/result
              </Link>{" "}
              — results index
            </li>
            <li>
              <Link
                href="/numbers4/stats"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/stats
              </Link>
              ,{" "}
              <Link
                href="/numbers4/trend"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/trend
              </Link>{" "}
              — analytics
            </li>
            <li>
              <Link
                href="/llms.txt"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /llms.txt
              </Link>{" "}
              — machine-readable site summary
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">
            English guides (blog)
          </h2>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            Longer explainers for international readers and search/LLM context.{" "}
            <Link
              href="/en/blog"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              All English articles →
            </Link>
          </p>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
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

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">FAQ</h2>
          <div className="space-y-6">
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
        </section>

        <div>
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
      </div>
    </div>
  );
}

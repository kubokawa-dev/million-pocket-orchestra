import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRightIcon,
  Globe2Icon,
  LineChartIcon,
  ShieldCheckIcon,
  SparklesIcon,
} from "lucide-react";

import { buttonVariants } from "@/components/ui/button-variants";
import { getEnPostsSortedByDate } from "@/lib/blog/posts-en";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { cn } from "@/lib/utils";

const enFaq = [
  {
    question: "What is Takarakuji AI?",
    answer:
      "An unofficial analytics product rooted in Japan’s number-based lottery ecosystem. It combines draw history, trends, reference model outputs, and multilingual explainers into a calmer, more structured experience than a typical prediction site.",
  },
  {
    question: "Is this official or affiliated with a lottery operator?",
    answer:
      "No. It is not affiliated with Mizuho Bank, the Japan Lottery, or any operator. Official sources should always be used for final verification of results.",
  },
  {
    question: "Do the model outputs guarantee wins?",
    answer:
      "No. They are experimental reference outputs based on public historical data. They are meant for research, entertainment, and information organization, not financial advice or gambling encouragement.",
  },
  {
    question: "Why is this relevant beyond one lottery page?",
    answer:
      "Because the defensible value is not one screen. It is the compounding dataset, the multilingual narrative layer, and the potential to evolve into a premium intelligence property for regulated entertainment categories.",
  },
] as const;

const strategicPoints = [
  {
    icon: Globe2Icon,
    title: "Japan-first, internationally legible",
    body:
      "The product begins with a Japanese market niche, but its presentation now has clear English and Arabic entry points for wider audiences.",
  },
  {
    icon: LineChartIcon,
    title: "Compounding data asset",
    body:
      "Each draw, model run, and historical comparison increases the usefulness of the archive. That makes the product stronger over time.",
  },
  {
    icon: ShieldCheckIcon,
    title: "Trust over hype",
    body:
      "The tone is reference-driven and responsible. That matters if the long-term goal includes premium partnerships, sponsorships, or serious strategic capital.",
  },
] as const;

const nextDoors = [
  {
    href: "/investors",
    title: "Investor brief",
    body: "The premium narrative layer for strategic partners and capital introductions.",
  },
  {
    href: "/ar",
    title: "Arabic strategic entry",
    body: "A Gulf-friendly version of the story for regional sharing and first review.",
  },
  {
    href: "/data-sources",
    title: "Data provenance",
    body: "The credibility checkpoint for visitors evaluating source discipline.",
  },
  {
    href: "/numbers4",
    title: "Flagship dashboard",
    body: "The main live product experience for models, results, and analytics.",
  },
] as const;

const pageDescription =
  "English entry for Takarakuji AI: a Japan-born analytics product for number-based lotteries, presented as a multilingual data and intelligence brand rather than a hype-driven prediction page.";

export const metadata: Metadata = {
  title: "Takarakuji AI — English entry for global visitors",
  description: pageDescription,
  keywords: [
    "Takarakuji AI",
    "Japan lottery analytics",
    "Numbers4",
    "Numbers3",
    "Loto6",
    "multilingual analytics product",
    "reference model outputs",
    "data-driven lottery dashboard",
    "premium intelligence brand",
    "Japanese lottery",
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
    title: "Takarakuji AI — English entry",
    description:
      "A premium English overview for international visitors evaluating Takarakuji AI as a multilingual analytics and data brand.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Takarakuji AI — English entry",
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
    name: "Takarakuji AI — English entry",
    description: pageDescription,
    inLanguage: "en",
    isPartOf: { "@id": `${origin}/#website` },
    about: {
      "@type": "Thing",
      name: "Takarakuji AI",
      description:
        "A multilingual analytics brand rooted in Japan’s number-based lottery data.",
    },
  };

  return (
    <div lang="en" className="flex flex-1 flex-col bg-[#f6f2e8]">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }}
      />

      <section className="px-4 pt-10 pb-8 sm:px-6 sm:pt-14 sm:pb-10">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-[2rem] border border-[#d7c8ac] bg-[linear-gradient(135deg,rgba(255,250,239,0.96),rgba(245,236,219,0.92)_52%,rgba(233,225,207,0.96)_100%)] shadow-[0_18px_60px_rgba(84,68,31,0.12)]">
          <div className="grid gap-8 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-10">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#b6914b]/25 bg-[#fffaf0] px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[#8a6b2f]">
                <SparklesIcon className="size-3.5" />
                English Brand Entry
              </div>
              <div className="space-y-4">
                <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
                  Takarakuji AI / International Overview
                </p>
                <h1 className="font-heading text-3xl font-semibold leading-tight tracking-tight text-[#21190f] sm:text-4xl lg:text-5xl">
                  A Japan-born analytics product reframed as a multilingual data
                  and intelligence brand.
                </h1>
                <p className="max-w-2xl text-sm leading-8 text-[#4d3d27] sm:text-base">
                  This page is the clean English entry for international visitors,
                  launch traffic, and partner introductions. The goal is not to
                  sound louder. It is to present the product as a disciplined,
                  premium-facing analytics property with room to expand.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link
                  href="/investors"
                  className={cn(
                    buttonVariants({ size: "lg" }),
                    "h-11 rounded-full bg-[#1d3b2f] px-5 text-white shadow-sm hover:bg-[#244a3b]",
                  )}
                >
                  Open investor brief
                  <ArrowRightIcon className="size-4" />
                </Link>
                <Link
                  href="/ar"
                  className={cn(
                    buttonVariants({ variant: "outline", size: "lg" }),
                    "h-11 rounded-full border-[#b6914b]/30 bg-white/70 px-5 text-[#2b2115] hover:bg-white",
                  )}
                >
                  Arabic entry
                </Link>
                <Link
                  href="/numbers4"
                  className={cn(
                    buttonVariants({ variant: "ghost", size: "lg" }),
                    "h-11 rounded-full px-5 text-[#5a4528] hover:bg-white/70 hover:text-[#21190f]",
                  )}
                >
                  Flagship dashboard
                </Link>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
              {[
                { label: "Core market", value: "Japan" },
                { label: "Language entries", value: "7" },
                { label: "Product hubs", value: "3" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-[1.4rem] border border-[#d8c9a8] bg-white/65 px-5 py-4"
                >
                  <p className="text-xs uppercase tracking-[0.18em] text-[#8a7651]">
                    {item.label}
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-[#21190f]">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="mx-auto grid max-w-5xl gap-4 md:grid-cols-3">
          {strategicPoints.map(({ icon: Icon, title, body }) => (
            <div
              key={title}
              className="rounded-[1.5rem] border border-[#dfd3b8] bg-white/70 p-5 shadow-[0_10px_30px_rgba(84,68,31,0.06)]"
            >
              <div className="inline-flex size-10 items-center justify-center rounded-2xl bg-[#f3ead5] text-[#8a6b2f]">
                <Icon className="size-5" />
              </div>
              <h2 className="mt-4 text-lg font-semibold text-[#21190f]">
                {title}
              </h2>
              <p className="mt-3 text-sm leading-7 text-[#5a4528]">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="px-4 py-8 sm:px-6 sm:py-10">
        <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[1.75rem] border border-[#d8c9a8] bg-white/75 p-6 sm:p-8">
            <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
              Why this reads better to serious visitors
            </p>
            <h2 className="mt-3 font-heading text-2xl font-semibold leading-tight text-[#21190f] sm:text-3xl">
              The strongest story is not prediction hype. It is disciplined
              positioning around data, presentation, and trust.
            </h2>
            <div className="mt-5 space-y-4 text-sm leading-8 text-[#4d3d27] sm:text-base">
              <p>
                The public product already shows recurring analytics, structured
                archives, and multilingual discoverability. Reframed properly,
                that becomes more than a niche dashboard. It becomes a
                premium-facing information asset.
              </p>
              <p>
                That framing is more useful for international readers, media
                introductions, and early-stage strategic capital than a
                feature-first landing page.
              </p>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-[#d8c9a8] bg-[#1d3b2f] p-6 text-[#f5ecdb] sm:p-8">
            <p className="text-sm font-medium tracking-[0.18em] text-[#d9c49a]">
              Recommended next doors
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-7 sm:text-base">
              {nextDoors.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="font-semibold text-[#fff7e7] underline-offset-4 hover:underline"
                  >
                    {item.title}
                  </Link>
                  <p className="mt-1 text-[#e4d9c1]">{item.body}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="rounded-[1.75rem] border border-[#dfd3b8] bg-white/75 p-6 sm:p-8">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-[#21190f] sm:text-2xl">
                English guides
              </h2>
              <p className="mt-2 text-sm leading-7 text-[#5a4528] sm:text-base">
                Longer explainers for international context, search visibility,
                and LLM-readable orientation.
              </p>
            </div>
            <Link
              href="/en/blog"
              className="text-sm font-semibold text-[#1d3b2f] underline-offset-4 hover:underline"
            >
              All English articles
            </Link>
          </div>
          <ul className="mt-5 grid gap-3 md:grid-cols-2">
            {enPosts.map((post) => (
              <li
                key={post.slug}
                className="rounded-[1.25rem] border border-[#ece2cb] bg-[#fffdf8] p-4"
              >
                <Link
                  href={`/en/blog/${post.slug}`}
                  className="font-medium text-[#21190f] underline-offset-4 hover:underline"
                >
                  {post.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mx-auto w-full max-w-5xl px-4 py-2 sm:px-6 sm:py-4">
        <div className="rounded-[1.75rem] border border-[#dfd3b8] bg-white/75 p-6 sm:p-8">
          <h2 className="text-xl font-semibold text-[#21190f] sm:text-2xl">FAQ</h2>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            {enFaq.map((item) => (
              <div
                key={item.question}
                className="rounded-[1.25rem] border border-[#ece2cb] bg-[#fffdf8] p-5"
              >
                <h3 className="text-base font-semibold text-[#21190f]">
                  {item.question}
                </h3>
                <p className="mt-2 text-sm leading-7 text-[#5a4528]">
                  {item.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 pt-2 pb-16 sm:px-6 sm:pb-20">
        <div className="mx-auto flex max-w-5xl flex-wrap gap-3 rounded-[1.75rem] border border-[#d6c6a0] bg-[linear-gradient(135deg,rgba(255,250,240,0.96),rgba(244,235,216,0.9))] p-6 sm:items-center sm:justify-between sm:p-8">
          <div className="max-w-2xl">
            <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
              Recommended next move
            </p>
            <h2 className="mt-2 font-heading text-2xl font-semibold text-[#21190f]">
              Move from the narrative layer to either the investor brief, the
              data sources, or the live dashboard.
            </h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/investors"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 rounded-full bg-[#1d3b2f] px-5 text-white shadow-sm hover:bg-[#244a3b]",
              )}
            >
              Investor brief
            </Link>
            <Link
              href="/data-sources"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-11 rounded-full border-[#b6914b]/30 bg-white/70 px-5 text-[#2b2115] hover:bg-white",
              )}
            >
              Data sources
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

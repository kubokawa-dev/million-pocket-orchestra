import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRightIcon,
  Building2Icon,
  GemIcon,
  Globe2Icon,
  LineChartIcon,
  ShieldCheckIcon,
  SparklesIcon,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button-variants";
import { absoluteUrl } from "@/lib/site";
import { cn } from "@/lib/utils";

const investorSignals = [
  { label: "Core market live", value: "Japan" },
  { label: "Product hubs", value: "3" },
  { label: "Language doors", value: "7" },
  { label: "Strategic posture", value: "Lean + multilingual" },
] as const;

const thesisCards = [
  {
    icon: Globe2Icon,
    title: "Japan-first, border-ready",
    body:
      "Built on Japanese lottery data, with English and Arabic entry points already in place for broader discovery.",
  },
  {
    icon: LineChartIcon,
    title: "Data compounding",
    body:
      "Draw history, model outputs, trends, and validation views gain value as they accumulate.",
  },
  {
    icon: ShieldCheckIcon,
    title: "Calm, compliant tone",
    body:
      "Reference analytics and responsible-use framing create more trust than hype-led positioning.",
  },
  {
    icon: GemIcon,
    title: "Premium brand potential",
    body:
      "The opportunity is a premium intelligence layer for regulated entertainment, not a gambling blog.",
  },
] as const;

const roadmapPhases = [
  {
    phase: "Phase 1",
    title: "Own one category deeply",
    body:
      "Deepen the Japan Numbers3, Numbers4, and Loto6 experience with cleaner history, sharper reporting, and better international explainers.",
  },
  {
    phase: "Phase 2",
    title: "Launch the private briefing layer",
    body:
      "Offer curated partner pages, market briefs, and invite-only analytics snapshots.",
  },
  {
    phase: "Phase 3",
    title: "Expand to regional intelligence",
    body:
      "Extend the same infrastructure to additional regulated number-game markets across Asia and the Gulf.",
  },
] as const;

const partnerAngles = [
  "Strategic exposure to a Japan-origin data product with multilingual reach",
  "A compact team model that can compound value before large operational overhead appears",
  "A brand surface that can evolve into premium research, sponsorship, and data partnerships",
] as const;

const nextActions = [
  {
    href: "/ar",
    title: "Arabic strategic entry",
    body: "A Gulf-friendly narrative layer for regional visitors and introductions.",
  },
  {
    href: "/en",
    title: "English public overview",
    body: "A lighter overview for fast sharing, launch traffic, and first-pass review.",
  },
  {
    href: "/data-sources",
    title: "Data provenance",
    body: "The credibility layer for anyone checking source discipline before engaging.",
  },
] as const;

const proofPoints = [
  {
    label: "Language entries live",
    value: "7",
    note: "Japanese plus English, Arabic, Chinese, Korean, Spanish, and Hindi.",
  },
  {
    label: "Core product hubs",
    value: "3",
    note: "Numbers3, Numbers4, and Loto6 each have live public surfaces.",
  },
  {
    label: "Public machine endpoints",
    value: "8+",
    note: "JSON APIs, OpenAPI, RSS, sitemap, oEmbed, llms.txt, and llms-full.txt are already exposed.",
  },
  {
    label: "Schema migrations shipped",
    value: "8",
    note: "The data model is already being maintained as an evolving product, not a static mockup.",
  },
] as const;

const infrastructureRows = [
  "Public JSON endpoints exist for Numbers3, Numbers4, and Loto6 latest-draw access.",
  "OpenAPI 3.1, RSS, sitemap, oEmbed, and LLM-oriented summaries are already part of the surface area.",
  "A dedicated data-sources page explains provenance, verification posture, and machine-readable access.",
] as const;

const fundingUnlocks = [
  {
    title: "Premium partner layer",
    body:
      "Build invite-grade partner pages, curated briefings, and a sharper private narrative.",
  },
  {
    title: "Deeper multilingual expansion",
    body:
      "Turn English and Arabic entry pages into stronger product explanations and acquisition surfaces.",
  },
  {
    title: "Stronger data operations",
    body:
      "Improve ingestion reliability, validation tooling, and historical reporting.",
  },
  {
    title: "Category expansion",
    body:
      "Apply the same infrastructure pattern to more regulated number-game markets.",
  },
] as const;

const deckFlow = [
  {
    eyebrow: "Input",
    title: "Structured public data",
    body:
      "Official-result verification links, stored draw history, recurring model documents, and multilingual context pages.",
  },
  {
    eyebrow: "Engine",
    title: "Presentation and intelligence layer",
    body:
      "Dashboards, trend views, validation pages, machine-readable endpoints, and premium-facing narrative packaging.",
  },
  {
    eyebrow: "Output",
    title: "Compounding brand asset",
    body:
      "A more defensible product: part analytics interface, part data property, part strategic media surface.",
  },
] as const;

const whyNowPoints = [
  "Multilingual discovery matters more now because niche products can travel internationally before they are fully localized.",
  "Machine-readable surfaces such as APIs, OpenAPI, and LLM summaries make small products easier to inspect, cite, and integrate.",
  "Trust is becoming a differentiator. A calmer, reference-driven posture can stand apart from low-credibility prediction noise.",
] as const;

const strategicFitPoints = [
  "Strategic angels or family offices that value brand formation, data assets, and selective market expansion.",
  "Media, sponsorship, or platform partners looking for a premium niche property with international storytelling upside.",
  "Operators or ecosystem partners who understand regulated entertainment and prefer disciplined presentation over hype-led growth.",
] as const;

export const metadata: Metadata = {
  title: "Investors",
  description:
    "Private-brief style overview for strategic partners evaluating Takarakuji AI as a premium predictive entertainment intelligence brand.",
  alternates: {
    canonical: "/investors",
  },
  openGraph: {
    type: "website",
    url: absoluteUrl("/investors"),
    title: "Takarakuji AI | Investor Brief",
    description:
      "A premium overview for strategic partners: positioning, moat, expansion thesis, and multilingual market potential.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function InvestorsPage() {
  const printIssuedOn = "Issued on 2026-04-13";
  const printAudience = "Intended audience: strategic partners, sponsors, and early-stage capital.";
  const printConfidentiality =
    "Confidentiality note: prepared as a private narrative brief for review and discussion.";

  return (
    <div className="investor-deck relative isolate overflow-hidden bg-[#090b08] text-[#f6ecd2]">
      <div
        data-investor-print-hidden
        className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,rgba(185,145,62,0.24),transparent_32%),radial-gradient(circle_at_80%_20%,rgba(16,71,52,0.32),transparent_28%),linear-gradient(180deg,#0b0f0b_0%,#090b08_48%,#111610_100%)]"
      />
      <div
        data-investor-print-hidden
        className="absolute inset-0 -z-10 opacity-30 [background-image:linear-gradient(rgba(246,236,210,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(246,236,210,0.08)_1px,transparent_1px)] [background-size:72px_72px]"
      />

      <section data-investor-section className="px-4 pt-10 pb-8 sm:px-6 sm:pt-16 sm:pb-12">
        <div className="mx-auto max-w-6xl">
          <div className="hidden print:mb-6 print:flex print:flex-col print:gap-2">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-black">
              Takarakuji AI
            </p>
            <h1 className="font-heading text-3xl font-semibold tracking-tight text-black">
              Private Investor Brief
            </h1>
            <p className="text-sm text-black/70">
              Japan-born predictive entertainment intelligence
            </p>
            <p className="text-xs uppercase tracking-[0.18em] text-black/60">
              {printIssuedOn}
            </p>
            <div className="mt-2 border-t border-black/10 pt-3 text-[11px] leading-5 text-black/70">
              <p>{printAudience}</p>
              <p>{printConfidentiality}</p>
            </div>
          </div>
          <div className="overflow-hidden rounded-[2rem] border border-[#c8a45a]/25 bg-[linear-gradient(145deg,rgba(200,164,90,0.14),rgba(8,15,10,0.88)_30%,rgba(8,15,10,0.96)_100%)] shadow-[0_30px_120px_rgba(0,0,0,0.45)]">
            <div className="grid gap-8 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[1.25fr_0.75fr] lg:px-12 lg:py-14">
              <div className="space-y-6">
                <div className="inline-flex items-center gap-2 rounded-full border border-[#d2b272]/30 bg-[#f4d58d]/8 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#f4d58d]">
                  <SparklesIcon className="size-3.5" />
                  Private Investor Brief
                </div>
                <div className="space-y-4">
                  <p className="text-xs font-medium uppercase tracking-[0.28em] text-[#d4c4a2]">
                    Takarakuji AI / Strategic Narrative
                  </p>
                  <h1 className="max-w-3xl font-heading text-4xl font-semibold leading-tight tracking-tight text-[#fff8e7] sm:text-5xl lg:text-6xl">
                    Japan-born predictive entertainment intelligence with a premium
                    face for global capital.
                  </h1>
                  <p className="max-w-2xl text-sm leading-7 text-[#d7ccb3] sm:text-base">
                    The current product already shows multilingual framing,
                    recurring analytics, and brand discipline. The next step is a
                    tighter premium layer that turns the dataset into a strategic asset.
                  </p>
                </div>

                <div data-investor-print-hidden className="flex flex-wrap gap-3">
                  <Link
                    href="/ar"
                    className={cn(
                      buttonVariants({ size: "lg" }),
                      "h-11 rounded-full border border-[#d8b46a]/40 bg-[#d8b46a] px-5 text-[#17140d] hover:bg-[#e7c67a]",
                    )}
                  >
                    Arabic overview
                    <ArrowRightIcon className="size-4" />
                  </Link>
                  <Link
                    href="/en"
                    className={cn(
                      buttonVariants({ variant: "outline", size: "lg" }),
                      "h-11 rounded-full border-[#c8a45a]/35 bg-white/5 px-5 text-[#f6ecd2] hover:bg-white/10 hover:text-[#fff8e7]",
                    )}
                  >
                    English entry
                  </Link>
                  <Link
                    href="/data-sources"
                    className={cn(
                      buttonVariants({ variant: "ghost", size: "lg" }),
                      "h-11 rounded-full px-5 text-[#d7ccb3] hover:bg-white/6 hover:text-[#fff8e7]",
                    )}
                  >
                    Data sources
                  </Link>
                </div>
                <div data-investor-print-hidden className="flex flex-wrap gap-2 pt-2">
                  {[
                    { href: "#proof-points", label: "Proof points" },
                    { href: "#pitch-deck", label: "Mini deck" },
                    { href: "#funding-unlocks", label: "Funding use" },
                    { href: "#decision-support", label: "Next steps" },
                  ].map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-[#d7ccb3] transition-colors hover:bg-white/[0.08] hover:text-[#fff8e7]"
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                {investorSignals.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-[1.5rem] border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-sm"
                  >
                    <p className="text-xs uppercase tracking-[0.22em] text-[#bdae8d]">
                      {item.label}
                    </p>
                    <p className="mt-2 text-2xl font-semibold tracking-tight text-[#fff6de]">
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-2 xl:grid-cols-4">
          {thesisCards.map(({ icon: Icon, title, body }) => (
            <Card
              key={title}
              className="rounded-[1.5rem] border border-white/10 bg-white/[0.045] py-0 text-[#f6ecd2] ring-0"
            >
              <CardHeader className="px-5 pt-5">
                <div className="mb-3 inline-flex size-10 items-center justify-center rounded-2xl border border-[#d7b56c]/30 bg-[#d7b56c]/10 text-[#f2d38b]">
                  <Icon className="size-5" />
                </div>
                <CardTitle className="text-lg text-[#fff8e7]">{title}</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pb-5 text-sm leading-7 text-[#d7ccb3]">
                {body}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="px-4 py-8 sm:px-6 sm:py-12">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[1.75rem] border border-[#c8a45a]/20 bg-[linear-gradient(180deg,rgba(13,20,15,0.92),rgba(12,17,13,0.82))] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Why this can attract premium capital
            </p>
            <h2 className="mt-3 max-w-xl font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              The appeal is not a lucky-number gimmick. It is a disciplined niche
              becoming a defensible media-data property.
            </h2>
            <div className="mt-6 space-y-4 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              <p>
                Strong backers fund assets that can become scarce, trusted, and
                hard to replicate. This product already points that way through
                structured history, recurring model output, multilingual discovery,
                and a calm responsible-use posture.
              </p>
              <p>
                The next layer should package those strengths into premium
                briefings, sponsor-grade presentation, and selective expansion.
              </p>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Gulf-facing narrative
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-7 text-[#e7dcc1] sm:text-base">
              {partnerAngles.map((item) => (
                <li key={item} className="flex gap-3">
                  <Building2Icon className="mt-1 size-4 shrink-0 text-[#d7b56c]" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="px-4 py-8 sm:px-6 sm:py-12">
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.045),rgba(255,255,255,0.02))] p-6 sm:p-8 lg:p-10">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Roadmap for the premium version
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              Build the investor-facing layer without breaking the public product.
            </h2>
          </div>
          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            {roadmapPhases.map((item) => (
              <div
                key={item.phase}
                className="rounded-[1.5rem] border border-white/10 bg-[#0e130f] p-5"
              >
                <p className="text-xs uppercase tracking-[0.24em] text-[#d7b56c]">
                  {item.phase}
                </p>
                <h3 className="mt-3 text-xl font-semibold text-[#fff8e7]">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-[#d7ccb3]">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section
        id="proof-points"
        data-investor-section
        className="px-4 py-8 sm:px-6 sm:py-12 scroll-mt-24"
      >
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-[#0d120e] p-6 sm:p-8 lg:p-10">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Proof points
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              Enough real infrastructure exists already to support a serious narrative.
            </h2>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {proofPoints.map((item) => (
              <div
                key={item.label}
                className="rounded-[1.5rem] border border-white/10 bg-white/[0.04] p-5"
              >
                <p className="text-xs uppercase tracking-[0.22em] text-[#bdae8d]">
                  {item.label}
                </p>
                <p className="mt-3 text-4xl font-semibold tracking-tight text-[#fff8e7]">
                  {item.value}
                </p>
                <p className="mt-3 text-sm leading-7 text-[#d7ccb3]">{item.note}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section
        id="pitch-deck"
        data-investor-section
        className="px-4 py-8 sm:px-6 sm:py-12 scroll-mt-24"
      >
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-[#d7b56c]/18 bg-[linear-gradient(135deg,rgba(215,181,108,0.08),rgba(10,14,11,0.92)_28%,rgba(10,14,11,0.98)_100%)] p-6 sm:p-8 lg:p-10">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Mini pitch deck
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              One-screen summary of how the business can compound.
            </h2>
            <p className="mt-4 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              A concise view of the inputs, the product layer, and the resulting asset.
            </p>
          </div>

          <div className="mt-8 grid gap-4 xl:grid-cols-[1fr_auto_1fr_auto_1fr] xl:items-stretch">
            {deckFlow.map((item, index) => (
              <div key={item.title} className="contents">
                <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.045] p-5">
                  <p className="text-xs uppercase tracking-[0.22em] text-[#d7b56c]">
                    {item.eyebrow}
                  </p>
                  <h3 className="mt-3 text-2xl font-semibold text-[#fff8e7]">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-[#d7ccb3]">
                    {item.body}
                  </p>
                </div>
                {index < deckFlow.length - 1 ? (
                  <div className="hidden items-center justify-center xl:flex">
                    <div className="flex h-full min-h-24 items-center">
                      <div className="flex items-center gap-3 rounded-full border border-[#d7b56c]/18 bg-[#d7b56c]/8 px-4 py-2 text-sm font-medium text-[#f0d89d]">
                        <span>Compounds into</span>
                        <ArrowRightIcon className="size-4" />
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-[1.5rem] border border-[#d7b56c]/16 bg-[#0c110d] p-5">
            <p className="text-sm leading-7 text-[#e3d8bc] sm:text-base">
              The funding story follows this same flow: improve the input quality,
              sharpen the intelligence layer, and let the resulting brand asset
              support better partnerships, stronger international reach, and future
              category expansion.
            </p>
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 py-8 sm:px-6 sm:py-12">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Why now
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              The timing works because small, disciplined products can now look global earlier.
            </h2>
            <ul className="mt-5 space-y-4 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              {whyNowPoints.map((point) => (
                <li key={point} className="flex gap-3">
                  <ArrowRightIcon className="mt-1 size-4 shrink-0 text-[#d7b56c]" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-[1.75rem] border border-[#c8a45a]/20 bg-[linear-gradient(180deg,rgba(13,20,15,0.92),rgba(12,17,13,0.82))] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Founder note
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              The ambition is not to shout louder than the category. It is to build the most legible asset inside it.
            </h2>
            <div className="mt-5 space-y-4 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              <p>
                The current product shows a specific taste: structured information,
                restrained presentation, and enough technical surface to make the
                work inspectable. That taste is part of the asset.
              </p>
              <p>
                If capital joins, it should preserve that discipline while helping
                the product grow into a clearer international brand, not dissolve
                into generic growth theater.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 pt-2 pb-10 sm:px-6 sm:pb-12">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-[1.75rem] border border-[#c8a45a]/20 bg-[linear-gradient(180deg,rgba(13,20,15,0.92),rgba(12,17,13,0.82))] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Deck framing
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              This now reads closer to an early-stage strategic deck than a feature catalog.
            </h2>
            <p className="mt-5 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              The combination of multilingual entries, maintained schemas, public
              machine-readable interfaces, and source-transparency pages gives the
              product enough substance to justify a capital conversation without
              inventing traction that does not exist.
            </p>
          </div>

          <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Infrastructure surface
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-7 text-[#e7dcc1] sm:text-base">
              {infrastructureRows.map((row) => (
                <li key={row} className="flex gap-3">
                  <LineChartIcon className="mt-1 size-4 shrink-0 text-[#d7b56c]" />
                  <span>{row}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 py-8 sm:px-6 sm:py-12">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-[1.75rem] border border-[#c8a45a]/20 bg-[linear-gradient(180deg,rgba(13,20,15,0.92),rgba(12,17,13,0.82))] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Best-fit capital
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              This is a strategic-fit opportunity before it is a broad-process fundraising story.
            </h2>
            <p className="mt-5 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              The best match is aligned capital that understands patient brand
              building, data compounding, and controlled category expansion.
            </p>
          </div>

          <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-6 sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Strategic fit
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-7 text-[#e7dcc1] sm:text-base">
              {strategicFitPoints.map((point) => (
                <li key={point} className="flex gap-3">
                  <Building2Icon className="mt-1 size-4 shrink-0 text-[#d7b56c]" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section
        id="funding-unlocks"
        data-investor-section
        className="px-4 py-8 sm:px-6 sm:py-12 scroll-mt-24"
      >
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.045),rgba(255,255,255,0.02))] p-6 sm:p-8 lg:p-10">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Use of proceeds
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              Capital should accelerate compounding assets, not just add cosmetic growth.
            </h2>
            <p className="mt-4 text-sm leading-7 text-[#d7ccb3] sm:text-base">
              The strongest use of proceeds is selective: deepen the premium
              layer, strengthen data operations, and widen international reach
              without breaking the disciplined tone that makes the product credible.
            </p>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {fundingUnlocks.map((item) => (
              <div
                key={item.title}
                className="rounded-[1.5rem] border border-white/10 bg-[#0e130f] p-5"
              >
                <h3 className="text-xl font-semibold text-[#fff8e7]">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-[#d7ccb3]">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 pt-4 pb-14 sm:px-6 sm:pb-16">
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-[#d7b56c]/20 bg-[linear-gradient(135deg,rgba(215,181,108,0.16),rgba(8,15,10,0.9)_35%,rgba(8,15,10,0.96)_100%)] p-6 sm:p-8 lg:flex lg:items-end lg:justify-between lg:gap-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Recommended next move
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              Present this as a premium intelligence brand, not a prediction toy.
            </h2>
            <p className="mt-4 text-sm leading-7 text-[#e3d8bc] sm:text-base">
              Use this page as the narrative entry point, then guide serious visitors
              to the English and Arabic overviews, data provenance, and the flagship
              dashboard experience.
            </p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3 lg:mt-0 lg:justify-end">
            <Link
              href="/numbers4"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 rounded-full border border-[#d8b46a]/40 bg-[#d8b46a] px-5 text-[#17140d] hover:bg-[#e7c67a]",
              )}
            >
              Open flagship dashboard
            </Link>
            <Link
              href="/ar"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-11 rounded-full border-[#c8a45a]/35 bg-white/5 px-5 text-[#f6ecd2] hover:bg-white/10 hover:text-[#fff8e7]",
              )}
            >
              Show Arabic story
            </Link>
          </div>
        </div>
      </section>

      <section
        id="decision-support"
        data-investor-section
        className="px-4 pb-16 sm:px-6 sm:pb-20 scroll-mt-24"
      >
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-white/[0.045] p-6 sm:p-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Decision support
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              The next click should deepen conviction, not dump visitors back into a generic navigation flow.
            </h2>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {nextActions.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-[1.5rem] border border-white/10 bg-[#0e130f] p-5 transition-colors hover:bg-[#121914]"
              >
                <p className="text-lg font-semibold text-[#fff8e7]">{item.title}</p>
                <p className="mt-3 text-sm leading-7 text-[#d7ccb3]">{item.body}</p>
                <p className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-[#d7b56c]">
                  Open
                  <ArrowRightIcon className="size-4" />
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section data-investor-section className="px-4 pb-16 sm:px-6 sm:pb-20">
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-[#d7b56c]/18 bg-[linear-gradient(135deg,rgba(215,181,108,0.12),rgba(10,14,11,0.92)_35%,rgba(10,14,11,0.98)_100%)] p-6 sm:p-8 lg:flex lg:items-end lg:justify-between lg:gap-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-[#d7b56c]">
              Deck request path
            </p>
            <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-[#fff8e7]">
              Use this page as the briefing layer, then move the conversation by warm introduction.
            </h2>
            <p className="mt-4 text-sm leading-7 text-[#e3d8bc] sm:text-base">
              A public inbox is not exposed here. The intended route is controlled:
              review the brief, validate the data surface, then continue by direct
              introduction or private share.
            </p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3 lg:mt-0 lg:max-w-xl lg:justify-end">
            <Link
              href="/en"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 rounded-full border border-[#d8b46a]/40 bg-[#d8b46a] px-5 text-[#17140d] hover:bg-[#e7c67a]",
              )}
            >
              Share English entry
            </Link>
            <Link
              href="/ar"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-11 rounded-full border-[#c8a45a]/35 bg-white/5 px-5 text-[#f6ecd2] hover:bg-white/10 hover:text-[#fff8e7]",
              )}
            >
              Share Arabic entry
            </Link>
            <Link
              href="/data-sources"
              className={cn(
                buttonVariants({ variant: "ghost", size: "lg" }),
                "h-11 rounded-full px-5 text-[#d7ccb3] hover:bg-white/6 hover:text-[#fff8e7]",
              )}
            >
              Validate data surface
            </Link>
          </div>
        </div>
      </section>

      <section className="hidden print:block print:pt-3">
        <div className="border-t border-black/10 pt-4 text-[11px] leading-5 text-black/70">
          <p>Prepared for:</p>
          <div className="mt-2 h-6 border-b border-black/25" />
          <p className="mt-4">Introduction source / notes:</p>
          <div className="mt-2 h-10 border-b border-black/25" />
          <p className="mt-4">Follow-up owner:</p>
          <div className="mt-2 h-6 border-b border-black/25" />
        </div>
      </section>
    </div>
  );
}

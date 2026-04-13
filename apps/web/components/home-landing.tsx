import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import {
  ArrowRightIcon,
  BarChart3Icon,
  BookOpenIcon,
  CircleDotIcon,
  CircleHelpIcon,
  FlameIcon,
  LayersIcon,
  ListOrderedIcon,
  SparklesIcon,
  ZapIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { HomeLandingCopy, HomeLandingHeroCta } from "@/lib/home-landing-copy";
import { homeLandingCopyJa } from "@/lib/home-landing-copy";
import { cn } from "@/lib/utils";

const featureIconByHref: Record<string, LucideIcon> = {
  "/numbers3/result": ListOrderedIcon,
  "/numbers3": LayersIcon,
  "/numbers4/result": ListOrderedIcon,
  "/numbers4": LayersIcon,
  "/numbers4/stats": BarChart3Icon,
  "/numbers4/trend": FlameIcon,
  "/loto6/result": ListOrderedIcon,
  "/loto6": CircleDotIcon,
  "/loto6/stats": BarChart3Icon,
};

function homeCtaButtonClass(
  cta: HomeLandingHeroCta,
  surface: "hero" | "bottom" = "hero",
): string {
  if (cta.variant === "solid") {
    if (cta.lottery === "numbers4") {
      return cn(
        buttonVariants({ size: "lg" }),
        "gap-2 bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500",
      );
    }
    if (cta.lottery === "loto6") {
      return cn(
        buttonVariants({ size: "lg" }),
        "gap-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-md hover:from-amber-500 hover:to-orange-500",
      );
    }
    return cn(
      buttonVariants({ size: "lg" }),
      "gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md hover:from-emerald-500 hover:to-teal-500",
    );
  }
  const onGradient =
    surface === "bottom"
      ? "border-background/30 bg-background/90 shadow-sm hover:bg-background"
      : "border-border/80 bg-background/60 backdrop-blur-sm hover:bg-background/80";
  if (cta.lottery === "numbers4") {
    return cn(
      buttonVariants({ variant: "outline", size: "lg" }),
      "justify-center ring-violet-500/15 hover:ring-1 dark:ring-violet-400/20",
      onGradient,
    );
  }
  if (cta.lottery === "loto6") {
    return cn(
      buttonVariants({ variant: "outline", size: "lg" }),
      "justify-center ring-amber-500/20 hover:ring-1 dark:ring-amber-400/25",
      onGradient,
    );
  }
  return cn(
    buttonVariants({ variant: "outline", size: "lg" }),
    "justify-center ring-emerald-500/15 hover:ring-1 dark:ring-emerald-400/20",
    onGradient,
  );
}

function HomeCtaLink({
  cta,
  surface = "hero",
}: {
  cta: HomeLandingHeroCta;
  surface?: "hero" | "bottom";
}) {
  const SolidIcon =
    cta.lottery === "numbers4"
      ? ZapIcon
      : cta.lottery === "loto6"
        ? CircleDotIcon
        : SparklesIcon;
  const icon =
    cta.variant === "solid" ? (
      <SolidIcon className="size-4 shrink-0" />
    ) : (
      <ListOrderedIcon className="size-4 shrink-0 opacity-80" />
    );
  return (
    <Link
      href={cta.href}
      className={cn(homeCtaButtonClass(cta, surface), "w-full sm:min-w-0")}
    >
      {icon}
      <span className="text-balance">{cta.label}</span>
      <ArrowRightIcon className="size-4 shrink-0 opacity-90" />
    </Link>
  );
}

type HomeLandingProps = {
  copy?: HomeLandingCopy;
};

export function HomeLanding({ copy = homeLandingCopyJa }: HomeLandingProps) {
  const { hero, pitchLabels, features, story, disclaimer, blogCard, bottomCta } =
    copy;

  return (
    <div className="flex flex-1 flex-col">
      {/* Hero */}
      <section className="relative px-4 pt-12 pb-12 sm:px-6 sm:pt-16 sm:pb-16 lg:pt-20 lg:pb-20">
        <div className="border-border/60 from-card/30 to-background/40 relative mx-auto max-w-3xl rounded-3xl border bg-gradient-to-b px-5 py-12 text-center shadow-sm ring-1 ring-black/5 sm:px-10 sm:py-14 dark:ring-white/10">
          <div className="mb-5 flex flex-wrap items-center justify-center gap-2">
            <Badge className="gap-1 border-0 bg-gradient-to-r from-violet-600 to-cyan-600 px-3 py-1 text-white shadow-sm">
              <SparklesIcon className="size-3.5" />
              {hero.badgeBrand}
            </Badge>
            <Badge variant="secondary" className="font-medium">
              {hero.badgeFocus}
            </Badge>
          </div>
          <h1 className="text-foreground font-heading text-balance text-4xl font-bold tracking-tight sm:text-5xl sm:leading-[1.1] lg:text-[2.75rem]">
            {hero.titleLine1}
            <span
              className={
                hero.titleHighlightClassName ??
                "bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-600 bg-clip-text text-transparent dark:from-violet-400 dark:via-fuchsia-400 dark:to-cyan-400"
              }
            >
              {hero.titleHighlight}
            </span>
            {hero.titleLine2}
            {hero.titleLine3 ? (
              <>
                {hero.titleLineBreakBeforeLine3 ? (
                  <br className="hidden sm:block" />
                ) : null}
                {hero.titleLine3}
              </>
            ) : null}
          </h1>
          <p className="text-muted-foreground mx-auto mt-5 max-w-xl text-pretty text-base leading-relaxed sm:text-lg">
            <strong className="text-foreground font-semibold">{hero.introLead}</strong>
            {hero.introMid}
            {hero.introEmphasis ? (
              <strong className="text-foreground font-semibold">
                {hero.introEmphasis}
              </strong>
            ) : null}
            {hero.introTail}
          </p>
          <div className="mx-auto mt-8 grid max-w-lg grid-cols-1 gap-3 sm:max-w-3xl sm:grid-cols-2 lg:max-w-4xl lg:grid-cols-3">
            {hero.ctas.map((cta) => (
              <HomeCtaLink
                key={`${cta.href}-${cta.variant}`}
                cta={cta}
                surface="hero"
              />
            ))}
          </div>
          <div className="mt-4 flex justify-center">
            <Link
              href="/investors"
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "rounded-full border-amber-500/30 bg-amber-500/8 px-4 text-amber-900 shadow-sm hover:bg-amber-500/14 dark:text-amber-200",
              )}
            >
              <SparklesIcon className="size-3.5" />
              投資家向けブリーフ
              <ArrowRightIcon className="size-3.5" />
            </Link>
          </div>
          <p className="text-muted-foreground mt-8 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs sm:text-sm">
            {hero.languageLinks.map((link, index) => (
              <span key={link.href} className="contents">
                {index > 0 ? (
                  <span className="text-border" aria-hidden>
                    |
                  </span>
                ) : null}
                {link.current ? (
                  <span className="text-foreground font-medium">{link.label}</span>
                ) : (
                  <Link
                    href={link.href}
                    className="text-primary font-medium underline-offset-4 hover:underline"
                  >
                    {link.label}
                  </Link>
                )}
              </span>
            ))}
          </p>
        </div>
      </section>

      {/* Pitch strip */}
      <section className="px-4 pb-10 sm:px-6">
        <div className="mx-auto flex max-w-4xl flex-wrap justify-center gap-2">
          {pitchLabels.map((label) => (
            <span
              key={label}
              className="border-border/70 bg-background/80 text-foreground/85 rounded-full border px-3 py-1 text-xs font-medium shadow-sm backdrop-blur-sm sm:text-sm"
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className="px-4 pb-16 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <div className="mb-8 text-center">
            <h2 className="text-foreground font-heading text-2xl font-bold tracking-tight sm:text-3xl">
              {features.sectionTitle}
            </h2>
            <p className="text-muted-foreground mx-auto mt-2 max-w-2xl text-sm sm:text-base">
              {features.sectionSubtitle}
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {features.cards.map(
              ({ href, title, tag, description, accent }) => {
                const Icon = featureIconByHref[href] ?? ListOrderedIcon;
                return (
                  <Link key={href} href={href} className="group block h-full">
                    <Card
                      className={cn(
                        "border-border/70 h-full overflow-hidden bg-gradient-to-br to-card shadow-sm ring-1 ring-black/5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md dark:ring-white/10",
                        accent,
                      )}
                    >
                      <CardHeader className="pb-2">
                        <div className="mb-2 flex items-center justify-between gap-2">
                          <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-xl">
                            <Icon className="size-5" />
                          </div>
                          <Badge
                            variant="outline"
                            className="text-[0.65rem] font-normal"
                          >
                            {tag}
                          </Badge>
                        </div>
                        <CardTitle className="text-base leading-snug group-hover:underline">
                          {title}
                        </CardTitle>
                        <CardDescription className="text-xs leading-relaxed sm:text-sm">
                          {description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <span className="text-primary inline-flex items-center gap-1 text-xs font-semibold">
                          {features.openPage}
                          <ArrowRightIcon className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                        </span>
                      </CardContent>
                    </Card>
                  </Link>
                );
              },
            )}
          </div>
        </div>
      </section>

      {/* Story + disclaimer */}
      <section className="px-4 pb-16 sm:px-6">
        <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-5 lg:gap-8">
          <Card className="border-border/70 lg:col-span-3 lg:shadow-sm">
            <CardHeader>
              <CardTitle className="font-heading text-lg sm:text-xl">
                {story.title}
              </CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                {story.subtitle}
              </CardDescription>
            </CardHeader>
            <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
              <p>
                {story.p1Lead}
                <strong className="text-foreground">{story.p1Strong1}</strong>
                {story.p1Mid}
                <strong className="text-foreground">{story.p1Strong2}</strong>
                {story.p1Tail}
              </p>
              <p>{story.p2}</p>
            </CardContent>
          </Card>
          <div className="flex flex-col gap-4 lg:col-span-2">
            <Card className="border-border/70 border-dashed bg-muted/20 shadow-none">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <CircleHelpIcon className="text-muted-foreground size-5" />
                  <CardTitle className="text-base">{disclaimer.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="text-muted-foreground space-y-3 text-xs leading-relaxed sm:text-sm">
                <p>
                  {disclaimer.bodyLead}
                  <strong className="text-foreground">{disclaimer.bodyStrong}</strong>
                  {disclaimer.bodyTail}
                </p>
                {disclaimer.detailsLink ? (
                  <p>
                    <Link
                      href={disclaimer.detailsLink.href}
                      className="text-foreground font-medium underline-offset-4 hover:underline"
                    >
                      {disclaimer.detailsLink.label}
                    </Link>
                  </p>
                ) : null}
              </CardContent>
            </Card>
            <Link
              href="/blog"
              className={cn(
                buttonVariants({ variant: "secondary", size: "lg" }),
                "h-auto justify-start gap-3 py-4 text-left shadow-sm",
              )}
            >
              <BookOpenIcon className="size-5 shrink-0" />
              <span>
                <span className="text-foreground block text-sm font-semibold">
                  {blogCard.title}
                </span>
                <span className="text-muted-foreground block text-xs font-normal">
                  {blogCard.subtitle}
                </span>
              </span>
              <ArrowRightIcon className="text-muted-foreground ml-auto size-4 shrink-0" />
            </Link>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="px-4 pb-20 sm:px-6">
        <div className="from-primary/10 via-violet-500/10 to-cyan-500/10 border-primary/20 relative mx-auto max-w-3xl overflow-hidden rounded-3xl border bg-gradient-to-br px-6 py-10 text-center sm:px-10 sm:py-12">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,oklch(0.7_0.2_280/0.2),transparent_50%)]" />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_78%_88%,oklch(0.78_0.14_75/0.14),transparent_42%)]" />
          <div className="relative">
            <h2 className="text-foreground font-heading text-xl font-bold sm:text-2xl">
              {bottomCta.title}
            </h2>
            <p className="text-muted-foreground mx-auto mt-2 max-w-md text-sm sm:text-base">
              {bottomCta.subtitle}
            </p>
            <div className="mx-auto mt-6 grid max-w-lg grid-cols-1 gap-3 sm:max-w-3xl sm:grid-cols-2 lg:max-w-4xl lg:grid-cols-3">
              {bottomCta.ctas.map((cta) => (
                <HomeCtaLink
                  key={`bottom-${cta.href}-${cta.variant}`}
                  cta={cta}
                  surface="bottom"
                />
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ModelReportCard } from "@/lib/model-report-cards";

type ModelReportCardsProps = {
  title: string;
  description: string;
  cards: ModelReportCard[];
  primaryMetricLabel: string;
  sampleCaption: string;
  secondaryMetricLabel?: string;
  secondaryMetric?: (card: ModelReportCard) => string | null;
};

export function ModelReportCards({
  title,
  description,
  cards,
  primaryMetricLabel,
  sampleCaption,
  secondaryMetricLabel,
  secondaryMetric,
}: ModelReportCardsProps) {
  return (
    <section className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-foreground font-heading text-2xl font-semibold tracking-tight">
          {title}
        </h2>
        <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
          {description}
        </p>
      </div>

      {cards.length === 0 ? (
        <Card className="border-dashed shadow-none">
          <CardContent className="py-6 text-sm text-muted-foreground">
            まだ成績カードを出せるだけの照合データがありません。
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {cards.map((card) => {
            const secondary = secondaryMetric?.(card) ?? null;
            return (
              <Card key={card.slug} className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base leading-snug">{card.label}</CardTitle>
                  <CardDescription className="text-xs">{sampleCaption.replace("{n}", String(card.sampleSize))}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-muted-foreground text-xs font-medium tracking-wide">
                      {primaryMetricLabel}
                    </p>
                    <p className="text-foreground mt-1 text-2xl font-semibold tabular-nums">
                      {card.hitRatePct}%
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-3 rounded-xl border border-border/70 bg-background/60 px-3 py-3 text-sm">
                    <div>
                      <p className="text-muted-foreground text-xs">hits</p>
                      <p className="text-foreground mt-1 font-medium tabular-nums">
                        {card.hitsAny}/{card.sampleSize}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs">
                        {secondaryMetricLabel ?? "secondary"}
                      </p>
                      <p className="text-foreground mt-1 font-medium tabular-nums">
                        {secondary ?? "—"}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </section>
  );
}

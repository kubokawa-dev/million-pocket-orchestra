import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { MissAnalysisSummary } from "@/lib/miss-analysis";

type MissAnalysisCardsProps = {
  title: string;
  description: string;
  summary: MissAnalysisSummary;
  oneDigitOffLabel: string;
};

type StatCard = {
  label: string;
  value: string;
  detail: string;
};

function buildStatCards(
  summary: MissAnalysisSummary,
  oneDigitOffLabel: string,
): StatCard[] {
  return [
    {
      label: "top 10 box",
      value: `${summary.top10BoxRatePct}%`,
      detail: "直近サンプルで、ensemble の上位10候補以内にボックス相当が入っていた割合です。",
    },
    {
      label: "top 20 exact",
      value: `${summary.exactTop20RatePct}%`,
      detail: "上位20候補のどこかでストレート一致していた割合です。完全一致だけを見た数字です。",
    },
    {
      label: oneDigitOffLabel,
      value: `${summary.oneDigitOffTop1RatePct}%`,
      detail: "top1 が完全一致ではないものの、数字の重なり方がかなり近かった回の割合です。",
    },
    {
      label: "avg first box rank",
      value:
        summary.averageFirstBoxRank != null
          ? `${summary.averageFirstBoxRank} 位`
          : "—",
      detail: "ボックス相当が入っていた回だけで見た、最初の一致順位の平均です。低いほど早い段階で近い候補が出ています。",
    },
  ];
}

export function MissAnalysisCards({
  title,
  description,
  summary,
  oneDigitOffLabel,
}: MissAnalysisCardsProps) {
  if (summary.sampleSize === 0) {
    return null;
  }

  const cards = buildStatCards(summary, oneDigitOffLabel);

  return (
    <section className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-foreground font-heading text-2xl font-semibold tracking-tight">
          {title}
        </h2>
        <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
          {description}
        </p>
        <p className="text-muted-foreground text-xs">
          直近 {summary.sampleSize} 回の照合です。将来の優位性を保証するものではなく、外れ方の質を見るための参考表示です。
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <Card
            key={card.label}
            className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10"
          >
            <CardHeader className="pb-3">
              <CardTitle className="text-base leading-snug">{card.label}</CardTitle>
              <CardDescription className="text-xs">{card.detail}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-foreground text-2xl font-semibold tabular-nums">
                {card.value}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

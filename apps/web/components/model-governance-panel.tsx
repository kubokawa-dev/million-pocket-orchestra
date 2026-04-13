import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ModelGovernanceSummary } from "@/lib/model-governance";

type ModelGovernancePanelProps = {
  title: string;
  description: string;
  summary: ModelGovernanceSummary;
};

function ModelList({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: { slug: string; label: string }[];
}) {
  return (
    <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="pb-3">
        <CardTitle className="text-base leading-snug">{title}</CardTitle>
        <CardDescription className="text-xs leading-relaxed">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-muted-foreground text-sm">該当モデルはありません。</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {items.map((item) => (
              <span
                key={item.slug}
                className="border-border/70 bg-background/60 text-foreground rounded-full border px-3 py-1 text-sm"
              >
                {item.label}
              </span>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ModelGovernancePanel({
  title,
  description,
  summary,
}: ModelGovernancePanelProps) {
  if (summary.sampleSize === 0) {
    return null;
  }

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
          直近 {summary.sampleSize} 回の成績を基準に、表示上の扱いを整理しています。将来の断定ではなく、過信を防ぐための運用ルールです。
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <ModelList
          title="主役にするモデル"
          description="直近成績が比較的安定しているため、まず見る候補です。"
          items={summary.preferred}
        />
        <ModelList
          title="様子を見るモデル"
          description="完全に切らず、補助的に扱うラインです。"
          items={summary.watchlist}
        />
        <ModelList
          title="控えめに扱うモデル"
          description="直近成績が弱いため、説明や重み付けでは後ろに回す候補です。"
          items={summary.deprioritized}
        />
      </div>
    </section>
  );
}

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { BudgetPlanPayload } from "@/lib/numbers4-predictions/types";

type BudgetStrategyOverviewProps = {
  title: string;
  description: string;
  budgetPlan: BudgetPlanPayload | null;
};

type StrategyCard = {
  title: string;
  summary: string;
  fit: string;
  budgets: string[];
  metrics: string[];
};

function toBudgetLabel(value?: string | null): string | null {
  if (!value) return null;
  return value.replace(/\s+/g, "");
}

function pushMetric(metrics: string[], label: string, value?: string | number | null) {
  if (value == null || value === "") return;
  metrics.push(`${label}: ${value}`);
}

function buildStrategyCards(budgetPlan: BudgetPlanPayload | null): StrategyCard[] {
  if (!budgetPlan) return [];

  const cards: StrategyCard[] = [];

  if (budgetPlan.plan_5 || budgetPlan.plan_10) {
    const budgets = [budgetPlan.plan_5?.budget, budgetPlan.plan_10?.budget]
      .map(toBudgetLabel)
      .filter((value): value is string => value != null);
    const preferred = budgetPlan.plan_10 ?? budgetPlan.plan_5;
    const metrics: string[] = [];
    pushMetric(metrics, "coverage", preferred?.total_coverage);
    pushMetric(metrics, "probability", preferred?.probability);
    cards.push({
      title: "バランス型",
      summary: "最初に見る基準プラン。極端に寄せず、候補の重複を抑えながら基本の買い目を組みます。",
      fit: "迷ったらここから。少額で全体像を見たい人向けです。",
      budgets,
      metrics,
    });
  }

  if (budgetPlan.hybrid_5 || budgetPlan.hybrid_10) {
    const budgets = [budgetPlan.hybrid_5?.total_budget, budgetPlan.hybrid_10?.total_budget]
      .map(toBudgetLabel)
      .filter((value): value is string => value != null);
    const preferred = budgetPlan.hybrid_10 ?? budgetPlan.hybrid_5;
    const metrics: string[] = [];
    pushMetric(metrics, "combined", preferred?.combined_probability);
    pushMetric(metrics, "box coverage", preferred?.box_coverage);
    pushMetric(metrics, "mini tails", preferred?.mini_unique_tails);
    cards.push({
      title: "広げつつ絞る型",
      summary: "ボックスを軸にしつつミニで裾野を広げる、重複削減と探索の中間プランです。",
      fit: "同じような候補ばかり買いたくない人、少し攻めたい人向けです。",
      budgets,
      metrics,
    });
  }

  if (budgetPlan.expected_value_5 || budgetPlan.expected_value_10) {
    const budgets = [budgetPlan.expected_value_5?.budget, budgetPlan.expected_value_10?.budget]
      .map(toBudgetLabel)
      .filter((value): value is string => value != null);
    const preferred = budgetPlan.expected_value_10 ?? budgetPlan.expected_value_5;
    const metrics: string[] = [];
    pushMetric(metrics, "probability", preferred?.probability);
    pushMetric(metrics, "expected", preferred?.total_expected_value);
    cards.push({
      title: "期待値重視型",
      summary: "当たりやすさだけでなく、配当の見込みも含めて並べ替える参考プランです。",
      fit: "確率だけでなく、モデルの評価軸をもう一段見たい人向けです。",
      budgets,
      metrics,
    });
  }

  if (budgetPlan.distributed_plan) {
    const metrics: string[] = [];
    pushMetric(metrics, "per cycle", budgetPlan.distributed_plan.cumulative_probability);
    pushMetric(metrics, "monthly", budgetPlan.distributed_plan.monthly_hit_probability);
    pushMetric(metrics, "sessions", budgetPlan.distributed_plan.sessions);
    cards.push({
      title: "分散購入型",
      summary: "一度に張らず、複数回に分けて買う前提で候補の偏りを緩めるプランです。",
      fit: "毎回少しずつ継続したい人、月間で管理したい人向けです。",
      budgets: [toBudgetLabel(budgetPlan.distributed_plan.total_budget)].filter(
        (value): value is string => value != null,
      ),
      metrics,
    });
  }

  if (budgetPlan.all_mini_5) {
    const metrics: string[] = [];
    pushMetric(metrics, "per draw", budgetPlan.all_mini_5.per_draw_probability);
    pushMetric(metrics, "monthly", budgetPlan.all_mini_5.monthly_probability);
    pushMetric(metrics, "slots", budgetPlan.all_mini_5.slots);
    cards.push({
      title: "薄く広く型",
      summary: "ミニを中心に候補の幅を取りに行くプランで、少額で広く試す時に向きます。",
      fit: "一点集中より分散を優先したい人向けです。",
      budgets: [toBudgetLabel(budgetPlan.all_mini_5.total_budget)].filter(
        (value): value is string => value != null,
      ),
      metrics,
    });
  }

  if (budgetPlan.set_plan || budgetPlan.set_plan_5) {
    const budgets = [budgetPlan.set_plan?.total_budget, budgetPlan.set_plan_5?.total_budget]
      .map(toBudgetLabel)
      .filter((value): value is string => value != null);
    const preferred = budgetPlan.set_plan_5 ?? budgetPlan.set_plan;
    const metrics: string[] = [];
    pushMetric(metrics, "coverage", preferred?.total_coverage);
    pushMetric(metrics, "probability", preferred?.probability);
    pushMetric(metrics, "slots", preferred?.slots);
    cards.push({
      title: "セット寄り型",
      summary: "セット購入を前提に、口数とカバー範囲のバランスを取りたい時の参考プランです。",
      fit: "ストレートだけに寄せず、セット込みで考えたい人向けです。",
      budgets,
      metrics,
    });
  }

  return cards;
}

export function BudgetStrategyOverview({
  title,
  description,
  budgetPlan,
}: BudgetStrategyOverviewProps) {
  const cards = buildStrategyCards(budgetPlan);

  if (cards.length === 0) {
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
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <Card
            key={card.title}
            className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10"
          >
            <CardHeader className="pb-3">
              <div className="flex flex-wrap items-center gap-2">
                <CardTitle className="text-base leading-snug">{card.title}</CardTitle>
                {card.budgets.map((budget) => (
                  <Badge key={budget} variant="outline" className="text-[0.7rem]">
                    {budget}
                  </Badge>
                ))}
              </div>
              <CardDescription className="text-sm leading-relaxed">
                {card.summary}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-foreground text-sm font-medium">{card.fit}</p>
              {card.metrics.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {card.metrics.map((metric) => (
                    <Badge key={metric} variant="secondary" className="font-normal">
                      {metric}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

import { SparklesIcon } from "lucide-react";

import { AnalysisTransparencyCallout } from "@/components/analysis-transparency-callout";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  countLoto6MainHits,
  isLoto6BonusHit,
} from "@/lib/loto6-predictions/hit-utils";
import { lastLoto6PredictionRun } from "@/lib/loto6-predictions/load-bundles";
import type {
  Loto6BudgetPlanPayload,
  Loto6MethodPayload,
  Loto6PredictionBundle,
  Loto6TopPrediction,
} from "@/lib/loto6-predictions/types";

const DISPLAY_LIMIT = 12;

function formatMain(main: number[] | undefined | null): string {
  if (!main?.length) return "—";
  return main
    .slice()
    .sort((a, b) => a - b)
    .map((n) => String(n))
    .join(" · ");
}

function normalizeTicket(row: Loto6TopPrediction, index: number): {
  rank: number;
  main: number[];
  bonus: number | null;
  score: number | null;
} {
  const main = (row.main ?? []).filter(
    (x) => typeof x === "number" && x >= 1 && x <= 43,
  );
  const bonus =
    typeof row.bonus === "number" && row.bonus >= 1 && row.bonus <= 43
      ? row.bonus
      : null;
  return {
    rank: typeof row.rank === "number" ? row.rank : index + 1,
    main,
    bonus,
    score: typeof row.score === "number" ? row.score : null,
  };
}

function TicketsTable({
  rows,
  actualMain,
  actualBonus,
}: {
  rows: Loto6TopPrediction[];
  actualMain?: number[];
  actualBonus?: number | null;
}) {
  const showHits =
    actualMain != null &&
    actualMain.length === 6 &&
    actualBonus != null &&
    actualBonus > 0;

  const normalized = rows
    .slice(0, DISPLAY_LIMIT)
    .map((r, i) => normalizeTicket(r, i))
    .filter((r) => r.main.length === 6);

  if (!normalized.length) {
    return (
      <p className="text-muted-foreground text-sm">有効な候補行がありません。</p>
    );
  }

  return (
    <div className="overflow-x-auto">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-14">順</TableHead>
          <TableHead>本数字（試算）</TableHead>
          <TableHead className="w-20 text-right">Bonus</TableHead>
          {showHits ? (
            <>
              <TableHead className="w-24 text-right">本一致</TableHead>
              <TableHead className="w-20 text-center">B</TableHead>
            </>
          ) : null}
          <TableHead className="w-24 text-right">スコア</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {normalized.map((r) => {
          const mainHits = showHits
            ? countLoto6MainHits(r.main, actualMain!)
            : null;
          const bHit =
            showHits && isLoto6BonusHit(r.bonus, actualBonus) ? "○" : "—";
          return (
            <TableRow key={r.rank}>
              <TableCell className="font-mono text-sm tabular-nums">
                {r.rank}
              </TableCell>
              <TableCell className="font-mono text-sm">{formatMain(r.main)}</TableCell>
              <TableCell className="text-right font-mono text-sm">
                {r.bonus ?? "—"}
              </TableCell>
              {showHits ? (
                <>
                  <TableCell className="text-right font-mono text-sm tabular-nums">
                    {mainHits}/6
                  </TableCell>
                  <TableCell className="text-center text-sm">{bHit}</TableCell>
                </>
              ) : null}
              <TableCell className="text-right font-mono text-sm tabular-nums">
                {r.score != null ? r.score : "—"}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
    </div>
  );
}

function BudgetPlanSection({ plan }: { plan: Loto6BudgetPlanPayload }) {
  const guide = plan.monthly_budget_guide;
  const note =
    guide && typeof guide.note === "string" ? guide.note : null;

  return (
    <Card className="border-border/70 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">予算プラン（MVP・参考）</CardTitle>
        <CardDescription className="text-xs">
          {plan.planner_version ? `planner: ${plan.planner_version}` : null}
          {plan.created_at ? ` · ${plan.created_at}` : null}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        {note ? (
          <p className="text-muted-foreground leading-relaxed">{note}</p>
        ) : null}
        {plan.plan_5?.recommendations?.length ? (
          <div>
            <p className="text-foreground mb-2 font-medium">{plan.plan_5.budget ?? "plan_5"}</p>
            <ul className="text-muted-foreground list-inside list-disc space-y-1">
              {plan.plan_5.recommendations.map((r, i) => (
                <li key={i}>
                  <span className="font-mono text-foreground">{r.number ?? "—"}</span>
                  {r.reason ? ` — ${r.reason}` : null}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {plan.plan_10?.recommendations?.length ? (
          <div>
            <p className="text-foreground mb-2 font-medium">{plan.plan_10.budget ?? "plan_10"}</p>
            <ul className="text-muted-foreground list-inside list-disc space-y-1">
              {plan.plan_10.recommendations.map((r, i) => (
                <li key={i}>
                  <span className="font-mono text-foreground">{r.number ?? "—"}</span>
                  {r.reason ? ` — ${r.reason}` : null}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function MethodLabel(slug: string): string {
  if (slug === "cold_six") return "コールド6（出現少なめ寄り）";
  if (slug === "hot_six") return "ホット6（出現多め寄り）";
  if (slug === "pair_cooccur") return "ペア共起（いっしょに出やすい球）";
  if (slug === "last_draw_shift") return "前回シフト（前回から1球差し替え）";
  if (slug === "sum_streak") return "和ストリーク（連番ブロックで和を寄せる）";
  if (slug === "odd_even_cold") return "奇偶コールド（奇3・偶3を冷めから）";
  if (slug === "zone_heat") return "ゾーンヒート（低・中・高帯から人気球）";
  if (slug === "spread_wheel") return "スプレッド（円周7間隔で散らす）";
  return slug;
}

function MethodSection({
  slug,
  payload,
  actualMain,
  actualBonus,
}: {
  slug: string;
  payload: Loto6MethodPayload;
  actualMain?: number[];
  actualBonus?: number | null;
}) {
  const run = lastLoto6PredictionRun(payload);
  const tops = run?.top_predictions ?? [];
  return (
    <Card className="border-border/70 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{MethodLabel(slug)}</CardTitle>
        <CardDescription className="font-mono text-xs">
          method: {slug}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TicketsTable
          rows={tops}
          actualMain={actualMain}
          actualBonus={actualBonus}
        />
      </CardContent>
    </Card>
  );
}

type Loto6PredictionsPanelProps = {
  bundle: Loto6PredictionBundle;
  /** 当選が確定しているときのみ渡す（照合用） */
  actualMain?: number[];
  actualBonus?: number | null;
};

export function Loto6PredictionsPanel({
  bundle,
  actualMain,
  actualBonus,
}: Loto6PredictionsPanelProps) {
  const ens = bundle.ensemble;
  const ensRun = ens ? lastLoto6PredictionRun(ens) : null;
  const ensTops = ensRun?.top_predictions ?? [];
  const weights =
    ensRun && "ensemble_weights" in ensRun ? ensRun.ensemble_weights : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <SparklesIcon className="text-amber-600 dark:text-amber-400 size-5" />
        <h2 className="text-foreground font-heading text-lg font-semibold tracking-tight">
          モデル試算（MVP）第 {bundle.targetDrawNumber} 回向け
        </h2>
      </div>
      <p className="text-muted-foreground text-sm leading-relaxed">
        直近の抽選データから頻度を集計したシンプルモデルです。娯楽・検証用で、当せんの保証はありません。
      </p>

      <AnalysisTransparencyCallout
        basis={[
          "公開されているロト6の当せん番号（本数字・ボーナス）を前提に、各 method のルールで候補を生成しています。",
          "行の「スコア」はモデル内部の並び替え用指標で、期待値や当せん確率ではありません。",
        ]}
        limitations={[
          "抽選はランダム性が大きく、過去の出方から将来が読めるとは限りません。",
          "表示は「試算・整理」であり、購入の推奨や最適口数の指示ではありません。",
        ]}
      />

      {ens && ensTops.length > 0 ? (
        <Card className="border-amber-500/25 bg-amber-500/[0.04] shadow-sm ring-1 ring-amber-500/15 dark:ring-amber-400/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">アンサンブル（合成）</CardTitle>
            <CardDescription>
              {weights
                ? Object.entries(weights)
                    .map(([k, v]) => `${MethodLabel(k)} ${v}`)
                    .join(" · ")
                : "cold_six + hot_six の候補を合成"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TicketsTable
              rows={ensTops}
              actualMain={actualMain}
              actualBonus={actualBonus}
            />
          </CardContent>
        </Card>
      ) : null}

      {bundle.budgetPlan &&
      (bundle.budgetPlan.plan_5?.recommendations?.length ||
        bundle.budgetPlan.plan_10?.recommendations?.length) ? (
        <BudgetPlanSection plan={bundle.budgetPlan} />
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {bundle.methodRows.map(({ slug, payload }) => (
          <MethodSection
            key={slug}
            slug={slug}
            payload={payload}
            actualMain={actualMain}
            actualBonus={actualBonus}
          />
        ))}
      </div>
    </div>
  );
}

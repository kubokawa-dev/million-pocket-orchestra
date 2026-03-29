import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { BarChart3Icon, CoinsIcon, LayersIcon, ListOrderedIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
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
  getLatestEnsembleRun,
  loadNumbers4Predictions6949,
} from "@/lib/numbers4-predictions/load-6949";
import type { BudgetPlanSlice, PredictionBundle6949 } from "@/lib/numbers4-predictions/types";
import { cn } from "@/lib/utils";

function SourceBadges({ data }: { data: PredictionBundle6949 }) {
  const sourceLabel =
    data.source === "database"
      ? "Supabase"
      : data.source === "repository_files"
        ? "リポジトリ JSON"
        : "内蔵モック";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="outline" className="font-mono text-[0.7rem]">
        DEBUG 6949
      </Badge>
      <Badge
        variant={data.source === "database" ? "default" : "secondary"}
        className="text-xs"
      >
        データ: {sourceLabel}
      </Badge>
    </div>
  );
}

function BudgetPlanCard({
  title,
  icon: Icon,
  plan,
}: {
  title: string;
  icon: LucideIcon;
  plan: BudgetPlanSlice | undefined;
}) {
  const recs = plan?.recommendations ?? [];
  if (!plan || recs.length === 0) return null;

  return (
    <Card className="border-border/80 h-full shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <Icon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          {plan.budget && <span>{plan.budget}</span>}
          {plan.slots != null && <span>{plan.slots} 口</span>}
          {plan.total_coverage != null && (
            <span>カバー {plan.total_coverage} 通り</span>
          )}
          {plan.probability && <span>当選確率目安 {plan.probability}</span>}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 pb-4 pt-0">
        <div className="max-h-[28rem] overflow-y-auto sm:max-h-none">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="text-muted-foreground w-14 px-3 text-xs sm:px-4">
                  順
                </TableHead>
                <TableHead className="text-muted-foreground px-3 text-xs sm:px-4">
                  番号
                </TableHead>
                <TableHead className="text-muted-foreground hidden px-3 text-xs sm:table-cell sm:px-4">
                  買い方
                </TableHead>
                <TableHead className="text-muted-foreground hidden px-3 text-xs md:table-cell md:px-4">
                  理由
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recs.map((r, i) => (
                <TableRow key={`${r.number}-${i}`} className="border-border/60">
                  <TableCell className="text-muted-foreground px-3 py-2.5 text-xs sm:px-4">
                    {r.priority ?? `—`}
                  </TableCell>
                  <TableCell className="font-mono px-3 py-2.5 text-sm font-semibold tracking-wide sm:px-4">
                    {r.number ?? "—"}
                  </TableCell>
                  <TableCell className="hidden px-3 py-2.5 text-xs sm:table-cell sm:px-4">
                    <span className="text-foreground">{r.buy_method ?? "—"}</span>
                    {r.box_type && (
                      <span className="text-muted-foreground block text-[0.65rem]">
                        {r.box_type}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground hidden max-w-[14rem] truncate px-3 py-2.5 text-xs md:table-cell md:max-w-none md:whitespace-normal md:px-4">
                    {r.reason ?? "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

export async function Numbers4PredictionsHub() {
  const data = await loadNumbers4Predictions6949();
  const latest = getLatestEnsembleRun(data.ensemble);
  const topList = (latest?.top_predictions ?? []).slice(0, 12);
  const weights = latest?.ensemble_weights
    ? Object.entries(latest.ensemble_weights)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)
    : [];

  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-[1600px] flex-1 space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <SourceBadges data={data} />
            <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
              ナンバーズ4 予測ダッシュボード
            </h1>
            <p className="text-muted-foreground max-w-2xl text-sm leading-relaxed sm:text-base">
              <span className="text-foreground font-medium">
                第 {data.targetDrawNumber} 回
              </span>
              向けの日次予測を表示しています（現在はデバッグ用に回号固定）。
              本番では「次回抽選回号」に自動で追従させる想定です。
            </p>
            {data.source !== "database" && (
              <p className="text-muted-foreground border-border/80 bg-muted/40 max-w-2xl rounded-lg border px-3 py-2 text-xs leading-relaxed">
                Supabase に{" "}
                <code className="bg-muted rounded px-1 font-mono">
                  numbers4_daily_prediction_documents
                </code>{" "}
                の該当行が無いため、リポジトリ内の JSON または内蔵モックを表示しています。
              </p>
            )}
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <Link
              href="/numbers4/result"
              className={cn(buttonVariants({ size: "lg" }), "justify-center shadow-sm")}
            >
              当選番号一覧へ
            </Link>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 lg:col-span-2">
            <CardHeader className="border-border/60 border-b">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2">
                  <LayersIcon className="text-muted-foreground size-5" />
                  <div>
                    <CardTitle className="text-lg">アンサンブル TOP</CardTitle>
                    <CardDescription>
                      最新実行のスコア順（最大12件）· JST{" "}
                      {latest?.time_jst ?? "—"}
                    </CardDescription>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-0 pb-6 pt-4 sm:px-0">
              <div className="grid gap-6 lg:grid-cols-2">
                <div className="px-4 sm:px-6">
                  <div className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide">
                    <ListOrderedIcon className="size-3.5" />
                    ランキング
                  </div>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent">
                          <TableHead className="w-12 text-xs">#</TableHead>
                          <TableHead className="text-xs">番号</TableHead>
                          <TableHead className="text-right text-xs">スコア</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topList.length === 0 ? (
                          <TableRow>
                            <TableCell
                              colSpan={3}
                              className="text-muted-foreground h-24 text-center text-sm"
                            >
                              予測データがありません
                            </TableCell>
                          </TableRow>
                        ) : (
                          topList.map((row, i) => (
                            <TableRow key={`${row.rank}-${row.number}-${i}`}>
                              <TableCell className="text-muted-foreground tabular-nums">
                                {row.rank ?? "—"}
                              </TableCell>
                              <TableCell className="font-mono font-semibold tracking-wide">
                                {row.number ?? "—"}
                              </TableCell>
                              <TableCell className="text-right tabular-nums">
                                {row.score != null
                                  ? row.score.toLocaleString("ja-JP", {
                                      maximumFractionDigits: 2,
                                    })
                                  : "—"}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
                <div className="border-border/60 px-4 lg:border-l lg:px-6">
                  <div className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide">
                    <BarChart3Icon className="size-3.5" />
                    モデル重み（上位）
                  </div>
                  <div className="max-h-64 space-y-2 overflow-y-auto pr-1">
                    {weights.length === 0 ? (
                      <p className="text-muted-foreground text-sm">—</p>
                    ) : (
                      weights.map(([name, w]) => (
                        <div
                          key={name}
                          className="flex items-center justify-between gap-3 text-sm"
                        >
                          <span className="text-foreground truncate font-mono text-xs">
                            {name}
                          </span>
                          <span className="text-muted-foreground shrink-0 tabular-nums">
                            {w.toLocaleString("ja-JP", {
                              maximumFractionDigits: 2,
                            })}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <BudgetPlanCard
            title="予算プラン · 1,000円枠"
            icon={CoinsIcon}
            plan={data.budgetPlan?.plan_5}
          />
          <BudgetPlanCard
            title="予算プラン · 2,000円枠"
            icon={CoinsIcon}
            plan={data.budgetPlan?.plan_10}
          />
        </div>

        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 border-b">
            <CardTitle className="text-lg">個別メソッド（サマリ）</CardTitle>
            <CardDescription>
              各手法 JSON の最新 1 件から 1 位候補を抜き出しています（空の手法は
              「—」）。
            </CardDescription>
          </CardHeader>
          <CardContent className="px-0 pb-4 pt-0 sm:px-0">
            <div className="overflow-x-auto">
              <Table className="min-w-[640px]">
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      method_slug
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      実行回数
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      最終 JST
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      1位候補
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.methodRows.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={4}
                        className="text-muted-foreground h-20 text-center text-sm"
                      >
                        メソッド行がありません（DB に method 種別が無い、または JSON
                        未配置）
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.methodRows.map((m) => (
                      <TableRow key={m.slug} className="border-border/60">
                        <TableCell className="px-4 font-mono text-xs sm:px-6">
                          {m.slug}
                        </TableCell>
                        <TableCell className="px-4 tabular-nums sm:px-6">
                          {m.runs}
                        </TableCell>
                        <TableCell className="text-muted-foreground px-4 text-sm sm:px-6">
                          {m.lastTimeJst ?? "—"}
                        </TableCell>
                        <TableCell className="px-4 font-mono text-sm font-medium sm:px-6">
                          {m.topNumber ?? "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import Link from "next/link";
import { notFound } from "next/navigation";
import type { LucideIcon } from "lucide-react";
import {
  BarChart3Icon,
  CoinsIcon,
  DatabaseIcon,
  LayersIcon,
  ListOrderedIcon,
  SparklesIcon,
  TargetIcon,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { buildMethodConsensus } from "@/lib/numbers4-predictions/consensus";
import { getEnsembleWeightJaLabel } from "@/lib/numbers4-predictions/ensemble-weight-labels";
import {
  fetchNumbers4DrawFullRow,
  fetchNumbers4DrawResult,
  getLatestEnsembleRun,
  loadNumbers4PredictionBundle,
  loadNumbers4PredictionBundleForDraw,
} from "@/lib/numbers4-predictions/load-6949";
import {
  classifyHit,
  createWinningDigitPool,
  hitLabel,
  normalizeNumbers4,
  type HitKind,
} from "@/lib/numbers4-predictions/prediction-hit-utils";
import type {
  BudgetPlanSlice,
  BudgetRecommendation,
  EnsembleTopPrediction,
  Numbers4PredictionBundle,
} from "@/lib/numbers4-predictions/types";
import { cn } from "@/lib/utils";

import { Numbers4OfficialDrawDetail } from "./numbers4-official-draw-detail";

export type Numbers4PredictionsHubProps = {
  /** 指定時はその回の予測のみ読み込み（無ければ公式当選のみ or 404） */
  targetDrawNumber?: number;
  /** `/numbers4/result/[回]` 用の一覧へ戻るリンク */
  showBackToResultList?: boolean;
};

function SourceBadges({ data }: { data: Numbers4PredictionBundle }) {
  const sourceLabel =
    data.source === "database"
      ? "Supabase（numbers4_daily_prediction_documents）"
      : data.source === "repository_files"
        ? "リポジトリ JSON"
        : "内蔵デモ";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="outline" className="font-mono text-[0.7rem]">
        第 {data.targetDrawNumber} 回
      </Badge>
      <Badge
        variant={data.source === "database" ? "default" : "secondary"}
        className="text-xs"
      >
        <DatabaseIcon className="mr-1 inline size-3" />
        {sourceLabel}
      </Badge>
    </div>
  );
}

function HitBadge({ kind, className }: { kind: HitKind; className?: string }) {
  if (kind === "none") return null;
  return (
    <Badge
      variant={kind === "straight" ? "default" : "secondary"}
      className={cn(
        "font-normal",
        kind === "straight" && "bg-emerald-600 hover:bg-emerald-600/90",
        kind === "box" && "border-amber-600/60 bg-amber-500/15 text-amber-950 dark:text-amber-100",
        className,
      )}
    >
      {hitLabel(kind)}
    </Badge>
  );
}

function numberCellClass(kind: HitKind): string {
  if (kind === "straight")
    return "bg-emerald-500/10 ring-1 ring-emerald-600/40";
  if (kind === "box") return "bg-amber-500/10 ring-1 ring-amber-600/35";
  return "";
}

/**
 * 当選番号の各数字の個数を上限に、予測を左から見て「まだ当選側に余りがある」桁だけ薄い赤。
 * 例: 当選 4568（4 が1個）・予測 4444 → 先頭の 4 だけ強調、残りは色なし。
 */
function PredictionNumberHighlight({
  value,
  winningRaw,
  className,
}: {
  value: string | null | undefined;
  winningRaw: string | null;
  className?: string;
}) {
  if (value == null || value === "") return <>—</>;
  const norm = normalizeNumbers4(value);
  const chars =
    norm != null ? [...norm] : [...String(value).replace(/\D/g, "")];
  if (chars.length === 0) {
    return <span className={className}>{value}</span>;
  }

  const poolTemplate = createWinningDigitPool(winningRaw);
  const pool =
    poolTemplate != null ? new Map(poolTemplate) : null;

  return (
    <span
      className={cn(
        "inline-flex items-center tabular-nums tracking-wide",
        className,
      )}
      translate="no"
    >
      {chars.map((ch, i) => {
        const isDigit = ch >= "0" && ch <= "9";
        let highlight = false;
        if (pool != null && isDigit) {
          const left = pool.get(ch) ?? 0;
          if (left > 0) {
            highlight = true;
            pool.set(ch, left - 1);
          }
        }
        return (
          <span
            key={`${i}-${ch}`}
            className={cn(
              highlight &&
                "rounded-[2px] bg-red-400/[0.12] px-[1px] text-red-600/85 dark:bg-red-500/[0.14] dark:text-red-200/75",
            )}
          >
            {ch}
          </span>
        );
      })}
    </span>
  );
}

function BudgetPlanCard({
  title,
  icon: Icon,
  plan,
  winning: winningRaw,
}: {
  title: string;
  icon: LucideIcon;
  plan: BudgetPlanSlice | undefined;
  winning: string | null;
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
          <span className="text-muted-foreground">doc_kind: budget_plan</span>
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
                <TableHead className="text-muted-foreground px-3 text-xs sm:px-4">
                  あたり
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
              {recs.map((r: BudgetRecommendation, i: number) => {
                const num = r.number ?? "";
                const hit = classifyHit(num, winningRaw);
                return (
                  <TableRow key={`${r.number}-${i}`} className="border-border/60">
                    <TableCell className="text-muted-foreground px-3 py-2.5 text-xs sm:px-4">
                      {r.priority ?? `—`}
                    </TableCell>
                    <TableCell
                      className={cn(
                        "rounded-md px-3 py-2.5 text-sm font-semibold sm:px-4",
                        numberCellClass(hit),
                      )}
                    >
                      <PredictionNumberHighlight
                        value={r.number}
                        winningRaw={winningRaw}
                        className="font-mono"
                      />
                    </TableCell>
                    <TableCell className="px-3 py-2.5 sm:px-4">
                      <HitBadge kind={hit} className="text-[0.65rem]" />
                      {hit === "none" && winningRaw && (
                        <span className="text-muted-foreground text-xs">—</span>
                      )}
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
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

export async function Numbers4PredictionsHub({
  targetDrawNumber,
  showBackToResultList = false,
}: Numbers4PredictionsHubProps = {}) {
  let data: Numbers4PredictionBundle;

  if (targetDrawNumber !== undefined) {
    const got = await loadNumbers4PredictionBundleForDraw(targetDrawNumber);
    if (!got) {
      const official = await fetchNumbers4DrawFullRow(targetDrawNumber);
      if (!official) notFound();
      return (
        <div className="flex flex-1 flex-col">
          {showBackToResultList ? (
            <div className="mx-auto w-full max-w-3xl px-4 pt-8 sm:max-w-4xl sm:px-6">
              <Link
                href="/numbers4/result"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "sm" }),
                  "text-muted-foreground -ml-2 hover:text-foreground",
                )}
              >
                ← 一覧へ
              </Link>
            </div>
          ) : null}
          <Numbers4OfficialDrawDetail row={official} />
        </div>
      );
    }
    data = got;
  } else {
    data = await loadNumbers4PredictionBundle();
  }

  const resultRow = await fetchNumbers4DrawResult(data.targetDrawNumber);
  const winningRaw = resultRow?.numbers ?? null;
  const winningNorm = normalizeNumbers4(winningRaw);

  const latest = getLatestEnsembleRun(data.ensemble);
  const topList = (latest?.top_predictions ?? []).slice(0, 18);
  const weights = latest?.ensemble_weights
    ? Object.entries(latest.ensemble_weights)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 14)
    : [];

  const consensus = buildMethodConsensus(data.methodRows, 3);

  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-[1600px] flex-1 space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-10">
        {showBackToResultList ? (
          <div className="-mt-2 mb-2">
            <Link
              href="/numbers4/result"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "text-muted-foreground -ml-2 hover:text-foreground",
              )}
            >
              ← 一覧へ
            </Link>
          </div>
        ) : null}
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <SourceBadges data={data} />
            <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
              ナンバーズ4 予測
            </h1>
            <p className="text-muted-foreground max-w-2xl text-sm leading-relaxed sm:text-base">
              Supabase の{" "}
              <code className="bg-muted rounded px-1 font-mono text-xs">
                numbers4_daily_prediction_documents
              </code>{" "}
              と同じく、
              <strong className="text-foreground"> ensemble / method / budget_plan </strong>
              の3種類のドキュメントを一覧しやすくまとめています。当選番号が DB
              に入っていれば、予測との一致も表示します。
            </p>
            {data.source !== "database" && (
              <p className="text-muted-foreground border-border/80 bg-muted/40 max-w-2xl rounded-lg border px-3 py-2 text-xs leading-relaxed">
                該当する Supabase 行が無いため、リポジトリ内 JSON またはデモデータを表示しています。
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

        <Card
          className={cn(
            "overflow-hidden shadow-sm ring-1 ring-black/5 dark:ring-white/10",
            winningNorm
              ? "border-emerald-600/25 bg-gradient-to-br from-emerald-500/5 to-transparent"
              : "border-border/80",
          )}
        >
          <CardHeader className="pb-2">
            <div className="flex flex-wrap items-center gap-2">
              <TargetIcon className="text-muted-foreground size-5" />
              <CardTitle className="text-lg">第 {data.targetDrawNumber} 回 · 当選結果</CardTitle>
            </div>
            <CardDescription>
              <code className="text-muted-foreground text-xs">numbers4_draws.numbers</code>{" "}
              と照合（ストレート / ボックス相当）。
              {winningNorm
                ? " 下の予測番号で、当選と同じ数字は出現回数の範囲内だけ左から薄い赤で強調します（例: 当選に4が1個なら予測の4は先頭1桁のみ）。"
                : null}
            </CardDescription>
          </CardHeader>
          <CardContent className="pb-6 pt-0">
            {winningNorm ? (
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:gap-8">
                <div>
                  <p className="text-muted-foreground mb-1 text-xs font-medium uppercase tracking-wide">
                    当選番号
                  </p>
                  <p className="font-mono text-4xl font-bold tracking-[0.2em] sm:text-5xl">
                    {winningNorm}
                  </p>
                </div>
                <p className="text-muted-foreground max-w-md text-sm">
                  下のアンサンブル・各手法・予算プランの番号に、緑＝ストレート一致、黄＝桁の並び替え一致（簡易ボックス判定）でマークが付きます。
                </p>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-3">
                <Badge variant="outline" className="text-sm">
                  抽選前 / 未登録
                </Badge>
                <p className="text-muted-foreground text-sm">
                  この回の当選番号がまだ DB に無いため、「あたり」表示はありません。開催後は{" "}
                  <code className="bg-muted rounded px-1 font-mono text-xs">
                    numbers4_draws
                  </code>{" "}
                  に取り込むと自動で照合されます。
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {consensus.length > 0 && (
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="border-border/60 border-b">
              <div className="flex items-center gap-2">
                <SparklesIcon className="text-muted-foreground size-5" />
                <div>
                  <CardTitle className="text-lg">手法横断の合意（上位3候補×複数モデル）</CardTitle>
                  <CardDescription>
                    各 <code className="font-mono text-xs">method</code>{" "}
                    ドキュメントの上位3件から、2つ以上の手法に現れた番号だけ表示
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-0 pb-4 pt-4 sm:px-6">
              <div className="flex flex-wrap gap-2">
                {consensus.slice(0, 24).map((c) => {
                  const hit = classifyHit(c.number, winningRaw);
                  return (
                    <div
                      key={c.number}
                      className={cn(
                        "flex flex-col gap-1 rounded-lg border px-3 py-2",
                        numberCellClass(hit),
                      )}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <PredictionNumberHighlight
                          value={c.number}
                          winningRaw={winningRaw}
                          className="font-mono text-base font-semibold"
                        />
                        <HitBadge kind={hit} className="text-[0.65rem]" />
                        <Badge variant="outline" className="font-mono text-[0.65rem]">
                          {c.supportCount} 手法
                        </Badge>
                      </div>
                      <p className="text-muted-foreground max-w-prose text-[0.7rem] leading-snug">
                        {c.methods.join(", ")}
                      </p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 lg:col-span-2">
            <CardHeader className="border-border/60 border-b">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2">
                  <LayersIcon className="text-muted-foreground size-5" />
                  <div>
                    <CardTitle className="text-lg">アンサンブル</CardTitle>
                    <CardDescription>
                      <code className="font-mono text-xs">doc_kind: ensemble</code>
                      {" · "}
                      相対パス例:{" "}
                      <code className="font-mono text-xs">
                        predictions/daily/numbers4_{data.targetDrawNumber}.json
                      </code>
                      {" · "}
                      最新実行 JST {latest?.time_jst ?? "—"}
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
                    ランキングとあたり
                  </div>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent">
                          <TableHead className="w-12 text-xs">#</TableHead>
                          <TableHead className="text-xs">番号</TableHead>
                          <TableHead className="text-xs">あたり</TableHead>
                          <TableHead className="text-right text-xs">スコア</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topList.length === 0 ? (
                          <TableRow>
                            <TableCell
                              colSpan={4}
                              className="text-muted-foreground h-24 text-center text-sm"
                            >
                              アンサンブル予測がありません
                            </TableCell>
                          </TableRow>
                        ) : (
                          topList.map((row: EnsembleTopPrediction, i: number) => {
                            const num = row.number ?? "";
                            const hit = classifyHit(num, winningRaw);
                            return (
                              <TableRow key={`${row.rank}-${row.number}-${i}`}>
                                <TableCell className="text-muted-foreground tabular-nums">
                                  {row.rank ?? "—"}
                                </TableCell>
                                <TableCell
                                  className={cn(
                                    "font-semibold",
                                    numberCellClass(hit),
                                    "rounded-md",
                                  )}
                                >
                                  <PredictionNumberHighlight
                                    value={row.number}
                                    winningRaw={winningRaw}
                                    className="font-mono"
                                  />
                                </TableCell>
                                <TableCell className="py-2">
                                  <HitBadge kind={hit} className="text-[0.65rem]" />
                                </TableCell>
                                <TableCell className="text-right tabular-nums">
                                  {row.score != null
                                    ? row.score.toLocaleString("ja-JP", {
                                        maximumFractionDigits: 2,
                                      })
                                    : "—"}
                                </TableCell>
                              </TableRow>
                            );
                          })
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
                <div className="border-border/60 px-4 lg:border-l lg:px-6">
                  <div className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide">
                    <BarChart3Icon className="size-3.5" />
                    ensemble_weights（上位）
                  </div>
                  <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
                    {weights.length === 0 ? (
                      <p className="text-muted-foreground text-sm">—</p>
                    ) : (
                      weights.map(([name, w]) => {
                        const ja = getEnsembleWeightJaLabel(name);
                        return (
                          <div
                            key={name}
                            className="flex items-start justify-between gap-3 text-sm"
                          >
                            <span className="text-foreground min-w-0 flex-1 text-xs leading-snug break-words">
                              <span className="font-mono">{name}</span>
                              {ja != null && ja !== "" ? (
                                <span className="text-muted-foreground">
                                  ({ja})
                                </span>
                              ) : null}
                            </span>
                            <span className="text-muted-foreground shrink-0 tabular-nums">
                              {w.toLocaleString("ja-JP", {
                                maximumFractionDigits: 2,
                              })}
                            </span>
                          </div>
                        );
                      })
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
            winning={winningRaw}
          />
          <BudgetPlanCard
            title="予算プラン · 2,000円枠"
            icon={CoinsIcon}
            plan={data.budgetPlan?.plan_10}
            winning={winningRaw}
          />
        </div>

        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 border-b">
            <CardTitle className="text-lg">手法別（method）</CardTitle>
            <CardDescription>
              <code className="font-mono text-xs">doc_kind: method</code>
              {" · "}
              各行が 1 スラッグ＝1 JSON（
              <code className="font-mono text-xs">relative_path</code> 相当）。上位
              5 件を番号チップで表示し、当選と照合します。
            </CardDescription>
          </CardHeader>
          <CardContent className="px-0 pb-4 pt-0 sm:px-0">
            <div className="overflow-x-auto">
              <Table className="min-w-[720px]">
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      method_slug
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      relative_path
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      実行
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      最終 JST
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 text-xs sm:px-6">
                      予測 TOP（スコア付き）
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.methodRows.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={5}
                        className="text-muted-foreground h-20 text-center text-sm"
                      >
                        method 行がありません（未生成か、別回のみ）
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.methodRows.map((m) => (
                      <TableRow key={m.slug} className="border-border/60">
                        <TableCell className="px-4 font-mono text-xs sm:px-6">
                          {m.slug}
                        </TableCell>
                        <TableCell
                          className="text-muted-foreground max-w-[14rem] truncate px-4 font-mono text-[0.65rem] sm:max-w-xs sm:px-6"
                          title={m.relativePath ?? undefined}
                        >
                          {m.relativePath ?? "—"}
                        </TableCell>
                        <TableCell className="px-4 tabular-nums sm:px-6">
                          {m.runs}
                        </TableCell>
                        <TableCell className="text-muted-foreground px-4 text-sm sm:px-6">
                          {m.lastTimeJst ?? "—"}
                        </TableCell>
                        <TableCell className="px-4 py-3 sm:px-6">
                          <div className="flex flex-wrap gap-1.5">
                            {m.topPredictions.slice(0, 5).map((p) => {
                              const hit = classifyHit(p.number, winningRaw);
                              return (
                                <span
                                  key={`${m.slug}-${p.rank}-${p.number}`}
                                  className={cn(
                                    "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 font-mono text-xs",
                                    hit === "none" && "bg-muted/40",
                                    hit === "straight" &&
                                      "border-emerald-600/50 bg-emerald-500/15",
                                    hit === "box" &&
                                      "border-amber-600/50 bg-amber-500/15",
                                  )}
                                >
                                  <span className="tabular-nums">
                                    #{p.rank ?? "—"}
                                  </span>
                                  <PredictionNumberHighlight
                                    value={p.number}
                                    winningRaw={winningRaw}
                                    className="font-mono"
                                  />
                                  {p.score != null && (
                                    <span className="text-muted-foreground text-[0.65rem]">
                                      {p.score.toLocaleString("ja-JP", {
                                        maximumFractionDigits: 1,
                                      })}
                                    </span>
                                  )}
                                  {hit !== "none" && (
                                    <span className="text-[0.6rem] font-normal">
                                      {hit === "straight" ? "◎" : "△"}
                                    </span>
                                  )}
                                </span>
                              );
                            })}
                          </div>
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

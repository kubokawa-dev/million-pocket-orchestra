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
  FlameIcon,
  ArrowRightIcon,
  LightbulbIcon,
  WavesIcon,
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
import {
  contributorsForEnsembleNumber,
  formatContributorSlugLine,
} from "@/lib/numbers4-predictions/ensemble-contributors";
import { getEnsembleWeightJaLabel } from "@/lib/numbers4-predictions/ensemble-weight-labels";
import {
  buildWinningModelHitsForDrawList,
  fetchNumbers4DrawFullRow,
  fetchNumbers4DrawResult,
  fetchOfficialWinningDrawsBeforeTarget,
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
  AllMiniPlanPayload,
  BudgetPlanSlice,
  BudgetRecommendation,
  DistributedPlanPayload,
  EnsembleTopPrediction,
  ExpectedValuePlanSlice,
  HybridPlanPayload,
  MethodPredictionRow,
  MonthlySimulationPayload,
  Numbers4PredictionBundle,
  SetPlanPayload,
} from "@/lib/numbers4-predictions/types";
import { cn } from "@/lib/utils";

import { Numbers4RecentModelHits } from "./result/numbers4-recent-model-hits";
import { EnsembleContributorCell } from "./ensemble-contributor-cell";
import { Numbers4OfficialDrawDetail } from "./numbers4-official-draw-detail";

const ENSEMBLE_SCORE_HEAD_TITLE =
  "各モデルの予測リストの順位を重み付けして合算し、その後に多様性調整・4桁の合計値ボーナス・ボックスタイプの分布調整などを適用した値です。当選確率や期待値ではありません。";

const ENSEMBLE_NEARBY_HEAD_TITLE =
  "メイン候補に近い別4桁の提案です。統計・LightGBMの桁確率などに基づき生成されます。アンサンブル本体のスコアとは別指標です。";

const ENSEMBLE_CONTRIBUTOR_HEAD_TITLE =
  "下の「モデル別」で読み込んだ各モデル直近ランの候補（最大96件）に、この4桁が含まれるかを表示します。「一致」「ボックス」の文字にマウスを載せるかキーボードでフォーカスすると、モデル名がツールチップで開きます（行は展開しません）。";

const ENSEMBLE_WEIGHTS_HEAD_TITLE =
  "アンサンブル集計時に各モデルへ掛け合わせる重みです。学習結果とデフォルト値が混ざっている場合があります。";

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
            <span>ユニークカバー {plan.total_coverage} 通り</span>
          )}
          {plan.probability && (
            <span title={plan.coverage_note}>参考 {plan.probability}</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 pb-4 pt-0">
        {/* Mobile card layout */}
        <div className="max-h-[28rem] space-y-2 overflow-y-auto px-3 pt-3 sm:hidden">
          {recs.map((r: BudgetRecommendation, i: number) => {
            const num = r.number ?? "";
            const hit = classifyHit(num, winningRaw);
            return (
              <div
                key={`${r.number}-${i}`}
                className={cn(
                  "border-border/60 rounded-lg border p-3",
                  numberCellClass(hit),
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground text-xs tabular-nums">
                      #{r.priority ?? "—"}
                    </span>
                    <PredictionNumberHighlight
                      value={r.number}
                      winningRaw={winningRaw}
                      className="font-mono text-base font-semibold"
                    />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <HitBadge kind={hit} className="text-[0.65rem]" />
                    {hit === "none" && winningRaw && (
                      <span className="text-muted-foreground text-xs">—</span>
                    )}
                  </div>
                </div>
                {(r.buy_method || r.reason) && (
                  <div className="mt-2 space-y-1 text-xs">
                    {r.buy_method && (
                      <div className="flex items-baseline gap-1.5">
                        <span className="text-muted-foreground shrink-0">買い方:</span>
                        <span className="text-foreground">
                          {r.buy_method}
                          {r.box_type && (
                            <span className="text-muted-foreground ml-1 text-[0.65rem]">
                              ({r.box_type})
                            </span>
                          )}
                        </span>
                      </div>
                    )}
                    {r.reason && (
                      <p className="text-muted-foreground leading-snug">
                        {r.reason}
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {/* Desktop table layout */}
        <div className="hidden sm:block">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="text-muted-foreground w-14 px-4 text-xs">
                  順
                </TableHead>
                <TableHead className="text-muted-foreground px-4 text-xs">
                  番号
                </TableHead>
                <TableHead className="text-muted-foreground px-4 text-xs">
                  あたり
                </TableHead>
                <TableHead className="text-muted-foreground px-4 text-xs">
                  買い方
                </TableHead>
                <TableHead className="text-muted-foreground hidden px-4 text-xs md:table-cell">
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
                    <TableCell className="text-muted-foreground px-4 py-2.5 text-xs">
                      {r.priority ?? `—`}
                    </TableCell>
                    <TableCell
                      className={cn(
                        "rounded-md px-4 py-2.5 text-sm font-semibold",
                        numberCellClass(hit),
                      )}
                    >
                      <PredictionNumberHighlight
                        value={r.number}
                        winningRaw={winningRaw}
                        className="font-mono"
                      />
                    </TableCell>
                    <TableCell className="px-4 py-2.5">
                      <HitBadge kind={hit} className="text-[0.65rem]" />
                      {hit === "none" && winningRaw && (
                        <span className="text-muted-foreground text-xs">—</span>
                      )}
                    </TableCell>
                    <TableCell className="px-4 py-2.5 text-xs">
                      <span className="text-foreground">{r.buy_method ?? "—"}</span>
                      {r.box_type && (
                        <span className="text-muted-foreground block text-[0.65rem]">
                          {r.box_type}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground hidden max-w-[14rem] truncate px-4 py-2.5 text-xs md:table-cell md:max-w-none md:whitespace-normal">
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

/** v15: ハイブリッドプラン表示 */
function HybridPlanCard({
  title,
  plan,
  winning: winningRaw,
}: {
  title: string;
  plan: HybridPlanPayload | undefined;
  winning: string | null;
}) {
  if (!plan) return null;
  const boxRecs = plan.box_recommendations ?? [];
  const miniRecs = plan.mini_recommendations ?? [];
  if (boxRecs.length === 0 && miniRecs.length === 0) return null;

  return (
    <Card className="border-border/80 h-full shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <TargetIcon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          <span>{plan.total_budget}</span>
          <span>
            BOX {plan.box_slots}口 + MINI {plan.mini_slots}口
          </span>
        </CardDescription>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge variant="outline" className="text-[0.65rem]">
            BOX {plan.box_probability}
          </Badge>
          <Badge variant="outline" className="text-[0.65rem]">
            MINI {plan.mini_probability}
          </Badge>
          <Badge variant="default" className="text-[0.65rem]">
            合計 {plan.combined_probability}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 px-3 pb-4 pt-3">
        {boxRecs.length > 0 && (
          <div>
            <p className="text-muted-foreground mb-1.5 text-xs font-medium">
              BOX ({plan.box_slots}口)
            </p>
            <div className="space-y-1.5">
              {boxRecs.map((r, i) => {
                const hit = classifyHit(r.number ?? "", winningRaw);
                return (
                  <div
                    key={`box-${r.number}-${i}`}
                    className={cn(
                      "border-border/60 flex items-center justify-between rounded border px-2.5 py-1.5",
                      numberCellClass(hit),
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground text-[0.65rem]">
                        {r.priority}
                      </span>
                      <PredictionNumberHighlight
                        value={r.number}
                        winningRaw={winningRaw}
                        className="font-mono text-sm font-semibold"
                      />
                      <span className="text-muted-foreground text-[0.6rem]">
                        {r.box_type} +{r.coverage}通り
                      </span>
                    </div>
                    <HitBadge kind={hit} className="text-[0.6rem]" />
                  </div>
                );
              })}
            </div>
          </div>
        )}
        {miniRecs.length > 0 && (
          <div>
            <p className="text-muted-foreground mb-1.5 text-xs font-medium">
              MINI ({plan.mini_slots}口) — 下2桁一致で当選 (1/100)
            </p>
            <div className="space-y-1.5">
              {miniRecs.map((r, i) => (
                <div
                  key={`mini-${r.number}-${i}`}
                  className="border-border/60 flex items-center justify-between rounded border px-2.5 py-1.5"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground text-[0.65rem]">
                      {r.priority}
                    </span>
                    <span className="font-mono text-sm">
                      <span className="text-muted-foreground/50">
                        {(r.number ?? "").slice(0, 2)}
                      </span>
                      <span className="font-semibold">
                        {(r.number ?? "").slice(2)}
                      </span>
                    </span>
                    <span className="text-muted-foreground text-[0.6rem]">
                      {r.box_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/** v15: 分散購入プラン表示 */
function DistributedPlanCard({
  plan,
  winning: winningRaw,
}: {
  plan: DistributedPlanPayload | undefined;
  winning: string | null;
}) {
  if (!plan || !plan.schedule?.length) return null;

  return (
    <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 lg:col-span-2">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <LayersIcon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">
            分散購入プラン（独立試行で確率UP）
          </CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          <span>{plan.total_budget}</span>
          <span>
            {plan.sessions}回 x {plan.tickets_per_session}口
          </span>
          <span>累積 {plan.cumulative_unique_coverage}通り</span>
        </CardDescription>
        <div className="mt-2">
          <Badge variant="default" className="text-[0.65rem]">
            月間当選確率 {plan.monthly_hit_probability}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="px-3 pb-4 pt-3">
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {plan.schedule.map((s) => (
            <div
              key={s.session}
              className="border-border/60 rounded-lg border p-2.5"
            >
              <p className="text-muted-foreground mb-1.5 text-[0.65rem] font-medium">
                第{s.session}回 · {s.budget} · +{s.session_coverage}通り
              </p>
              <div className="space-y-1">
                {(s.picks ?? []).map((p, i) => {
                  const hit = classifyHit(p.number ?? "", winningRaw);
                  return (
                    <div
                      key={`${p.number}-${i}`}
                      className={cn(
                        "flex items-center justify-between gap-1 text-xs",
                        numberCellClass(hit),
                      )}
                    >
                      <PredictionNumberHighlight
                        value={p.number}
                        winningRaw={winningRaw}
                        className="font-mono font-semibold"
                      />
                      <span className="text-muted-foreground text-[0.6rem]">
                        {p.box_type}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** v15: 期待値プラン表示 */
function ExpectedValuePlanCard({
  title,
  plan,
  winning: winningRaw,
}: {
  title: string;
  plan: ExpectedValuePlanSlice | undefined;
  winning: string | null;
}) {
  const recs = plan?.recommendations ?? [];
  if (!plan || recs.length === 0) return null;

  return (
    <Card className="border-border/80 h-full shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <BarChart3Icon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          <span>{plan.budget}</span>
          {plan.total_expected_value != null && (
            <span>
              合計期待値{" "}
              <span className="tabular-nums">
                {plan.total_expected_value > 0 ? "+" : ""}
                {plan.total_expected_value.toLocaleString("ja-JP")}円
              </span>
            </span>
          )}
          {plan.total_coverage != null && (
            <span>カバー {plan.total_coverage}通り</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-3 pb-4 pt-3">
        <div className="space-y-1.5">
          {recs.map((r, i) => {
            const hit = classifyHit(r.number ?? "", winningRaw);
            return (
              <div
                key={`ev-${r.number}-${i}`}
                className={cn(
                  "border-border/60 flex items-center justify-between rounded border px-2.5 py-1.5",
                  numberCellClass(hit),
                )}
              >
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground text-[0.65rem]">
                    {r.priority}
                  </span>
                  <PredictionNumberHighlight
                    value={r.number}
                    winningRaw={winningRaw}
                    className="font-mono text-sm font-semibold"
                  />
                  <span className="text-muted-foreground text-[0.6rem]">
                    {r.box_type}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <HitBadge kind={hit} className="text-[0.6rem]" />
                  {r.box_payout != null && (
                    <span className="text-muted-foreground text-[0.6rem] tabular-nums">
                      {r.box_payout.toLocaleString("ja-JP")}円
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/** v16: オールミニプラン表示 */
function AllMiniPlanCard({
  plan,
  winning: winningRaw,
}: {
  plan: AllMiniPlanPayload | undefined;
  winning: string | null;
}) {
  const recs = plan?.recommendations ?? [];
  if (!plan || recs.length === 0) return null;

  return (
    <Card className="border-border/80 h-full shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <SparklesIcon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">
            オールミニ（月間当選確率MAX）
          </CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          <span>{plan.total_budget}/回</span>
          <span>{plan.slots}口</span>
          {plan.mini_payout_estimate && (
            <span>配当目安 {plan.mini_payout_estimate}</span>
          )}
        </CardDescription>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge variant="outline" className="text-[0.65rem]">
            1回 {plan.per_draw_probability}
          </Badge>
          <Badge variant="default" className="bg-green-600 text-[0.65rem]">
            月間 {plan.monthly_probability}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="px-3 pb-4 pt-3">
        <div className="space-y-1.5">
          {recs.map((r, i) => (
            <div
              key={`mini-all-${r.number}-${i}`}
              className="border-border/60 flex items-center justify-between rounded border px-2.5 py-1.5"
            >
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground text-[0.65rem]">
                  {r.priority}
                </span>
                <span className="font-mono text-sm">
                  <span className="text-muted-foreground/50">
                    {(r.number ?? "").slice(0, 2)}
                  </span>
                  <span className="font-semibold">
                    {(r.number ?? "").slice(2)}
                  </span>
                </span>
                <span className="text-muted-foreground text-[0.6rem]">
                  {r.box_type}
                </span>
              </div>
              <span className="text-muted-foreground text-[0.6rem]">
                {r.reason?.split(" / ").find((s) => s.includes("過去")) ?? ""}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** v16: セット購入プラン表示 */
function SetPlanCard({
  title,
  plan,
  winning: winningRaw,
}: {
  title: string;
  plan: SetPlanPayload | undefined;
  winning: string | null;
}) {
  const recs = plan?.recommendations ?? [];
  if (!plan || recs.length === 0) return null;

  return (
    <Card className="border-border/80 h-full shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <ListOrderedIcon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
        <CardDescription className="flex flex-wrap gap-x-3 gap-y-1 text-xs sm:text-sm">
          <span>{plan.total_budget}</span>
          <span>{plan.slots}口 (1口400円)</span>
          {plan.total_coverage != null && (
            <span>カバー {plan.total_coverage}通り</span>
          )}
          {plan.probability && <span>({plan.probability})</span>}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-3 pb-4 pt-3">
        <div className="space-y-1.5">
          {recs.map((r, i) => {
            const hit = classifyHit(r.number ?? "", winningRaw);
            return (
              <div
                key={`set-${r.number}-${i}`}
                className={cn(
                  "border-border/60 rounded border px-2.5 py-1.5",
                  numberCellClass(hit),
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground text-[0.65rem]">
                      {r.priority}
                    </span>
                    <PredictionNumberHighlight
                      value={r.number}
                      winningRaw={winningRaw}
                      className="font-mono text-sm font-semibold"
                    />
                    <span className="text-muted-foreground text-[0.6rem]">
                      {r.box_type} +{r.coverage}通り
                    </span>
                  </div>
                  <HitBadge kind={hit} className="text-[0.6rem]" />
                </div>
                {(r as Record<string, unknown>).set_straight_payout != null && (
                  <p className="text-muted-foreground mt-0.5 text-[0.6rem]">
                    ST的中:{" "}
                    {(
                      (r as Record<string, unknown>)
                        .set_straight_payout as number
                    ).toLocaleString("ja-JP")}
                    円 / BOX的中:{" "}
                    {(
                      (r as Record<string, unknown>).set_box_payout as number
                    ).toLocaleString("ja-JP")}
                    円
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/** v16: 月間確率シミュレーション表示 */
function MonthlySimulationCard({
  simulation,
}: {
  simulation: MonthlySimulationPayload | undefined;
}) {
  if (!simulation?.strategies?.length) return null;

  return (
    <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 lg:col-span-2">
      <CardHeader className="border-border/60 border-b pb-4">
        <div className="flex items-center gap-2">
          <BarChart3Icon className="text-muted-foreground size-4" />
          <CardTitle className="text-base">
            月間確率シミュレーション（全戦略比較）
          </CardTitle>
        </div>
        <CardDescription className="text-xs">
          平日{simulation.draws_per_month}回/月で「1回以上当選する確率」を計算
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 pb-4 pt-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="text-muted-foreground w-10 px-3 text-xs">
                #
              </TableHead>
              <TableHead className="text-muted-foreground px-3 text-xs">
                戦略
              </TableHead>
              <TableHead className="text-muted-foreground px-3 text-xs">
                1回の予算
              </TableHead>
              <TableHead className="text-muted-foreground px-3 text-xs">
                1回の確率
              </TableHead>
              <TableHead className="text-muted-foreground px-3 text-xs">
                月間確率
              </TableHead>
              <TableHead className="text-muted-foreground hidden px-3 text-xs md:table-cell">
                配当
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {simulation.strategies.map((s, i) => {
              const raw = s.monthly_probability_raw ?? 0;
              const barWidth = Math.min(raw * 100, 100);
              return (
                <TableRow
                  key={s.name}
                  className={cn(
                    "border-border/60",
                    i === 0 && "bg-green-50/50 dark:bg-green-950/20",
                  )}
                >
                  <TableCell className="text-muted-foreground px-3 py-2.5 text-xs tabular-nums">
                    {i + 1}
                  </TableCell>
                  <TableCell className="px-3 py-2.5 text-xs font-medium">
                    {s.name}
                  </TableCell>
                  <TableCell className="text-muted-foreground px-3 py-2.5 text-xs tabular-nums">
                    {s.budget_per_draw}
                  </TableCell>
                  <TableCell className="text-muted-foreground px-3 py-2.5 text-xs tabular-nums">
                    {s.per_draw_probability}
                  </TableCell>
                  <TableCell className="px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold tabular-nums">
                        {s.monthly_probability}
                      </span>
                      <div className="bg-muted hidden h-2 w-16 overflow-hidden rounded-full sm:block">
                        <div
                          className="h-full rounded-full bg-green-500"
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground hidden px-3 py-2.5 text-xs md:table-cell">
                    {s.payout_type}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function EnsembleNearbyDetails({
  patterns,
  winningRaw,
}: {
  patterns: NonNullable<EnsembleTopPrediction["similar_patterns"]>;
  winningRaw: string | null;
}) {
  return (
    <details className="text-xs">
      <summary
        className="text-muted-foreground cursor-pointer list-none py-0.5 marker:content-none [&::-webkit-details-marker]:hidden"
        title={ENSEMBLE_NEARBY_HEAD_TITLE}
      >
        近傍 {patterns.length} 件
      </summary>
      <ul className="border-border/60 mt-1 max-h-36 max-w-full space-y-1 overflow-y-auto border-t pt-1">
        {patterns.slice(0, 8).map((sp, si) => (
          <li
            key={`${sp.number}-${si}`}
            className="text-muted-foreground leading-snug"
          >
            <PredictionNumberHighlight
              value={sp.number}
              winningRaw={winningRaw}
              className="font-mono text-foreground"
            />
            {sp.score != null && (
              <span className="ml-1 tabular-nums">
                (
                {sp.score.toLocaleString("ja-JP", {
                  maximumFractionDigits: 2,
                })}
                )
              </span>
            )}
            {sp.description != null && sp.description !== "" && (
              <span className="mt-0.5 block text-[0.65rem] opacity-90">
                {sp.description}
              </span>
            )}
          </li>
        ))}
      </ul>
    </details>
  );
}

/** モデルカード内で見せる予測行の上限（JSON からは最大 96 件まで読み込み） */
const METHOD_MODEL_TABLE_MAX_ROWS = 16;

function MethodModelDetailCard({
  row,
  winningRaw,
}: {
  row: MethodPredictionRow;
  winningRaw: string | null;
}) {
  const ja = getEnsembleWeightJaLabel(row.slug);
  const preds = row.topPredictions.slice(0, METHOD_MODEL_TABLE_MAX_ROWS);

  return (
    <Card className="border-border/80 flex h-full flex-col shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 space-y-1 border-b pb-3">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
          <CardTitle className="font-mono text-base leading-tight">
            {row.slug}
          </CardTitle>
          {ja != null && ja !== "" ? (
            <Badge variant="secondary" className="font-normal">
              {ja}
            </Badge>
          ) : null}
        </div>
        <CardDescription className="text-xs leading-relaxed">
          <span className="text-muted-foreground">
            実行 {row.runs} 回 · 最終 JST {row.lastTimeJst ?? "—"}
          </span>
          {row.relativePath != null && row.relativePath !== "" ? (
            <span
              className="text-muted-foreground mt-1 block truncate font-mono text-[0.65rem]"
              title={row.relativePath}
            >
              {row.relativePath}
            </span>
          ) : null}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col px-0 pb-3 pt-0">
        {preds.length === 0 ? (
          <p className="text-muted-foreground px-4 py-6 text-center text-sm">
            このモデルは直近ランで候補がありません
          </p>
        ) : (
          <div className="max-h-[22rem] overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-muted-foreground w-11 px-2 text-xs">
                    #
                  </TableHead>
                  <TableHead className="text-muted-foreground px-2 text-xs">
                    番号
                  </TableHead>
                  <TableHead className="text-muted-foreground px-2 text-right text-xs">
                    スコア
                  </TableHead>
                  <TableHead className="text-muted-foreground w-14 px-2 text-xs">
                    照合
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {preds.map((p, i) => {
                  const hit = classifyHit(p.number, winningRaw);
                  return (
                    <TableRow
                      key={`${row.slug}-${p.rank}-${p.number}-${i}`}
                      className="border-border/60"
                    >
                      <TableCell className="text-muted-foreground px-2 py-2 tabular-nums text-xs">
                        {p.rank ?? i + 1}
                      </TableCell>
                      <TableCell
                        className={cn(
                          "px-2 py-2 font-mono text-sm font-semibold",
                          numberCellClass(hit),
                          "rounded-md",
                        )}
                      >
                        <PredictionNumberHighlight
                          value={p.number}
                          winningRaw={winningRaw}
                          className="font-mono"
                        />
                      </TableCell>
                      <TableCell className="text-muted-foreground px-2 py-2 text-right tabular-nums text-xs">
                        {p.score != null
                          ? p.score.toLocaleString("ja-JP", {
                              maximumFractionDigits: 2,
                            })
                          : "—"}
                      </TableCell>
                      <TableCell className="px-2 py-2">
                        <HitBadge kind={hit} className="text-[0.6rem]" />
                        {hit === "none" && winningRaw && (
                          <span className="text-muted-foreground text-[0.6rem]">
                            —
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
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
  const hotModels = latest?.hot_models || [];
  const recentFlow = [...(latest?.recent_flow ?? [])].sort(
    (a, b) => (a.draw ?? 0) - (b.draw ?? 0),
  );
  const nextPredictions = latest?.next_model_predictions || [];

  const consensus = buildMethodConsensus(data.methodRows, 3);

  const winningModelContrib =
    winningNorm && data.methodRows.length > 0
      ? contributorsForEnsembleNumber(winningNorm, data.methodRows)
      : null;

  const officialPastFiveDraws = await fetchOfficialWinningDrawsBeforeTarget(
    data.targetDrawNumber,
    5,
  );
  const officialPastFiveHits = await buildWinningModelHitsForDrawList(
    officialPastFiveDraws,
  );

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
              第 {data.targetDrawNumber} 回 ナンバーズ4｜予測と当選照合
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

        <Numbers4RecentModelHits
          hits={officialPastFiveHits}
          emphasizeOfficial
          title={`第 ${data.targetDrawNumber} 回の直前 · 公式当選5回 × モデル照合`}
          description={
            <>
              <span className="block">
                いま見ている対象が第 {data.targetDrawNumber} 回なので、
                <strong className="text-foreground">
                  その一つ前の回からさかのぼって最大5回分
                </strong>
                （いずれも第 {data.targetDrawNumber} 回より前で、すでに当選番号が{" "}
                <code className="font-mono text-xs">numbers4_draws</code>{" "}
                に入っている回だけ）の
                <strong className="text-foreground">実際の当選4桁</strong>
                を1行ずつ取り、
                <strong className="text-foreground">同じ回号の</strong>{" "}
                <code className="font-mono text-xs">method</code>{" "}
                予測と突き合わせています。
              </span>
              <span className="block">
                当選数字はすべて{" "}
                <code className="font-mono text-xs">numbers4_draws</code>{" "}
                の抽選結果です。下のアンサンブル上位から数字を選んでいるわけではありません。
              </span>
            </>
          }
          bannerLead={`表示順は新しい回が上です（全 ${officialPastFiveHits.length} 行）。`}
          emptyMessage="直前5回の公式当選がまだ DB に無いか、Supabase に接続できていません。"
        />

        {winningNorm ? (
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="border-border/60 border-b pb-3">
              <div className="flex flex-wrap items-center gap-2">
                <LayersIcon className="text-muted-foreground size-5" />
                <div>
                  <CardTitle className="text-lg">
                    第 {data.targetDrawNumber} 回の公式当選が、各モデル候補に載っていたか
                  </CardTitle>
                  <CardDescription className="text-pretty mt-1 text-sm">
                    <span className="block">
                      照合の左側にある当選{" "}
                      <span className="font-mono">{winningNorm}</span> は{" "}
                      <code className="font-mono text-xs">numbers4_draws</code>{" "}
                      の<strong className="text-foreground">実抽選結果</strong>
                      です。
                    </span>
                    <span className="block">
                      各 <code className="font-mono text-xs">method</code> の
                      <strong className="text-foreground">
                        この回向け
                      </strong>
                      直近ラン上位候補（最大96件）に、その数字が含まれていたかを出しています（下の「モデル別」と同じデータ）。
                    </span>
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pb-6 pt-2">
              {winningModelContrib == null ? (
                <p className="text-muted-foreground text-sm">
                  この回の method 予測が無いため、モデル別との照合はできません。
                </p>
              ) : (
                <div className="space-y-4">
                  <div>
                    <p className="text-muted-foreground mb-2 text-xs font-medium uppercase tracking-wide">
                      ストレート一致
                    </p>
                    {winningModelContrib.exactSlugs.length === 0 ? (
                      <p className="text-muted-foreground text-sm">該当なし</p>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {winningModelContrib.exactSlugs.map((s) => (
                          <Badge
                            key={s}
                            variant="outline"
                            className="border-emerald-600/40 bg-emerald-500/10 font-mono text-[0.7rem] font-normal text-emerald-950 dark:text-emerald-100"
                            title={formatContributorSlugLine(s)}
                          >
                            {s}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-2 text-xs font-medium uppercase tracking-wide">
                      ボックス相当のみ（完全一致の候補は無いが並び替えはリスト内）
                    </p>
                    {winningModelContrib.boxOnlySlugs.length === 0 ? (
                      <p className="text-muted-foreground text-sm">該当なし</p>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {winningModelContrib.boxOnlySlugs.map((s) => (
                          <Badge
                            key={s}
                            variant="outline"
                            className="border-amber-600/40 bg-amber-500/10 font-mono text-[0.7rem] font-normal text-amber-950 dark:text-amber-100"
                            title={formatContributorSlugLine(s)}
                          >
                            {s}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ) : null}

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
              <div className="text-muted-foreground border-border/60 bg-muted/30 mx-4 mb-4 space-y-2 rounded-lg border px-3 py-2.5 text-xs leading-relaxed sm:mx-6">
                <p>
                  <strong className="text-foreground">統合スコア</strong>
                  列は、多数の予測モデルの
                  <strong className="text-foreground"> 順位を重み付けして合算 </strong>
                  したうえで、多様性・4桁の合計値・ボックスタイプの分布などを調整した値です。
                  <strong className="text-foreground"> 当選確率ではありません。</strong>
                  列見出しにカーソルを置くと同じ説明が表示されます。
                </p>
                <p>
                  <strong className="text-foreground">寄与モデル</strong>
                  は、このページで読み込んだ「モデル別」各モデルの直近ラン候補（最大96件）との照合です。
                  <strong className="text-foreground">「一致」「ボックス」</strong>
                  にカーソルを載せる（または Tab でフォーカス）とモデル名がツールチップで表示されます。クリックで行が伸びることはありません。集計パイプライン内部の票とは完全一致しない場合があります。
                </p>
                {/* 寄与モデル横の ? ヘルプは一旦オフ（復帰時は HelpTooltip + CircleHelpIcon） */}
              </div>
              <div className="grid gap-6 lg:grid-cols-2">
                <div className="px-4 sm:px-6">
                  <div className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide">
                    <ListOrderedIcon className="size-3.5" />
                    ランキングとあたり
                  </div>
                  {/* Mobile card layout */}
                  <div className="space-y-2 sm:hidden">
                    {topList.length === 0 ? (
                      <p className="text-muted-foreground py-8 text-center text-sm">
                        アンサンブル予測がありません
                      </p>
                    ) : (
                      topList.map((row: EnsembleTopPrediction, i: number) => {
                        const num = row.number ?? "";
                        const hit = classifyHit(num, winningRaw);
                        const norm = normalizeNumbers4(num) ?? "";
                        const contrib = contributorsForEnsembleNumber(
                          norm || num,
                          data.methodRows,
                        );
                        return (
                          <div
                            key={`${row.rank}-${row.number}-${i}`}
                            className={cn(
                              "border-border/60 rounded-lg border p-3",
                              numberCellClass(hit),
                            )}
                          >
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="text-muted-foreground text-xs tabular-nums">
                                  #{row.rank ?? "—"}
                                </span>
                                <PredictionNumberHighlight
                                  value={row.number}
                                  winningRaw={winningRaw}
                                  className="font-mono text-base font-semibold"
                                />
                                <HitBadge kind={hit} className="text-[0.65rem]" />
                              </div>
                              <span
                                className="text-muted-foreground text-xs tabular-nums"
                                title={ENSEMBLE_SCORE_HEAD_TITLE}
                              >
                                {row.score != null
                                  ? row.score.toLocaleString("ja-JP", {
                                      maximumFractionDigits: 2,
                                    })
                                  : "—"}
                              </span>
                            </div>
                            <div className="mt-2 space-y-1.5">
                              <EnsembleContributorCell
                                exactSlugs={contrib.exactSlugs}
                                boxOnlySlugs={contrib.boxOnlySlugs}
                              />
                              {row.similar_patterns &&
                              row.similar_patterns.length > 0 ? (
                                <EnsembleNearbyDetails
                                  patterns={row.similar_patterns}
                                  winningRaw={winningRaw}
                                />
                              ) : null}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                  {/* Desktop table layout */}
                  <div className="hidden overflow-x-auto sm:block">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent">
                          <TableHead className="w-12 text-xs">#</TableHead>
                          <TableHead className="text-xs">番号</TableHead>
                          <TableHead className="text-xs">あたり</TableHead>
                          <TableHead
                            className="text-right text-xs"
                            title={ENSEMBLE_SCORE_HEAD_TITLE}
                          >
                            統合スコア
                          </TableHead>
                          <TableHead
                            className="hidden min-w-[6.5rem] text-xs md:table-cell"
                            title={ENSEMBLE_CONTRIBUTOR_HEAD_TITLE}
                          >
                            寄与モデル
                          </TableHead>
                          <TableHead
                            className="hidden min-w-[7rem] text-xs lg:table-cell"
                            title={ENSEMBLE_NEARBY_HEAD_TITLE}
                          >
                            近傍
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topList.length === 0 ? (
                          <TableRow>
                            <TableCell
                              colSpan={6}
                              className="text-muted-foreground h-24 text-center text-sm"
                            >
                              アンサンブル予測がありません
                            </TableCell>
                          </TableRow>
                        ) : (
                          topList.map((row: EnsembleTopPrediction, i: number) => {
                            const num = row.number ?? "";
                            const hit = classifyHit(num, winningRaw);
                            const norm = normalizeNumbers4(num) ?? "";
                            const contrib = contributorsForEnsembleNumber(
                              norm || num,
                              data.methodRows,
                            );
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
                                  <div className="flex flex-col gap-1">
                                    <PredictionNumberHighlight
                                      value={row.number}
                                      winningRaw={winningRaw}
                                      className="font-mono"
                                    />
                                    <div className="md:hidden">
                                      <EnsembleContributorCell
                                        exactSlugs={contrib.exactSlugs}
                                        boxOnlySlugs={contrib.boxOnlySlugs}
                                      />
                                    </div>
                                    {row.similar_patterns &&
                                    row.similar_patterns.length > 0 ? (
                                      <div className="lg:hidden">
                                        <EnsembleNearbyDetails
                                          patterns={row.similar_patterns}
                                          winningRaw={winningRaw}
                                        />
                                      </div>
                                    ) : null}
                                  </div>
                                </TableCell>
                                <TableCell className="py-2">
                                  <HitBadge kind={hit} className="text-[0.65rem]" />
                                </TableCell>
                                <TableCell
                                  className="text-right tabular-nums"
                                  title={ENSEMBLE_SCORE_HEAD_TITLE}
                                >
                                  {row.score != null
                                    ? row.score.toLocaleString("ja-JP", {
                                        maximumFractionDigits: 2,
                                      })
                                    : "—"}
                                </TableCell>
                                <TableCell className="hidden align-top md:table-cell">
                                  <EnsembleContributorCell
                                    exactSlugs={contrib.exactSlugs}
                                    boxOnlySlugs={contrib.boxOnlySlugs}
                                  />
                                </TableCell>
                                <TableCell className="hidden align-top lg:table-cell">
                                  {row.similar_patterns &&
                                  row.similar_patterns.length > 0 ? (
                                    <EnsembleNearbyDetails
                                      patterns={row.similar_patterns}
                                      winningRaw={winningRaw}
                                    />
                                  ) : (
                                    <span className="text-muted-foreground">
                                      —
                                    </span>
                                  )}
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
                  <div
                    className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide"
                    title={ENSEMBLE_WEIGHTS_HEAD_TITLE}
                  >
                    <BarChart3Icon className="size-3.5" />
                    モデル別の重み（上位）
                  </div>
                  <p className="text-muted-foreground mb-2 text-[0.7rem] leading-snug">
                    <code className="font-mono text-[0.65rem]">ensemble_weights</code>
                    。英字キーは開発用ID、括弧内は日本語の意味です。
                  </p>
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

                  {hotModels.length > 0 && (
                    <div className="mt-8">
                      <div
                        className="text-orange-600 dark:text-orange-400 mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide"
                        title="直近50回の成績から算出したトレンドスコア"
                      >
                        <FlameIcon className="size-3.5" />
                        Hot Model トレンド
                      </div>
                      <p className="text-muted-foreground mb-3 text-[0.7rem] leading-snug">
                        直近50回で最も成績が良かったモデルのランキングです。上位モデルには予測時にボーナスが加算されます。
                      </p>
                      <div className="max-h-64 space-y-2.5 overflow-y-auto pr-1">
                        {hotModels.slice(0, 5).map((item, index) => {
                          const maxScore = hotModels[0].score || 1;
                          const percentage = Math.max(2, (item.score / maxScore) * 100);
                          const ja = getEnsembleWeightJaLabel(item.model);
                          
                          let medal = "✨";
                          if (index === 0) medal = "🥇";
                          else if (index === 1) medal = "🥈";
                          else if (index === 2) medal = "🥉";

                          return (
                            <div key={item.model} className="space-y-1">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-foreground min-w-0 flex-1 leading-snug break-words flex items-center gap-1.5">
                                  <span className="w-4 text-center">{medal}</span>
                                  <span className="font-mono">{item.model}</span>
                                </span>
                                <span className="text-muted-foreground shrink-0 tabular-nums">
                                  {item.score.toFixed(1)}
                                </span>
                              </div>
                              <div className="bg-muted h-1.5 w-full overflow-hidden rounded-full ml-5.5">
                                <div
                                  className={cn(
                                    "h-full rounded-full transition-all",
                                    index === 0 ? "bg-orange-500" : 
                                    index < 3 ? "bg-orange-400/70" : "bg-primary/40"
                                  )}
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-3">
                        <Link
                          href="/numbers4/trend"
                          className="text-orange-600 hover:text-orange-700 dark:text-orange-400 dark:hover:text-orange-300 text-xs font-medium flex items-center gap-1"
                        >
                          すべてのトレンドを見る
                          <ArrowRightIcon className="size-3" />
                        </Link>
                      </div>
                    </div>
                  )}

                  {recentFlow.length > 0 && (
                    <div className="mt-8 border-t border-border/60 pt-6">
                      <div
                        className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide"
                        title="各抽選回で評価スコアが最も高かったモデル（直近の履歴）"
                      >
                        <WavesIcon className="size-3.5 text-sky-500" />
                        直近の各回チャンプ
                      </div>
                      <p className="text-muted-foreground mb-3 text-[0.7rem] leading-snug">
                        回ごとに「その回の当選に対して一番当たりが良かった」モデルIDです。箇条書きは{" "}
                        <code className="font-mono text-[0.65rem]">第○回: slug</code>{" "}
                        の形（トレンドページでも同じデータを見られます）。
                      </p>
                      <ul className="max-h-56 space-y-1.5 overflow-y-auto pr-1 font-mono text-[0.7rem] leading-relaxed">
                        {recentFlow.map((flow) => {
                          const ja = getEnsembleWeightJaLabel(flow.model);
                          return (
                            <li
                              key={flow.draw}
                              className="text-foreground flex flex-wrap items-baseline gap-x-2 gap-y-0.5"
                            >
                              <span className="text-muted-foreground shrink-0">
                                • 第{flow.draw}回:
                              </span>
                              <span className="text-foreground">{flow.model}</span>
                              {ja != null && ja !== "" ? (
                                <span className="text-muted-foreground font-sans text-[0.65rem]">
                                  ({ja})
                                </span>
                              ) : null}
                              {flow.score != null ? (
                                <span className="text-muted-foreground font-sans text-[0.65rem] tabular-nums">
                                  {flow.score.toLocaleString("ja-JP", {
                                    maximumFractionDigits: 2,
                                  })}
                                </span>
                              ) : null}
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}

                  {nextPredictions.length > 0 && (
                    <div className="mt-8 border-t border-border/60 pt-6">
                      <div
                        className="text-blue-600 dark:text-blue-400 mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide"
                        title="過去の遷移パターンから算出した次回当たりやすいモデル"
                      >
                        <LightbulbIcon className="size-3.5" />
                        次回（第 {data.targetDrawNumber} 回）の最強モデル予測
                      </div>
                      <p className="text-muted-foreground mb-3 text-[0.7rem] leading-snug">
                        過去50回の遷移パターンから、前回（第 {data.targetDrawNumber - 1} 回）の最強モデルの次に当たりやすいモデルを予測しています。
                      </p>
                      <div className="space-y-2.5">
                        {nextPredictions.map((pred, i) => (
                          <div key={pred.model} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-foreground min-w-0 flex-1 leading-snug break-words flex items-center gap-1.5">
                                <span className="w-4 text-center">{i === 0 ? "🎯" : "✨"}</span>
                                <span className="font-mono">{pred.model}</span>
                              </span>
                              <span className="text-muted-foreground text-[0.65rem]">
                                確率: {(pred.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="bg-muted h-1 w-full overflow-hidden rounded-full ml-5.5">
                              <div
                                className={cn(
                                  "h-full rounded-full transition-all",
                                  i === 0 ? "bg-blue-500" : "bg-blue-400/50"
                                )}
                                style={{ width: `${Math.max(2, pred.probability * 100)}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {data.budgetPlan?.monthly_budget_guide != null && (
            <div className="border-border/60 bg-muted/25 text-muted-foreground rounded-lg border px-4 py-3 text-xs leading-relaxed lg:col-span-2">
              <p className="text-foreground mb-1 font-medium">月間の目安（v16 プラン）</p>
              <p>
                上限{" "}
                <span className="tabular-nums">
                  {data.budgetPlan.monthly_budget_guide.max_yen_per_month?.toLocaleString("ja-JP")}
                </span>
                円/月 · 基本{" "}
                {data.budgetPlan.monthly_budget_guide.default_per_draw_yen?.toLocaleString("ja-JP")}
                円（{data.budgetPlan.monthly_budget_guide.slots_for_1000yen}口）· 最大{" "}
                {data.budgetPlan.monthly_budget_guide.max_per_draw_yen?.toLocaleString("ja-JP")}
                円（{data.budgetPlan.monthly_budget_guide.slots_for_2000yen}口）
              </p>
              {data.budgetPlan.monthly_budget_guide.daily_full_month_hint ? (
                <p className="mt-1.5">
                  {data.budgetPlan.monthly_budget_guide.daily_full_month_hint}
                </p>
              ) : null}
            </div>
          )}

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

          {/* v15: ハイブリッドプラン（ボックス＋ミニ） */}
          <HybridPlanCard
            title="ハイブリッド · 1,000円枠"
            plan={data.budgetPlan?.hybrid_5}
            winning={winningRaw}
          />
          <HybridPlanCard
            title="ハイブリッド · 2,000円枠"
            plan={data.budgetPlan?.hybrid_10}
            winning={winningRaw}
          />

          {/* v15: 期待値プラン */}
          <ExpectedValuePlanCard
            title="期待値重視 · 1,000円枠"
            plan={data.budgetPlan?.expected_value_5}
            winning={winningRaw}
          />
          <ExpectedValuePlanCard
            title="期待値重視 · 2,000円枠"
            plan={data.budgetPlan?.expected_value_10}
            winning={winningRaw}
          />

          {/* v15: 分散購入プラン */}
          <DistributedPlanCard
            plan={data.budgetPlan?.distributed_plan}
            winning={winningRaw}
          />

          {/* v16: オールミニプラン */}
          <AllMiniPlanCard
            plan={data.budgetPlan?.all_mini_5}
            winning={winningRaw}
          />

          {/* v16: セット購入プラン */}
          <SetPlanCard
            title="セット · 800円枠 (2口)"
            plan={data.budgetPlan?.set_plan}
            winning={winningRaw}
          />
          <SetPlanCard
            title="セット · 2,000円枠 (5口)"
            plan={data.budgetPlan?.set_plan_5}
            winning={winningRaw}
          />

          {/* v16: 月間確率シミュレーション */}
          <MonthlySimulationCard
            simulation={data.budgetPlan?.monthly_simulation}
          />
        </div>

        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 border-b">
            <CardTitle className="text-lg">
              次回（第 {data.targetDrawNumber} 回）予測 · モデル別
            </CardTitle>
            <CardDescription className="space-y-1">
              <span className="block">
                <code className="font-mono text-xs">doc_kind: method</code>
                {" · "}
                各予測モデルごとに、直近実行ランの上位候補を順位・スコアつきで表示します（JSON
                から最大 96 件まで読み込み、カード内では最大 {METHOD_MODEL_TABLE_MAX_ROWS}{" "}
                件まで表示）。当選番号が分かっている回では照合バッジも付きます。
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent className="px-4 pb-6 pt-4 sm:px-6">
            {data.methodRows.length === 0 ? (
              <p className="text-muted-foreground py-8 text-center text-sm">
                method ドキュメントがありません（未生成か、別回のみ）
              </p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {data.methodRows.map((m) => (
                  <MethodModelDetailCard
                    key={m.slug}
                    row={m}
                    winningRaw={winningRaw}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

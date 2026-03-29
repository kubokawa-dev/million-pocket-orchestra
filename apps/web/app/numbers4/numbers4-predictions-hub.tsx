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
import {
  contributorsForEnsembleNumber,
  formatContributorSlugLine,
} from "@/lib/numbers4-predictions/ensemble-contributors";
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
  MethodPredictionRow,
  Numbers4PredictionBundle,
} from "@/lib/numbers4-predictions/types";
import { cn } from "@/lib/utils";

import { Numbers4OfficialDrawDetail } from "./numbers4-official-draw-detail";

const ENSEMBLE_SCORE_HEAD_TITLE =
  "各モデルの予測リストの順位を重み付けして合算し、その後に多様性調整・4桁の合計値ボーナス・ボックスタイプの分布調整などを適用した値です。当選確率や期待値ではありません。";

const ENSEMBLE_NEARBY_HEAD_TITLE =
  "メイン候補に近い別4桁の提案です。統計・LightGBMの桁確率などに基づき生成されます。アンサンブル本体のスコアとは別指標です。";

const ENSEMBLE_CONTRIBUTOR_HEAD_TITLE =
  "下の「モデル別」で読み込んだ各モデル直近ランの候補（最大96件）に、この4桁が含まれるかを表示します。完全一致と、桁の並びだけ異なるボックス同一を分けます。リストの下位のみに載っている場合は「—」になります。";

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

function EnsembleNearbyDetails({
  patterns,
}: {
  patterns: NonNullable<EnsembleTopPrediction["similar_patterns"]>;
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
            <span className="font-mono text-foreground">{sp.number ?? "—"}</span>
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

function EnsembleContributorCell({
  exactSlugs,
  boxOnlySlugs,
}: {
  exactSlugs: string[];
  boxOnlySlugs: string[];
}) {
  const nExact = exactSlugs.length;
  const nBox = boxOnlySlugs.length;
  if (nExact === 0 && nBox === 0) {
    return (
      <span
        className="text-muted-foreground text-xs tabular-nums"
        title="各モデル直近ラン上位96件に一致する候補がありません（より下位のみの可能性あり）"
      >
        —
      </span>
    );
  }

  const summaryParts: string[] = [];
  if (nExact > 0) summaryParts.push(`一致 ${nExact}`);
  if (nBox > 0) summaryParts.push(`ボックス ${nBox}`);

  return (
    <details className="max-w-[11rem] text-xs">
      <summary className="text-muted-foreground cursor-pointer list-none py-0.5 marker:content-none [&::-webkit-details-marker]:hidden">
        <span className="text-foreground font-medium tabular-nums">
          {summaryParts.join(" · ")}
        </span>
      </summary>
      <div className="border-border/60 mt-1 max-h-36 space-y-2 overflow-y-auto border-t pt-1">
        {nExact > 0 ? (
          <ul className="space-y-1">
            {exactSlugs.map((slug) => (
              <li
                key={slug}
                className="text-muted-foreground leading-snug break-words"
              >
                {formatContributorSlugLine(slug)}
              </li>
            ))}
          </ul>
        ) : null}
        {nBox > 0 ? (
          <div>
            <p className="text-muted-foreground mb-1 text-[0.65rem] leading-snug">
              桁の並びは異なるが、ボックス（数字の組み合わせ）は同一の候補:
            </p>
            <ul className="space-y-1">
              {boxOnlySlugs.map((slug) => (
                <li
                  key={slug}
                  className="text-muted-foreground leading-snug break-words"
                >
                  {formatContributorSlugLine(slug)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </details>
  );
}

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
                  は、このページで読み込んだ「モデル別」各モデルの直近ラン候補（最大96件）との照合です。集計パイプライン内部の票とは完全一致しない場合があります。
                </p>
              </div>
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

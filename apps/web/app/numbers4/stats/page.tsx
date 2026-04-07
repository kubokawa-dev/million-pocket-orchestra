import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeftIcon, LineChartIcon } from "lucide-react";

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
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { computeBoxRankStats } from "@/lib/numbers4-predictions/box-rank-stats";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ボックス順位の統計 | ナンバーズ4",
  description:
    "直近の開催回について、アンサンブル・手法別の予測リスト内で当選番号（ボックス一致）が何位以内に入ったかを集計します。",
  alternates: { canonical: "/numbers4/stats" },
  openGraph: {
    title: "ボックス順位の統計 | ナンバーズ4",
    description:
      "予測リスト内での当選番号の順位を、モデル別に集計して比較できます。",
    url: "/numbers4/stats",
  },
};

type PageProps = {
  searchParams: Promise<{ last?: string; topK?: string }>;
};

function parsePositiveInt(v: string | undefined, fallback: number): number {
  if (v == null || v === "") return fallback;
  const n = parseInt(v, 10);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

export default async function Numbers4StatsPage({ searchParams }: PageProps) {
  const sp = await searchParams;
  const last = parsePositiveInt(sp.last, 20);
  const topK = parsePositiveInt(sp.topK, 100);

  const stats = await computeBoxRankStats({ lastN: last, topK });

  const lastOptions = [10, 20, 30, 50] as const;
  const topKOptions = [50, 100, 200] as const;

  const mkHref = (l: number, k: number) =>
    `/numbers4/stats?last=${l}&topK=${k}`;

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ナンバーズ4", path: "/numbers4" },
    { name: "ボックス順位の統計", path: "/numbers4/stats" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-6xl flex-1 space-y-8 px-4 py-10 sm:px-6 sm:py-14">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-2">
            <Link
              href="/numbers4"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "text-muted-foreground -ml-2 w-fit gap-1",
              )}
            >
              <ArrowLeftIcon className="size-4" />
              ナンバーズ4 トップへ
            </Link>
            <div className="flex items-center gap-2">
              <LineChartIcon className="text-muted-foreground size-7" />
              <h1 className="text-foreground font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
                ボックス順位の統計
              </h1>
            </div>
            <p className="text-muted-foreground max-w-2xl text-sm leading-relaxed">
              Supabase の{" "}
              <code className="bg-muted rounded px-1 font-mono text-xs">
                numbers4_draws
              </code>{" "}
              に当選番号がある直近{" "}
              <strong className="text-foreground">{stats.draws.length}</strong>{" "}
              回を対象に、各回の予測バンドル（DB 優先・無ければリポジトリ
              JSON）から<strong className="text-foreground">
                ボックス一致
              </strong>
              が<strong className="text-foreground">
                リスト先頭から何番目か
              </strong>
              を数え、しきい値ごとの割合を出しています。JSON
              に保存されている件数（例: アンサンブル上位
              20）より下は「圏外」になります。
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">条件</CardTitle>
            <CardDescription>
              対象回数・評価するリスト長を切り替えます（いずれも URL
              クエリに反映）。
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
            <div className="space-y-1">
              <p className="text-muted-foreground text-xs font-medium">
                直近の開催回（当選データあり）
              </p>
              <div className="flex flex-wrap gap-2">
                {lastOptions.map((l) => (
                  <Link
                    key={l}
                    href={mkHref(l, topK)}
                    className={cn(
                      buttonVariants({
                        variant: l === last ? "default" : "outline",
                        size: "sm",
                      }),
                    )}
                  >
                    {l} 回
                  </Link>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-muted-foreground text-xs font-medium">
                リスト先頭から探索する最大件数（top K）
              </p>
              <div className="flex flex-wrap gap-2">
                {topKOptions.map((k) => (
                  <Link
                    key={k}
                    href={mkHref(last, k)}
                    className={cn(
                      buttonVariants({
                        variant: k === topK ? "default" : "outline",
                        size: "sm",
                      }),
                    )}
                  >
                    {k} 件まで
                  </Link>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {!stats.hadSupabaseDraws ? (
          <Card className="border-destructive/40 bg-destructive/5">
            <CardHeader>
              <CardTitle className="text-base text-destructive">
                データを取得できませんでした
              </CardTitle>
              <CardDescription>
                Supabase の{" "}
                <code className="font-mono">numbers4_draws</code>{" "}
                から当選番号付きの行が読めません。環境変数・RLS・データ投入を確認してください。
              </CardDescription>
            </CardHeader>
          </Card>
        ) : (
          <>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">集計サマリー</CardTitle>
                <CardDescription>
                  n = 対象回数。圏外 = その回の保存リスト内にボックス一致が無い（または当選不明）。
                  列「≤5」は 5 位以内にボックス一致があった回の割合。
                </CardDescription>
              </CardHeader>
              <CardContent className="px-0 sm:px-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="min-w-[200px]">ソース</TableHead>
                      <TableHead className="text-right">n</TableHead>
                      <TableHead className="text-right">圏外</TableHead>
                      {stats.thresholds.map((t) => (
                        <TableHead key={t} className="text-right">
                          ≤{t}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {stats.aggregates.map((row) => (
                      <TableRow key={row.key}>
                        <TableCell className="font-medium whitespace-normal">
                          {row.label}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.n}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.outOfRange}
                        </TableCell>
                        {stats.thresholds.map((t) => {
                          const cell = row.atOrBelow[t];
                          return (
                            <TableCell
                              key={t}
                              className="text-right tabular-nums text-xs sm:text-sm"
                            >
                              {cell
                                ? `${cell.count} (${cell.pct.toFixed(1)}%)`
                                : "—"}
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">回別の順位（詳細）</CardTitle>
                <CardDescription>
                  数字はボックス一致の順位（1
                  始まり）。空欄は圏外。アンサンブル列は ensemble JSON
                  の最新スナップショットです。
                </CardDescription>
              </CardHeader>
              <CardContent className="px-0 sm:px-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="sticky left-0 z-10 bg-card min-w-[72px]">
                        回
                      </TableHead>
                      <TableHead className="min-w-[56px]">当選</TableHead>
                      <TableHead className="text-center min-w-[64px]">
                        Ens.
                      </TableHead>
                      {stats.aggregates
                        .filter((r) => r.key !== "ensemble")
                        .map((r) => (
                          <TableHead
                            key={r.key}
                            className="text-center min-w-[52px] max-w-[72px] truncate text-xs"
                            title={r.label}
                          >
                            {r.key}
                          </TableHead>
                        ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {stats.perDraw.map((d) => (
                      <TableRow key={d.drawNumber}>
                        <TableCell className="bg-card sticky left-0 z-10 font-medium tabular-nums">
                          {d.drawNumber}
                        </TableCell>
                        <TableCell className="font-mono text-xs sm:text-sm">
                          {d.winning ?? "—"}
                        </TableCell>
                        <TableCell className="text-center tabular-nums text-xs sm:text-sm">
                          {d.ranks.ensemble ?? "—"}
                        </TableCell>
                        {stats.aggregates
                          .filter((x) => x.key !== "ensemble")
                          .map((x) => {
                            const slug = x.key;
                            const v = d.ranks[slug];
                            return (
                              <TableCell
                                key={slug}
                                className="text-center tabular-nums text-xs"
                              >
                                {v ?? "—"}
                              </TableCell>
                            );
                          })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}

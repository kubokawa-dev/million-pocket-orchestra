import type { Metadata } from "next";
import Link from "next/link";
import { BarChart3Icon } from "lucide-react";

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
import {
  computeLoto6BallStats,
  maxMainCount,
  type Loto6DrawRowLite,
} from "@/lib/loto6-stats";
import { createClient } from "@/lib/supabase/server";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "出現回数の統計 | ロト6",
  description:
    "ロト6の本数字・ボーナス数字の出現回数を、直近の開催回から集計します（非公式・閲覧用）。",
  alternates: { canonical: "/loto6/stats" },
  openGraph: {
    title: "出現回数の統計 | ロト6",
    description: "1〜43の各球が、直近何回の本数字／ボーナスに出たかを一覧します。",
    url: "/loto6/stats",
  },
};

type PageProps = {
  searchParams: Promise<{ window?: string }>;
};

function parseWindow(v: string | undefined): number | null {
  if (v == null || v === "" || v === "all") return null;
  const n = parseInt(v, 10);
  if (!Number.isFinite(n) || n < 10) return 96;
  return Math.min(n, 2000);
}

export default async function Loto6StatsPage({ searchParams }: PageProps) {
  const sp = await searchParams;
  const window = parseWindow(sp.window);

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("loto6_draws")
    .select("draw_number, draw_date, numbers, bonus_number")
    .order("draw_number", { ascending: true });

  if (error) throw new Error(error.message);

  const rows = (data ?? []) as Loto6DrawRowLite[];
  const stats = computeLoto6BallStats(rows, window);
  const maxMain = maxMainCount(stats) || 1;
  const drawsUsed =
    window != null && window > 0 ? Math.min(window, rows.length) : rows.length;

  const windowOptions = [48, 96, 192, "all"] as const;
  const hrefWindow = (w: number | "all") =>
    w === "all" ? "/loto6/stats?window=all" : `/loto6/stats?window=${w}`;

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ロト6", path: "/loto6" },
    { name: "出現回数の統計", path: "/loto6/stats" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-4xl flex-1 space-y-8 px-4 py-10 sm:px-6 sm:py-14">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-2">
            <Link
              href="/loto6"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "text-muted-foreground -ml-2 w-fit hover:text-foreground",
              )}
            >
              ← ロト6 ハブへ
            </Link>
            <div className="flex items-center gap-2">
              <BarChart3Icon className="text-amber-600 dark:text-amber-400 size-7" />
              <h1 className="text-foreground font-heading text-2xl font-bold tracking-tight sm:text-3xl">
                ロト6 出現回数の統計
              </h1>
            </div>
            <p className="text-muted-foreground max-w-2xl text-sm leading-relaxed sm:text-base">
              取り込み済みの <strong className="text-foreground">{rows.length}</strong>{" "}
              回を元に、各球が本数字・ボーナスに何回出たかを数えています。窓を変えると「直近だけ見たい」検証にも使えます。
            </p>
          </div>
        </div>

        <Card className="border-border/70 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">集計窓</CardTitle>
            <CardDescription>
              現在:{" "}
              <strong className="text-foreground">
                {window == null ? `全 ${rows.length} 回` : `直近 ${drawsUsed} 回`}
              </strong>
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {windowOptions.map((w) => {
              const active =
                w === "all"
                  ? window == null
                  : window === w;
              return (
                <Link
                  key={String(w)}
                  href={hrefWindow(w)}
                  className={cn(
                    buttonVariants({ variant: active ? "default" : "outline", size: "sm" }),
                    active &&
                      "border-amber-600 bg-gradient-to-r from-amber-600 to-orange-600 text-white hover:from-amber-500 hover:to-orange-500",
                  )}
                >
                  {w === "all" ? "全期間" : `直近 ${w} 回`}
                </Link>
              );
            })}
          </CardContent>
        </Card>

        <Card className="border-border/70 overflow-hidden shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">1〜43 各球の出現</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              バーは本数字の出現回数（最大を 100% とした相対幅）です。
            </CardDescription>
          </CardHeader>
          <CardContent className="px-0 pb-4">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-14 pl-4">球</TableHead>
                    <TableHead className="min-w-[140px]">本数字（回数）</TableHead>
                    <TableHead className="w-28 text-right">本数字</TableHead>
                    <TableHead className="w-28 text-right">ボーナス</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats.map((s) => (
                    <TableRow key={s.ball}>
                      <TableCell className="pl-4 font-mono font-medium tabular-nums">
                        {s.ball}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="bg-muted h-2 min-w-[4rem] flex-1 overflow-hidden rounded-full">
                            <div
                              className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500"
                              style={{
                                width: `${Math.max(4, (s.mainCount / maxMain) * 100)}%`,
                              }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm tabular-nums">
                        {s.mainCount}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm tabular-nums">
                        {s.bonusCount}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <p className="text-muted-foreground text-center text-xs sm:text-sm">
          非公式の閲覧用です。当せん確認は必ず公式情報で行ってください。
        </p>
      </div>
    </div>
  );
}

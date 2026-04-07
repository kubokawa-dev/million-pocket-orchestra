import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRightIcon,
  BarChart3Icon,
  CoinsIcon,
  DatabaseIcon,
  LayersIcon,
  ListIcon,
  SparklesIcon,
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
import { resolveTargetDrawNumber } from "@/lib/numbers4-predictions/load-6949";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ナンバーズ4",
  description:
    "日次予測（アンサンブル・モデル別・予算プラン）と当選番号一覧への入口です。",
  alternates: { canonical: "/numbers4" },
  openGraph: {
    title: "ナンバーズ4 | Million Pocket（たからくじAI）",
    description:
      "複数のAI・統計モデルによるナンバーズ4の日次予測と、当選番号・統計ページへのハブ。",
    url: "/numbers4",
  },
};

export default async function Numbers4Page() {
  const latestDraw = await resolveTargetDrawNumber();
  const latestHref = `/numbers4/result/${latestDraw}`;

  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-3xl flex-1 space-y-10 px-4 py-10 sm:space-y-12 sm:px-6 sm:py-14">
        <header className="space-y-4 text-center sm:text-left">
          <Badge variant="secondary" className="mb-1">
            <SparklesIcon data-icon="inline-start" className="size-3.5" />
            Numbers4
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            ナンバーズ4
          </h1>
          <p className="text-muted-foreground mx-auto max-w-xl text-sm leading-relaxed sm:mx-0 sm:text-base">
            このサイトの「ナンバーズ4ゾーン」の入口です。いま取り込まれている予測データの最新回は{" "}
            <strong className="text-foreground">第 {latestDraw} 回</strong>
            向けです。当選番号は開催後に DB に入ると、予測との照合も自動で付きます。
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 sm:col-span-2">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <BarChart3Icon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">
                  ボックス順位の統計（直近の回を集計）
                </CardTitle>
              </div>
              <CardDescription>
                アンサンブル・手法別に、当選番号が予測リストの何位以内にボックス一致したかを表で確認できます。
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3 sm:flex-row">
              <Link
                href="/numbers4/stats"
                className={cn(
                  buttonVariants({ variant: "secondary", size: "lg" }),
                  "w-full justify-center gap-2 sm:w-auto",
                )}
              >
                統計ページを開く
                <ArrowRightIcon className="size-4" />
              </Link>
              <Link
                href="/numbers4/trend"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full justify-center gap-2 sm:w-auto border-orange-500/30 text-orange-600 hover:bg-orange-500/10 dark:text-orange-400",
                )}
              >
                🔥 Hot Model トレンド分析
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <LayersIcon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">最新回の予測を見る</CardTitle>
              </div>
              <CardDescription>
                第 {latestDraw} 回のアンサンブル・モデル別・予算プランをまとめて表示します。
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <ul className="text-muted-foreground space-y-2 text-sm leading-relaxed">
                <li className="flex gap-2">
                  <BarChart3Icon className="text-muted-foreground mt-0.5 size-4 shrink-0" />
                  <span>ランキングと重み（ensemble）</span>
                </li>
                <li className="flex gap-2">
                  <LayersIcon className="text-muted-foreground mt-0.5 size-4 shrink-0" />
                  <span>手法ごとの上位候補（method）</span>
                </li>
                <li className="flex gap-2">
                  <CoinsIcon className="text-muted-foreground mt-0.5 size-4 shrink-0" />
                  <span>予算プラン（1,000円 / 2,000円枠）</span>
                </li>
              </ul>
              <Link
                href={latestHref}
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "w-full justify-center gap-2 shadow-sm sm:w-auto",
                )}
              >
                第 {latestDraw} 回へ進む
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <ListIcon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">当選番号をさがす</CardTitle>
              </div>
              <CardDescription>
                回号ごとの公式当選と、予測ページへのリンクが並ぶ一覧です（ページ分割あり）。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href="/numbers4/result"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full justify-center gap-2 sm:w-auto",
                )}
              >
                当選番号一覧へ
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>
        </div>

        <Card className="border-border/60 bg-muted/30 shadow-none">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <DatabaseIcon className="text-muted-foreground size-4" />
              <CardTitle className="text-base">データについて</CardTitle>
            </div>
            <CardDescription className="text-xs sm:text-sm">
              表示は{" "}
              <code className="bg-background rounded px-1 font-mono text-[0.7rem]">
                numbers4_daily_prediction_documents
              </code>{" "}
              （Supabase）を優先し、無い場合はリポジトリ内の日次 JSON にフォールバックします。予測は参考情報であり、当選を保証するものではありません。
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}

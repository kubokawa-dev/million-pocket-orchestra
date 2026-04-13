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
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { resolveNumbers3TargetDrawNumber } from "@/lib/numbers3-predictions/load-numbers3";
import { createClient } from "@/lib/supabase/server";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ナンバーズ3",
  description:
    "日次モデル試算（アンサンブル・モデル別・予算プラン）と当選番号一覧への入口です。 EN: Unofficial Numbers3 hub — reference model outputs and results (verify officially).",
  alternates: { canonical: "/numbers3" },
  openGraph: {
    title: "ナンバーズ3 | 宝くじAI",
    description:
      "複数のAI・統計モデルによるナンバーズ3の日次試算と、当選番号一覧へのハブ。当せんの保証はありません。",
    url: "/numbers3",
  },
};

export default async function Numbers3Page() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("numbers3_draws")
    .select("draw_number")
    .order("draw_number", { ascending: false })
    .limit(1)
    .maybeSingle();
  const latestImportedDraw = data?.draw_number ?? null;

  const latestPredictTarget = await resolveNumbers3TargetDrawNumber();
  const latestPredictHref = `/numbers3/result/${latestPredictTarget}`;

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ナンバーズ3", path: "/numbers3" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-3xl flex-1 space-y-10 px-4 py-10 sm:space-y-12 sm:px-6 sm:py-14">
        <header className="space-y-4 text-center sm:text-left">
          <Badge variant="secondary" className="mb-1">
            <SparklesIcon data-icon="inline-start" className="size-3.5" />
            Numbers3
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            ナンバーズ3
          </h1>
          <p className="text-muted-foreground mx-auto max-w-xl text-sm leading-relaxed sm:mx-0 sm:text-base">
            このサイトの「ナンバーズ3ゾーン」の入口です。当せんデータの最新取り込み回は{" "}
            <strong className="text-foreground">
              {latestImportedDraw ? `第 ${latestImportedDraw} 回` : "未取得"}
            </strong>
            、モデル試算データの最新対象回は{" "}
            <strong className="text-foreground">第 {latestPredictTarget} 回</strong>
            向けです。
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 sm:col-span-2">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <LayersIcon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">最新回のモデル試算を見る</CardTitle>
              </div>
              <CardDescription>
                第 {latestPredictTarget} 回のアンサンブル・モデル別・予算プラン（あれば）をまとめて表示します。
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
                  <span>予算プラン（1,000円 / 2,000円枠・あれば）</span>
                </li>
              </ul>
              <Link
                href={latestPredictHref}
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "inline-flex w-full justify-center gap-2 shadow-sm sm:w-auto",
                )}
              >
                第 {latestPredictTarget} 回へ進む
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">最新の当せん取り込み回を見る</CardTitle>
              <CardDescription>
                当せんデータが取り込まれている最新回のページへ移動します（試算と同じ URL で照合も表示）。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href={
                  latestImportedDraw
                    ? `/numbers3/result/${latestImportedDraw}`
                    : "/numbers3/result"
                }
                className={cn(
                  buttonVariants({ variant: "secondary", size: "lg" }),
                  "w-full justify-center gap-2 shadow-sm sm:w-auto",
                )}
              >
                {latestImportedDraw ? `第 ${latestImportedDraw} 回へ` : "一覧へ"}
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
                回号ごとの公式当選と、試算・照合ページへのリンクが並ぶ一覧です。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href="/numbers3/result"
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
              表示はオンライン上の最新データを優先し、無い場合はサイトに同梱の日次 JSON
              から読み込みます。試算は参考情報であり、当せんを保証するものではありません。
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}

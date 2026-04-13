import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRightIcon,
  DatabaseIcon,
  ListIcon,
  SparklesIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { AnalysisTransparencyCallout } from "@/components/analysis-transparency-callout";
import { TodayReferencePanel } from "@/components/today-reference-panel";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loto6PredictionsPanel } from "@/components/loto6-predictions-panel";
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import {
  loadLoto6PredictionBundle,
  resolveNextLoto6TargetDrawNumber,
} from "@/lib/loto6-predictions/load-bundles";
import { createClient } from "@/lib/supabase/server";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ロト6",
  description:
    "ロト6の当選番号一覧への入口です。本数字・ボーナス・等級別払戻を Supabase 上のデータから表示します。",
  alternates: { canonical: "/loto6" },
  openGraph: {
    title: "ロト6 | 宝くじAI",
    description:
      "ロト6の抽選結果一覧・詳細、MVPモデル試算、出現回数統計へのハブ。当せんの保証はありません。",
    url: "/loto6",
  },
};

export default async function Loto6Page() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("loto6_draws")
    .select("draw_number")
    .order("draw_number", { ascending: false })
    .limit(1)
    .maybeSingle();

  const latestDraw = data?.draw_number ?? null;
  const latestHref = latestDraw ? `/loto6/result/${latestDraw}` : "/loto6/result";

  const nextTarget = await resolveNextLoto6TargetDrawNumber();
  const predictionBundle =
    nextTarget != null ? await loadLoto6PredictionBundle(nextTarget) : null;

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ロト6", path: "/loto6" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-4xl flex-1 space-y-10 px-4 py-10 sm:space-y-12 sm:px-6 sm:py-14">
        <header className="space-y-4 text-center sm:text-left">
          <Badge
            variant="secondary"
            className="mb-1 border-amber-500/30 bg-amber-500/10 text-amber-900 dark:border-amber-400/30 dark:bg-amber-400/10 dark:text-amber-100"
          >
            <SparklesIcon data-icon="inline-start" className="size-3.5" />
            Loto6
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            ロト6
          </h1>
          <p className="text-muted-foreground mx-auto max-w-xl text-sm leading-relaxed sm:mx-0 sm:text-base">
            本サイトのロト6ゾーンです。最新取り込み回は{" "}
            <strong className="text-foreground">
              {latestDraw ? `第 ${latestDraw} 回` : "未取得"}
            </strong>
            です。当選番号・ボーナス・等級別口数・払戻金・キャリーオーバーを一覧・詳細で確認できます。
            {nextTarget != null ? (
              <>
                {" "}
                次回予定の{" "}
                <strong className="text-foreground">第 {nextTarget} 回</strong>
                向けの MVP モデル試算は、下のパネルで確認できます（データがある場合。当せんの保証ではありません）。
              </>
            ) : null}
          </p>
        </header>

        {predictionBundle &&
        (predictionBundle.ensemble != null ||
          predictionBundle.methodRows.length > 0) ? (
          <section className="border-border/60 rounded-2xl border bg-card/40 p-5 shadow-sm ring-1 ring-black/5 sm:p-6 dark:ring-white/10">
            <Loto6PredictionsPanel bundle={predictionBundle} />
          </section>
        ) : nextTarget != null ? (
          <Card className="border-dashed border-amber-500/30 bg-muted/20 shadow-none">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">モデル試算（MVP）</CardTitle>
              <CardDescription>
                第 {nextTarget} 回向けの試算 JSON がまだ Supabase に入っていません。リポジトリで{" "}
                <code className="font-mono text-xs">
                  python tools/generate_loto6_predictions_mvp.py
                </code>{" "}
                →{" "}
                <code className="font-mono text-xs">
                  python tools/load_loto6_daily_json_to_postgres.py
                </code>{" "}
                を実行すると表示されます（8 手法 + アンサンブル JSON）。
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        <TodayReferencePanel
          title="Today view"
          latestLabel="最新取り込み / 次回参考対象"
          latestValue={`${latestDraw ? `取り込み: 第 ${latestDraw} 回` : "取り込み: 未取得"}${nextTarget != null ? ` / 次回: 第 ${nextTarget} 回` : ""}`}
          primaryHref={latestHref}
          primaryLabel={latestDraw ? `第 ${latestDraw} 回を見る` : "一覧を見る"}
          secondaryHref="/loto6/result"
          secondaryLabel="当選番号一覧"
          statsHref="/loto6/stats"
          statsLabel="出現回数の統計"
          apiHref="/api/loto6/latest"
          apiLabel="GET /api/loto6/latest"
          accentClassName="border-amber-500/20 bg-amber-500/5"
        />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">最新回を見る</CardTitle>
              <CardDescription>
                最新回の当選結果ページに移動します。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href={latestHref}
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "w-full justify-center gap-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-sm hover:from-amber-500 hover:to-orange-500 sm:w-auto",
                )}
              >
                {latestDraw ? `第 ${latestDraw} 回へ` : "一覧へ"}
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">出現回数の統計</CardTitle>
              <CardDescription>
                本数字・ボーナスの出現頻度を球ごとにチェック。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href="/loto6/stats"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full justify-center gap-2 border-amber-500/30 sm:w-auto",
                )}
              >
                統計ページへ
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <ListIcon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">当選番号一覧</CardTitle>
              </div>
              <CardDescription>回号ごとの結果を一覧表示します。</CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href="/loto6/result"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full justify-center gap-2 border-amber-500/30 sm:w-auto",
                )}
              >
                一覧を開く
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
              表示は Supabase の <code className="font-mono">loto6_draws</code>{" "}
              を参照します。非公式の二次情報です。購入判断は必ず公式発表で確認してください。
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <Link
              href="/data-sources"
              className={cn(
                buttonVariants({ variant: "link", size: "sm" }),
                "h-auto px-0 text-amber-700 dark:text-amber-400",
              )}
            >
              データの出所・API 一覧へ
            </Link>
          </CardContent>
        </Card>

        <AnalysisTransparencyCallout
          basis={[
            "公開された当選結果と、ある場合は日次の MVP モデル JSON を参照しています。",
            "一覧・統計・最新回ページをつないでいます。",
          ]}
          limitations={[
            "モデル表示は参考用で、当せん確率を保証しません。",
            "払戻やルールの最終確認は必ず公式情報で行ってください。",
          ]}
        />
      </div>
    </div>
  );
}

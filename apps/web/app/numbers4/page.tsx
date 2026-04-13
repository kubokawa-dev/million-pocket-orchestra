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
import { AnalysisTransparencyCallout } from "@/components/analysis-transparency-callout";
import { MissAnalysisCards } from "@/components/miss-analysis-cards";
import { ModelGovernancePanel } from "@/components/model-governance-panel";
import { ModelReportCards } from "@/components/model-report-cards";
import { TodayReferencePanel } from "@/components/today-reference-panel";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { buildNumbers4MissAnalysis } from "@/lib/miss-analysis";
import { buildNumbers4ModelGovernance } from "@/lib/model-governance";
import { buildNumbers4ModelReportCards } from "@/lib/model-report-cards";
import { resolveTargetDrawNumber } from "@/lib/numbers4-predictions/load-6949";
import { cn } from "@/lib/utils";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "ナンバーズ4",
  description:
    "日次モデル試算（アンサンブル・モデル別・予算プラン）と当選番号一覧への入口です。 EN: Unofficial Numbers4 hub — reference model outputs, stats, and results (verify officially).",
  alternates: { canonical: "/numbers4" },
  openGraph: {
    title: "ナンバーズ4 | 宝くじAI",
    description:
      "複数のAI・統計モデルによるナンバーズ4の日次試算と、当選番号・統計ページへのハブ。当せんの保証はありません。",
    url: "/numbers4",
  },
};

export default async function Numbers4Page() {
  const [latestDraw, reportCards, missAnalysis, governance] = await Promise.all([
    resolveTargetDrawNumber(),
    buildNumbers4ModelReportCards(30),
    buildNumbers4MissAnalysis(30),
    buildNumbers4ModelGovernance(30),
  ]);
  const latestHref = `/numbers4/result/${latestDraw}`;

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ナンバーズ4", path: "/numbers4" },
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
            Numbers4
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            ナンバーズ4
          </h1>
          <p className="text-muted-foreground mx-auto max-w-xl text-sm leading-relaxed sm:mx-0 sm:text-base">
            このサイトの「ナンバーズ4ゾーン」の入口です。いま取り込まれているモデル試算データの最新回は{" "}
            <strong className="text-foreground">第 {latestDraw} 回</strong>
            向けです。当選番号は開催後にサイトへ取り込まれると、試算リストとの照合も自動で付きます。
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <TodayReferencePanel
              title="Today view"
              latestLabel="いまの参考対象回"
              latestValue={`第 ${latestDraw} 回`}
              primaryHref={latestHref}
              primaryLabel={`第 ${latestDraw} 回を見る`}
              secondaryHref="/numbers4/result"
              secondaryLabel="当選番号一覧"
              statsHref="/numbers4/trend"
              statsLabel="Hot Model トレンド"
              apiHref="/api/numbers4/latest"
              apiLabel="GET /api/numbers4/latest"
              accentClassName="border-violet-500/20 bg-violet-500/5"
            />
          </div>

          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10 sm:col-span-2">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <BarChart3Icon className="text-muted-foreground size-5" />
                <CardTitle className="text-lg">
                  ボックス順位の統計（直近の回を集計）
                </CardTitle>
              </div>
              <CardDescription>
                アンサンブル・手法別に、当選番号が各モデルの候補リストの何位以内にボックス一致したかを表で確認できます。
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
                <CardTitle className="text-lg">最新回のモデル試算を見る</CardTitle>
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
                回号ごとの公式当選と、試算・照合ページへのリンクが並ぶ一覧です（ページ分割あり）。
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
              表示はオンライン上の最新データを優先し、無い場合はサイトに同梱の日次 JSON
              から読み込みます。試算は参考情報であり、当せんを保証するものではありません。
            </CardDescription>
          </CardHeader>
        </Card>

        <AnalysisTransparencyCallout
          basis={[
            "公開された抽選結果と日次モデル JSON を参照しています。",
            "最新回への導線と、統計・トレンドへの導線を同時に出しています。",
          ]}
          limitations={[
            "モデル表示は参考用で、当せん確率を保証しません。",
            "統計やトレンドは過去記述であり、将来の優位性を約束しません。",
          ]}
        />

        <ModelReportCards
          title="Model report cards"
          description="直近30回のボックス一致集計から、最近の見え方をカードで要約しています。過去成績の要約であり、将来の優位性を保証するものではありません。"
          cards={reportCards}
          primaryMetricLabel="box hit rate"
          sampleCaption="直近 {n} 回"
          secondaryMetricLabel="top 10"
          secondaryMetric={(card) =>
            card.top10Pct != null ? `${card.top10Pct}%` : null
          }
        />

        <MissAnalysisCards
          title="外れ方分析"
          description="完全一致だけでは見えない、ensemble の近さを要約しています。上位何位で近い候補が出ていたかを見ることで、候補の広げ方や重複の減らし方を判断しやすくします。"
          summary={missAnalysis}
          oneDigitOffLabel="top1 1桁違い圏"
        />

        <ModelGovernancePanel
          title="モデル淘汰ルール"
          description="直近成績の弱いモデルをそのまま横並びで見せ続けないために、扱いを分けています。ここで `控えめ` に入るモデルは、予測ページでも過信しない前提で読むべき対象です。"
          summary={governance}
        />
      </div>
    </div>
  );
}

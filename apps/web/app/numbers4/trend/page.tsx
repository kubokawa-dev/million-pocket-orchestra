import type { Metadata } from "next";
import { ArrowLeftIcon, FlameIcon, ArrowRightIcon, WavesIcon, LightbulbIcon } from "lucide-react";
import Link from "next/link";

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
import { loadNumbers4PredictionBundleForDraw, resolveTargetDrawNumber } from "@/lib/numbers4-predictions/load-6949";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Hot Model トレンド分析 | ナンバーズ4",
  description:
    "直近50回の成績から、いま一番「キテる」モデルを分析します。 EN: Hot model trend view for Numbers4 predictions (unofficial).",
  alternates: { canonical: "/numbers4/trend" },
  openGraph: {
    title: "Hot Model トレンド分析 | ナンバーズ4",
    description:
      "直近の予測成績から注目モデルを可視化。ナンバーズ4の予測トレンドをチェック。",
    url: "/numbers4/trend",
  },
};

async function fetchTrendData(targetDraw: number) {
  try {
    const bundle = await loadNumbers4PredictionBundleForDraw(targetDraw);
    if (!bundle || !bundle.ensemble || !bundle.ensemble.predictions) {
      return { hotModels: [], recentFlow: [], nextPredictions: [] };
    }
    const preds = bundle.ensemble.predictions;
    const lastRun = preds[preds.length - 1];
    return {
      hotModels: lastRun.hot_models || [],
      recentFlow: [...(lastRun.recent_flow || [])].sort(
        (a, b) => (a.draw ?? 0) - (b.draw ?? 0),
      ),
      nextPredictions: lastRun.next_model_predictions || [],
    };
  } catch (error) {
    console.error("Failed to fetch trend data:", error);
    return { hotModels: [], recentFlow: [], nextPredictions: [] };
  }
}

export default async function HotModelTrendPage() {
  const latestDraw = await resolveTargetDrawNumber();
  const { hotModels, recentFlow, nextPredictions } = await fetchTrendData(latestDraw);

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ナンバーズ4", path: "/numbers4" },
    { name: "Hot Model トレンド分析", path: "/numbers4/trend" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-3xl flex-1 space-y-8 px-4 py-10 sm:px-6 sm:py-14">
        <div className="flex items-start gap-4">
          <Link
            href="/numbers4"
            className={cn(
              buttonVariants({ variant: "ghost", size: "icon" }),
              "mt-1 shrink-0",
            )}
            aria-label="戻る"
          >
            <ArrowLeftIcon className="size-5" />
          </Link>
          <div>
            <Badge variant="secondary" className="mb-2">
              <FlameIcon data-icon="inline-start" className="size-3.5 text-orange-500" />
              Hot Model Trend
            </Badge>
            <h1 className="text-foreground font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
              直近50回のトレンド分析
            </h1>
          </div>
        </div>

        <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
          第 {latestDraw - 50} 回 〜 第 {latestDraw - 1} 回の成績を集計し、
          いま一番「キテる」モデルをランキング形式で表示します。
          （※ このスコアは毎日のアンサンブル予測の重み付けに自動で反映されます）
        </p>

        {hotModels.length > 0 ? (
          <div className="space-y-6">
            <Card className="border-orange-500/20 bg-orange-500/5 shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg text-orange-600 dark:text-orange-400">
                  <FlameIcon className="size-5" />
                  今一番キテるのは【{hotModels[0].model}】！
                </CardTitle>
                <CardDescription className="text-orange-700/80 dark:text-orange-300/80">
                  直近50回で最も高いスコア（{hotModels[0].score.toFixed(1)}）を獲得しています。
                  次の予測はこのモデルの候補に注目してみてください！
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/80 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">🏆 Hot Model ランキング</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {hotModels.map((item, index) => {
                    const maxScore = hotModels[0].score || 1;
                    const percentage = Math.max(2, (item.score / maxScore) * 100);
                    
                    let medal = "✨";
                    if (index === 0) medal = "🥇";
                    else if (index === 1) medal = "🥈";
                    else if (index === 2) medal = "🥉";

                    return (
                      <div key={item.model} className="space-y-1.5">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium flex items-center gap-2">
                            <span className="w-6 text-center">{medal}</span>
                            {item.model}
                          </span>
                          <span className="text-muted-foreground font-mono">
                            {item.score.toFixed(1)}
                          </span>
                        </div>
                        <div className="bg-muted h-2 w-full overflow-hidden rounded-full">
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
              </CardContent>
            </Card>

            {recentFlow.length > 0 && (
              <Card className="border-border/80 shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <WavesIcon className="size-5 text-blue-500" />
                    直近の最強モデルのながれ
                  </CardTitle>
                  <CardDescription>
                    各回で最も成績が良かったモデルの履歴です（JSON では直近11回分を保存）。
                    モデルの「連チャン」や「遷移パターン」を読むヒントになります。
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 font-mono text-sm">
                    {recentFlow.map((flow) => (
                      <li
                        key={flow.draw}
                        className="text-foreground flex flex-wrap items-baseline gap-x-2"
                      >
                        <span className="text-muted-foreground">• 第{flow.draw}回:</span>
                        <span>{flow.model}</span>
                        <span className="text-muted-foreground font-sans text-xs tabular-nums">
                          (スコア: {flow.score.toFixed(1)})
                        </span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {nextPredictions.length > 0 && (
              <Card className="border-border/80 shadow-sm border-blue-500/20 bg-blue-500/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg text-blue-600 dark:text-blue-400">
                    <LightbulbIcon className="size-5" />
                    次回（第 {latestDraw} 回）の最強モデル予測
                  </CardTitle>
                  <CardDescription className="text-blue-700/80 dark:text-blue-300/80">
                    過去50回の遷移パターンから、前回（第 {latestDraw - 1} 回）の最強モデル「{recentFlow[recentFlow.length - 1]?.model}」の次に当たりやすいモデルを予測しています。
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {nextPredictions.map((pred, i) => (
                      <div key={pred.model} className="space-y-1.5">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium flex items-center gap-2">
                            <span className="w-6 text-center">{i === 0 ? "🎯" : "✨"}</span>
                            {pred.model}
                          </span>
                          <span className="text-muted-foreground text-xs">
                            確率: {(pred.probability * 100).toFixed(1)}% ({pred.count}/{pred.total}回)
                          </span>
                        </div>
                        <div className="bg-muted h-2 w-full overflow-hidden rounded-full">
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
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <Card className="border-border/80 shadow-sm">
            <CardContent className="py-10 text-center">
              <p className="text-muted-foreground">
                トレンドデータを取得できませんでした。
                Pythonスクリプトの実行環境を確認してください。
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

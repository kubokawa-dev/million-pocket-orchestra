import type { Metadata } from "next";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import { ArrowLeftIcon, FlameIcon } from "lucide-react";
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
import { resolveTargetDrawNumber } from "@/lib/numbers4-predictions/load-6949";
import { cn } from "@/lib/utils";

const execAsync = promisify(exec);

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Hot Model トレンド分析 | ナンバーズ4",
  description: "直近50回の成績から、いま一番「キテる」モデルを分析します。",
};

async function fetchHotModels(targetDraw: number) {
  try {
    const repoRoot = path.join(process.cwd(), "..", "..");
    const scriptPath = path.join(repoRoot, "numbers4", "predict_hot_models.py");
    
    // Pythonスクリプトを--jsonフラグ付きで実行して結果を取得
    const { stdout } = await execAsync(
      `python ${scriptPath} --target ${targetDraw} --lookback 50 --json`,
      { cwd: repoRoot }
    );
    
    const data = JSON.parse(stdout);
    return data as { model: string; score: number }[];
  } catch (error) {
    console.error("Failed to fetch hot models:", error);
    return [];
  }
}

export default async function HotModelTrendPage() {
  const latestDraw = await resolveTargetDrawNumber();
  const hotModels = await fetchHotModels(latestDraw);

  return (
    <div className="flex flex-1 flex-col">
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

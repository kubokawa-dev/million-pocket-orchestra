import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRightIcon,
  DatabaseIcon,
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
    description: "ロト6の抽選結果一覧と詳細ページへのハブ。",
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

  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ロト6", path: "/loto6" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-3xl flex-1 space-y-10 px-4 py-10 sm:space-y-12 sm:px-6 sm:py-14">
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
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
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
      </div>
    </div>
  );
}

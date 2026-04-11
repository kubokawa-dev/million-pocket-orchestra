import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRightIcon, ListIcon, SparklesIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createClient } from "@/lib/supabase/server";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ナンバーズ3",
  description:
    "ナンバーズ3の当選番号一覧と結果閲覧のハブページです（非公式・公式で必ず照合してください）。",
  alternates: { canonical: "/numbers3" },
  openGraph: {
    title: "ナンバーズ3 | 宝くじAI",
    description: "ナンバーズ3の結果ページへの入口です。",
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
  const latestDraw = data?.draw_number ?? null;

  return (
    <div className="flex flex-1 flex-col">
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
            ナンバーズ3の入口ページです。最新取り込み回は{" "}
            <strong className="text-foreground">
              {latestDraw ? `第 ${latestDraw} 回` : "未取得"}
            </strong>
            です。
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">最新回を見る</CardTitle>
              <CardDescription>
                最新回の結果ページに移動します。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href={latestDraw ? `/numbers3/result/${latestDraw}` : "/numbers3/result"}
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "w-full justify-center gap-2 shadow-sm sm:w-auto",
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
                href="/numbers3/result"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full justify-center gap-2 sm:w-auto",
                )}
              >
                一覧を開く
                <ArrowRightIcon className="size-4" />
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

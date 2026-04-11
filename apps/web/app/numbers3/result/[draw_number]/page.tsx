import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button-variants";
import { createClient } from "@/lib/supabase/server";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { draw_number } = await params;
  const n = parseInt(draw_number, 10);
  if (!Number.isFinite(n)) return { title: "ナンバーズ3" };
  return {
    title: `第${n}回 ナンバーズ3 当選結果`,
    alternates: { canonical: `/numbers3/result/${n}` },
  };
}

export default async function Numbers3ResultDetailPage({ params }: PageProps) {
  const { draw_number } = await params;
  const n = parseInt(draw_number, 10);
  if (!Number.isFinite(n)) notFound();

  const supabase = await createClient();
  const { data: row, error } = await supabase
    .from("numbers3_draws")
    .select("draw_number, draw_date, numbers")
    .eq("draw_number", n)
    .maybeSingle();
  if (error) throw new Error(error.message);
  if (!row) notFound();

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8 sm:px-6 sm:py-10">
      <Link
        href="/numbers3/result"
        className={cn(
          buttonVariants({ variant: "ghost", size: "sm" }),
          "text-muted-foreground -ml-2 hover:text-foreground",
        )}
      >
        ← 一覧へ
      </Link>

      <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
        <CardHeader>
          <CardTitle className="text-xl">第 {row.draw_number} 回 ナンバーズ3</CardTitle>
          <CardDescription>抽選日: {row.draw_date}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">当選番号</p>
          <p className="font-mono text-5xl font-bold tracking-[0.2em]">
            {String(row.numbers)}
          </p>
          <p className="text-muted-foreground mt-4 text-xs">
            予測ページは numbers3 の予測パイプライン連携後にこのURLへ統合表示されます。
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

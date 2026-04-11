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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { buttonVariants } from "@/components/ui/button-variants";
import { createClient } from "@/lib/supabase/server";
import {
  NUMBERS3_TIER_DETAIL_LABELS,
  type Numbers3DrawRow,
  formatNumbers3Cell,
} from "@/lib/numbers3";
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

function tierKeys(tier: 1 | 2 | 3 | 4) {
  const w = `tier${tier}_winners` as const;
  const y = `tier${tier}_payout_yen` as const;
  return { w, y };
}

export default async function Numbers3ResultDetailPage({ params }: PageProps) {
  const { draw_number } = await params;
  const n = parseInt(draw_number, 10);
  if (!Number.isFinite(n)) notFound();

  const supabase = await createClient();
  const { data: row, error } = await supabase
    .from("numbers3_draws")
    .select("*")
    .eq("draw_number", n)
    .maybeSingle();
  if (error) throw new Error(error.message);
  if (!row) notFound();

  const r = row as Numbers3DrawRow;

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
          <CardTitle className="text-xl">第 {r.draw_number} 回 ナンバーズ3</CardTitle>
          <CardDescription>抽選日: {r.draw_date}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          <div>
            <p className="text-muted-foreground text-sm">当選番号</p>
            <p className="font-mono text-5xl font-bold tracking-[0.2em]">
              {String(r.numbers)}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-foreground text-sm font-medium">当せん口数・払戻金</p>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[40%]">区分</TableHead>
                  <TableHead className="text-right">当選口数</TableHead>
                  <TableHead className="text-right">払戻金（円）</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {NUMBERS3_TIER_DETAIL_LABELS.map(({ tier, label }) => {
                  const { w, y } = tierKeys(tier);
                  return (
                    <TableRow key={tier}>
                      <TableCell className="text-muted-foreground text-sm">
                        {label}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm tabular-nums">
                        {formatNumbers3Cell(w, r)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm tabular-nums">
                        {formatNumbers3Cell(y, r)}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          <p className="text-muted-foreground text-xs">
            1〜4等の列は、当せんデータのストレート・ボックス・セット（ストレート）・セット（ボックス）に対応しています。
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

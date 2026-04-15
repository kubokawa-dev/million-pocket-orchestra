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
import { Loto6PredictionsPanel } from "@/components/loto6-predictions-panel";
import { createStaticClient } from "@/lib/supabase/static";
import { formatYen } from "@/lib/numbers4";
import {
  type Loto6DrawRow,
  formatLoto6NumbersCell,
} from "@/lib/loto6";
import { parseLoto6MainNumbers } from "@/lib/loto6-predictions/hit-utils";
import { loadLoto6PredictionBundle } from "@/lib/loto6-predictions/load-bundles";
import { cn } from "@/lib/utils";

export const revalidate = 60;

const TIER_LABELS = [
  { tier: 1 as const, label: "1等" },
  { tier: 2 as const, label: "2等" },
  { tier: 3 as const, label: "3等" },
  { tier: 4 as const, label: "4等" },
  { tier: 5 as const, label: "5等" },
];

function tierKeys(tier: 1 | 2 | 3 | 4 | 5) {
  const w = `tier${tier}_winners` as const;
  const y = `tier${tier}_payout_yen` as const;
  return { w, y };
}

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { draw_number } = await params;
  const n = parseInt(draw_number, 10);
  if (!Number.isFinite(n)) return { title: "ロト6" };
  return {
    title: `第${n}回 ロト6 当選結果`,
    alternates: { canonical: `/loto6/result/${n}` },
  };
}

export default async function Loto6ResultDetailPage({ params }: PageProps) {
  const { draw_number } = await params;
  const n = parseInt(draw_number, 10);
  if (!Number.isFinite(n)) notFound();

  const supabase = createStaticClient();
  const [{ data: row, error }, predictionBundle] = await Promise.all([
    supabase
      .from("loto6_draws")
      .select("*")
      .eq("draw_number", n)
      .maybeSingle(),
    loadLoto6PredictionBundle(n),
  ]);

  if (error) throw new Error(error.message);
  const hasPredictionData =
    predictionBundle != null &&
    (predictionBundle.ensemble != null || predictionBundle.methodRows.length > 0);
  if (!row && !hasPredictionData) notFound();

  const r = (row as Loto6DrawRow | null) ?? null;
  const actualMain = r ? parseLoto6MainNumbers(r.numbers) : [];

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8 sm:px-6 sm:py-10">
      <Link
        href="/loto6/result"
        className={cn(
          buttonVariants({ variant: "ghost", size: "sm" }),
          "text-muted-foreground -ml-2 hover:text-foreground",
        )}
      >
        ← 一覧へ
      </Link>

      {r ? (
        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader>
            <CardTitle className="text-xl">第 {r.draw_number} 回 ロト6</CardTitle>
            <CardDescription>抽選日: {r.draw_date}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            <div>
              <p className="text-muted-foreground text-sm">本数字</p>
              <p className="font-mono text-2xl font-bold tracking-wide sm:text-3xl">
                {formatLoto6NumbersCell(r.numbers)}
              </p>
              <p className="text-muted-foreground mt-3 text-sm">ボーナス数字</p>
              <p className="text-foreground font-mono text-3xl font-bold sm:text-4xl">
                {r.bonus_number}
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-foreground text-sm font-medium">等級別 当せん口数・払戻金</p>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[30%]">等級</TableHead>
                    <TableHead className="text-right">当選口数</TableHead>
                    <TableHead className="text-right">払戻金（円）</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {TIER_LABELS.map(({ tier, label }) => {
                    const { w, y } = tierKeys(tier);
                    const wc = r[w];
                    const yc = r[y];
                    return (
                      <TableRow key={tier}>
                        <TableCell className="text-muted-foreground text-sm">
                          {label}
                        </TableCell>
                        <TableCell className="text-right font-mono text-sm tabular-nums">
                          {wc === null || wc === undefined ? "—" : String(wc)}
                        </TableCell>
                        <TableCell className="text-right font-mono text-sm tabular-nums">
                          {formatYen(yc as number | string | null)}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>

            <div>
              <p className="text-muted-foreground text-sm">キャリーオーバー</p>
              <p className="font-mono text-lg font-semibold tabular-nums">
                {formatYen(r.carryover_yen as number | string | null)}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-dashed border-amber-500/40 bg-amber-500/[0.04] shadow-none">
          <CardHeader>
            <CardTitle className="text-xl">第 {n} 回 ロト6（抽選前プレビュー）</CardTitle>
            <CardDescription>
              この回の当選番号はまだ取り込まれていないため、「あたり」表示はありません。開催後、公式結果が反映されると自動で照合されます。
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      {hasPredictionData && predictionBundle ? (
        <section className="border-border/60 rounded-2xl border bg-card/40 p-5 shadow-sm ring-1 ring-black/5 sm:p-6 dark:ring-white/10">
          <Loto6PredictionsPanel
            bundle={predictionBundle}
            actualMain={r && actualMain.length === 6 ? actualMain : undefined}
            actualBonus={r?.bonus_number}
          />
        </section>
      ) : null}
    </div>
  );
}

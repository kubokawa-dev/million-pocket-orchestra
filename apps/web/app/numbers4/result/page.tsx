import type { Metadata } from "next";
import { redirect } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createClient } from "@/lib/supabase/server";
import { NUMBERS4_PAGE_SIZE, type Numbers4DrawRow } from "@/lib/numbers4";

import { buildWinningModelHitsForDrawList } from "@/lib/numbers4-predictions/load-6949";

import { Numbers4DrawsTable } from "./numbers4-draws-table";
import { Numbers4Pagination } from "./numbers4-pagination";
import { Numbers4RecentModelHits } from "./numbers4-recent-model-hits";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ナンバーズ4 当選番号一覧",
  description:
    "ナンバーズ4の過去の抽選結果（当選番号・等級別口数・払戻金）を一覧表示します。",
};

type PageProps = {
  searchParams: Promise<{ page?: string }>;
};

function parsePage(raw: string | undefined): number {
  const n = parseInt(raw ?? "1", 10);
  if (!Number.isFinite(n) || n < 1) return 1;
  return n;
}

export default async function Numbers4ResultPage({ searchParams }: PageProps) {
  const { page: pageParam } = await searchParams;
  const requestedPage = parsePage(pageParam);

  const supabase = await createClient();

  const { count, error: countError } = await supabase
    .from("numbers4_draws")
    .select("*", { count: "exact", head: true });

  if (countError) {
    throw new Error(countError.message);
  }

  const totalCount = count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / NUMBERS4_PAGE_SIZE));

  if (requestedPage > totalPages && totalCount > 0) {
    redirect(`/numbers4/result?page=${totalPages}`);
  }

  const page = Math.min(requestedPage, totalPages);
  const from = (page - 1) * NUMBERS4_PAGE_SIZE;
  const to = from + NUMBERS4_PAGE_SIZE - 1;

  const { data, error } = await supabase
    .from("numbers4_draws")
    .select("*")
    .order("draw_number", { ascending: false })
    .range(from, to);

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data ?? []) as Numbers4DrawRow[];

  const { data: recentForHits, error: recentHitsError } = await supabase
    .from("numbers4_draws")
    .select("draw_number, numbers")
    .not("numbers", "is", null)
    .order("draw_number", { ascending: false })
    .limit(100);

  if (recentHitsError) {
    throw new Error(recentHitsError.message);
  }

  const recentHitRows = (recentForHits ?? []) as Pick<
    Numbers4DrawRow,
    "draw_number" | "numbers"
  >[];
  const winningModelHits = await buildWinningModelHitsForDrawList(
    recentHitRows.map((r) => ({
      draw_number: r.draw_number,
      numbers: r.numbers,
    })),
  );

  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-[1600px] flex-1 space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-10">
        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 space-y-4 border-b pb-6 sm:pb-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-2">
                <Badge variant="secondary">Numbers4</Badge>
                <CardTitle className="font-heading text-xl sm:text-2xl">
                  当選番号一覧
                </CardTitle>
                <CardDescription className="text-pretty max-w-2xl text-sm leading-relaxed sm:text-base">
                  回号の新しい順に表示しています。狭い画面では表を横にスクロールできます。ページは
                  URL の{" "}
                  <code className="bg-muted rounded-md px-1.5 py-0.5 font-mono text-xs">
                    page
                  </code>{" "}
                  でも切り替わります。
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <div className="bg-muted/40 border-border/60 border-b px-4 py-3 sm:px-6">
              <Numbers4Pagination
                totalCount={totalCount}
                currentPage={page}
              />
            </div>
            <Numbers4DrawsTable rows={rows} />
            <div className="bg-muted/40 border-border/60 rounded-b-xl border-t px-4 py-3 sm:px-6">
              <Numbers4Pagination
                totalCount={totalCount}
                currentPage={page}
              />
            </div>
          </CardContent>
        </Card>

        {winningModelHits.length > 0 ? (
          <Numbers4RecentModelHits hits={winningModelHits} />
        ) : null}
      </div>
    </div>
  );
}

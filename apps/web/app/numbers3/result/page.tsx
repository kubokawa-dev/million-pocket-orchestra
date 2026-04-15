import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { TodayReferencePanel } from "@/components/today-reference-panel";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createStaticClient } from "@/lib/supabase/static";
import { NUMBERS3_PAGE_SIZE, type Numbers3DrawRow } from "@/lib/numbers3";
import {
  loadNumbers3PredictionBundleForDraw,
  resolveNumbers3TargetDrawNumber,
} from "@/lib/numbers3-predictions/load-numbers3";

import { Numbers3DrawsTable } from "./numbers3-draws-table";
import { Numbers3Pagination } from "./numbers3-pagination";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "ナンバーズ3 当選番号一覧",
  description: "ナンバーズ3の過去の抽選結果（当選番号）を一覧表示します。",
  alternates: { canonical: "/numbers3/result" },
  openGraph: {
    title: "ナンバーズ3 当選番号一覧 | 宝くじAI",
    description: "過去の抽選結果を一覧で確認できます。",
    url: "/numbers3/result",
  },
};

type PageProps = {
  searchParams: Promise<{ page?: string }>;
};

function parsePage(raw: string | undefined): number {
  const n = parseInt(raw ?? "1", 10);
  if (!Number.isFinite(n) || n < 1) return 1;
  return n;
}

export default async function Numbers3ResultPage({ searchParams }: PageProps) {
  const { page: pageParam } = await searchParams;
  const requestedPage = parsePage(pageParam);

  const supabase = createStaticClient();
  const [{ count, error: countError }, nextTargetDraw] = await Promise.all([
    supabase.from("numbers3_draws").select("*", { count: "exact", head: true }),
    resolveNumbers3TargetDrawNumber(),
  ]);
  if (countError) throw new Error(countError.message);

  const nextPreviewBundle =
    await loadNumbers3PredictionBundleForDraw(nextTargetDraw);
  const hasNextPreview = nextPreviewBundle != null;

  const totalCount = count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / NUMBERS3_PAGE_SIZE));
  if (requestedPage > totalPages && totalCount > 0) {
    redirect(`/numbers3/result?page=${totalPages}`);
  }

  const page = Math.min(requestedPage, totalPages);
  const from = (page - 1) * NUMBERS3_PAGE_SIZE;
  const to = from + NUMBERS3_PAGE_SIZE - 1;

  const { data, error } = await supabase
    .from("numbers3_draws")
    .select("*")
    .order("draw_number", { ascending: false })
    .range(from, to);
  if (error) throw new Error(error.message);

  const rows = (data ?? []) as Numbers3DrawRow[];

  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-[1600px] flex-1 space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-10">
        <TodayReferencePanel
          title="Today view"
          latestLabel="いまの参考対象回"
          latestValue={`第 ${nextTargetDraw} 回${hasNextPreview ? "" : "（公開待ち）"}`}
          primaryHref={
            hasNextPreview ? `/numbers3/result/${nextTargetDraw}` : "/numbers3/result"
          }
          primaryLabel={
            hasNextPreview ? `第 ${nextTargetDraw} 回へ進む` : "次回詳細は公開待ち"
          }
          secondaryHref="/numbers3"
          secondaryLabel="ナンバーズ3トップ"
          apiHref="/api/numbers3/latest"
          apiLabel="GET /api/numbers3/latest"
          accentClassName="border-emerald-500/20 bg-emerald-500/5"
        />

        {!hasNextPreview ? (
          <Card className="border-dashed border-emerald-500/30 bg-muted/20 shadow-none">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">次回詳細ページの公開待ち</CardTitle>
              <CardDescription>
                第 {nextTargetDraw} 回向けの予測データがまだ公開されていないため、詳細ページは未開示です。
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 space-y-4 border-b pb-6 sm:pb-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-2">
                <Badge variant="secondary">Numbers3</Badge>
                <CardTitle className="font-heading text-xl sm:text-2xl">
                  当選番号一覧
                </CardTitle>
                <CardDescription className="text-pretty max-w-2xl text-sm leading-relaxed sm:text-base">
                  回号の新しい順に表示しています。狭い画面では表を横にスクロールできます。ページは URL
                  の{" "}
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
              <Numbers3Pagination totalCount={totalCount} currentPage={page} />
            </div>
            <Numbers3DrawsTable rows={rows} />
            <div className="bg-muted/40 border-border/60 rounded-b-xl border-t px-4 py-3 sm:px-6">
              <Numbers3Pagination totalCount={totalCount} currentPage={page} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

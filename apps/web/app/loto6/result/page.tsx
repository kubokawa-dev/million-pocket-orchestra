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
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { createStaticClient } from "@/lib/supabase/static";
import { getSiteOrigin } from "@/lib/site";
import { LOTO6_PAGE_SIZE, type Loto6DrawRow } from "@/lib/loto6";

import { Loto6DrawsTable } from "./loto6-draws-table";
import { Loto6Pagination } from "./loto6-pagination";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "ロト6 当選番号一覧",
  description:
    "ロト6の過去の抽選結果（本数字・ボーナス・等級別口数・払戻金・キャリーオーバー）を一覧表示します。",
  alternates: { canonical: "/loto6/result" },
  openGraph: {
    title: "ロト6 当選番号一覧 | 宝くじAI",
    description: "過去の抽選結果を一覧で確認できます。",
    url: "/loto6/result",
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

export default async function Loto6ResultPage({ searchParams }: PageProps) {
  const { page: pageParam } = await searchParams;
  const requestedPage = parsePage(pageParam);

  const supabase = createStaticClient();
  const { count, error: countError } = await supabase
    .from("loto6_draws")
    .select("*", { count: "exact", head: true });

  if (countError) {
    throw new Error(countError.message);
  }

  const totalCount = count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / LOTO6_PAGE_SIZE));

  if (requestedPage > totalPages && totalCount > 0) {
    redirect(`/loto6/result?page=${totalPages}`);
  }

  const page = Math.min(requestedPage, totalPages);
  const from = (page - 1) * LOTO6_PAGE_SIZE;
  const to = from + LOTO6_PAGE_SIZE - 1;

  const { data, error } = await supabase
    .from("loto6_draws")
    .select("*")
    .order("draw_number", { ascending: false })
    .range(from, to);

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data ?? []) as Loto6DrawRow[];

  const origin = getSiteOrigin();
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ロト6", path: "/loto6" },
    { name: "当選番号一覧", path: "/loto6/result" },
  ]);

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "ロト6 当選番号データセット",
    alternateName: "Loto6 Draw Results Dataset",
    description:
      "日本のロト6の過去の抽選結果（本数字・ボーナス・等級別口数・払戻金）を収録したデータセット。公開データから取得。",
    url: `${origin}/loto6/result`,
    distribution: [
      {
        "@type": "DataDownload",
        encodingFormat: "application/json",
        contentUrl: `${origin}/api/loto6/latest`,
      },
    ],
    keywords: ["Loto6", "ロト6", "lottery", "宝くじ", "当選番号", "Japan"],
  };

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetJsonLd) }}
      />
      <div className="mx-auto w-full max-w-[1600px] flex-1 space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-10">
        <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 space-y-4 border-b pb-6 sm:pb-6">
            <div className="space-y-2">
              <Badge
                variant="secondary"
                className="border-amber-500/30 bg-amber-500/10 text-amber-900 dark:border-amber-400/30 dark:bg-amber-400/10 dark:text-amber-100"
              >
                Loto6
              </Badge>
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
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <div className="bg-muted/40 border-border/60 border-b px-4 py-3 sm:px-6">
              <Loto6Pagination totalCount={totalCount} currentPage={page} />
            </div>
            <Loto6DrawsTable rows={rows} />
            <div className="bg-muted/40 border-border/60 rounded-b-xl border-t px-4 py-3 sm:px-6">
              <Loto6Pagination totalCount={totalCount} currentPage={page} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

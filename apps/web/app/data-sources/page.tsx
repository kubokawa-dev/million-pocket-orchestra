import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLinkIcon } from "lucide-react";

import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { NUMBERS4_OFFICIAL_LINKS } from "@/lib/numbers4-official-sources";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "データの出所・API",
  description:
    "宝くじAIのデータソース、公式照合先、公開API・RSS・oEmbed・OpenAPI の一覧。非公式サイトである旨の説明。",
  alternates: { canonical: "/data-sources" },
  openGraph: {
    title: "データの出所・API | 宝くじAI",
    description:
      "公式結果の二次利用、公開エンドポイント、機械可読フォーマットへのリンク。",
    url: "/data-sources",
  },
};

export default function DataSourcesPage() {
  const origin = getSiteOrigin();
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "データの出所・API", path: "/data-sources" },
  ]);

  const machineLinks = [
    { href: "/api/numbers3/latest", label: "GET /api/numbers3/latest", note: "直近のナンバーズ3抽選行など（JSON）" },
    { href: "/api/numbers4/latest", label: "GET /api/numbers4/latest", note: "直近のナンバーズ4抽選行など（JSON）" },
    { href: "/api/openapi.json", label: "GET /api/openapi.json", note: "OpenAPI 3.1 仕様" },
    {
      href: `/api/oembed?url=${encodeURIComponent(`${origin}/numbers4/result/1`)}&format=json`,
      label: "GET /api/oembed",
      note: "oEmbed（url= に当選ページの正規URLを指定）",
    },
    { href: "/feed.xml", label: "GET /feed.xml", note: "ブログ記事 RSS 2.0" },
    { href: "/sitemap.xml", label: "GET /sitemap.xml", note: "XML サイトマップ（hreflang）" },
    { href: "/llms.txt", label: "GET /llms.txt", note: "LLM 向け短いサイト要約" },
    { href: "/llms-full.txt", label: "GET /llms-full.txt", note: "LLM 向け詳細要約＋記事全文" },
  ] as const;

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            データの出所・API
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            <strong className="text-foreground">宝くじAIは非公式</strong>
            です。当せんの確認は必ず公式情報で行ってください。ここでは技術的なデータの流れと、検索・連携向けの公開 URL をまとめます。
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">公式の照合先</CardTitle>
            <CardDescription>
              画面上の数字が正しいかは、必ず次の公式サイトで確認してください。
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {NUMBERS4_OFFICIAL_LINKS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  buttonVariants({ variant: "secondary", size: "sm" }),
                  "h-auto justify-start gap-2 py-3",
                )}
              >
                <ExternalLinkIcon className="size-4 shrink-0 opacity-70" />
                <span className="text-left">
                  <span className="block font-medium">{item.label}</span>
                  <span className="text-muted-foreground text-xs font-normal">
                    {item.note}
                  </span>
                </span>
              </a>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">このサイトのデータについて</CardTitle>
            <CardDescription>
              抽選結果は公開情報の範囲で収集し、当サイトのサーバー側で保管したものを表示しています。取り込み遅延や表記揺れがある場合があります。
            </CardDescription>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
            <p>
              予測値は日次ジョブが出力した JSON（オンライン上の最新を優先し、無ければサイトに同梱したファイル）を参照しており、当せんを保証するものではありません。
            </p>
            <p>
              ライセンスはリポジトリのライセンスに従います。データセットの再利用を検討する場合は、公式結果の利用条件もあわせて確認してください。
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">機械可読・連携用 URL</CardTitle>
            <CardDescription>
              検索エンジン、RSS リーダー、LLM、外部ツールからの参照用です。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {machineLinks.map((item) => (
              <div
                key={item.href}
                className="border-border/60 flex flex-col gap-1 rounded-lg border px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <Link
                    href={item.href}
                    className="text-primary text-sm font-medium underline-offset-4 hover:underline"
                  >
                    {item.label}
                  </Link>
                  <p className="text-muted-foreground text-xs">{item.note}</p>
                </div>
                <code className="text-muted-foreground hidden font-mono text-[0.65rem] sm:block sm:max-w-[200px] sm:truncate sm:text-right">
                  {absoluteUrl(item.href)}
                </code>
              </div>
            ))}
          </CardContent>
        </Card>

        <p className="text-muted-foreground text-center text-sm">
          <Link href="/faq" className="text-primary underline-offset-4 hover:underline">
            よくある質問
          </Link>
          {" · "}
          <Link href="/en" className="text-primary underline-offset-4 hover:underline">
            English overview
          </Link>
        </p>
      </div>
    </div>
  );
}

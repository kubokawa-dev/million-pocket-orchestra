import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRightIcon, BookOpenIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { getPostsSortedByDate } from "@/lib/blog/posts";

export const metadata: Metadata = {
  title: "ブログ",
  description:
    "ナンバーズ4・当選番号一覧・予測ダッシュボードの使い方や読み方を記事にまとめています。",
  alternates: { canonical: "/blog" },
  openGraph: {
    title: "ブログ | 宝くじAI",
    description:
      "サイトの使い方、予測・統計ページの見方など、SEO向けの解説記事を掲載しています。",
    url: "/blog",
  },
};

export default function BlogIndexPage() {
  const posts = getPostsSortedByDate();
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "ブログ", path: "/blog" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <Badge variant="secondary" className="mb-1">
            <BookOpenIcon data-icon="inline-start" className="size-3.5" />
            Blog
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            ブログ
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            宝くじAIの使い方や、ナンバーズ4の結果・予測まわりの読み方を整理した記事です。
            海外向けの英語解説は{" "}
            <Link
              href="/en/blog"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              English blog
            </Link>
            からどうぞ。
          </p>
        </header>

        <ul className="space-y-4">
          {posts.map((post) => (
            <li key={post.slug}>
              <Link href={`/blog/${post.slug}`} className="group block">
                <Card className="border-border/80 transition-shadow group-hover:shadow-md">
                  <CardHeader className="pb-4">
                    <p className="text-muted-foreground mb-1 text-xs">
                      <time dateTime={post.publishedAt}>{post.publishedAt}</time>
                    </p>
                    <CardTitle className="text-lg leading-snug group-hover:underline">
                      {post.title}
                    </CardTitle>
                    <CardDescription className="text-sm leading-relaxed">
                      {post.description}
                    </CardDescription>
                    <span className="text-primary mt-2 inline-flex items-center gap-1 text-sm font-medium">
                      続きを読む
                      <ArrowRightIcon className="size-4 transition-transform group-hover:translate-x-0.5" />
                    </span>
                  </CardHeader>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

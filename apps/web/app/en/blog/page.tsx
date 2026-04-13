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
import { getEnPostsSortedByDate } from "@/lib/blog/posts-en";
import { absoluteUrl } from "@/lib/site";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "English blog — Japan Numbers4, Numbers3, and Loto6 guides",
  description:
    "English guides for Japan Numbers4, Numbers3, and Loto6: latest results, prediction context, official verification, stats, trends, and how to use Takarakuji AI.",
  keywords: [
    "Japan Numbers4 results",
    "Numbers4 prediction today",
    "Numbers3 result today Japan",
    "latest Loto6 results Japan",
    "official Numbers4 results",
    "Takarakuji AI English blog",
  ],
  alternates: {
    canonical: "/en/blog",
    languages: {
      ja: absoluteUrl("/blog"),
      en: absoluteUrl("/en/blog"),
    },
  },
  openGraph: {
    title: "English blog | Takarakuji AI",
    description:
      "English guides for international readers: latest Japan lottery results, prediction context, official verification, stats, and trends.",
    url: absoluteUrl("/en/blog"),
    locale: "en_US",
    alternateLocale: ["ja_JP"],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "English blog | Takarakuji AI",
    description:
      "English guides for Numbers4, Numbers3, and Loto6 in Japan: latest results, official verification, stats, and trends.",
  },
};

export default function EnglishBlogIndexPage() {
  const posts = getEnPostsSortedByDate();
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "English", path: "/en" },
    { name: "Blog", path: "/en/blog" },
  ]);

  return (
    <div lang="en" className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <Badge variant="secondary" className="mb-1">
            <BookOpenIcon data-icon="inline-start" className="size-3.5" />
            Blog · English
          </Badge>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            English articles
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            English guides for international readers looking for Japan Numbers4,
            Numbers3, and Loto6 results, prediction context, official verification,
            stats, and trend pages. The app UI is mostly Japanese; these posts explain
            how to use it responsibly.{" "}
            <Link
              href="/blog"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              Japanese blog
            </Link>
            .
          </p>
        </header>

        <ul className="space-y-4">
          {posts.map((post) => (
            <li key={post.slug}>
              <Link href={`/en/blog/${post.slug}`} className="group block">
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
                      Read more
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

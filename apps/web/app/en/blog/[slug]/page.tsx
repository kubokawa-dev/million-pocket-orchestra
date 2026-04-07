import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArrowLeftIcon } from "lucide-react";

import { MarkdownBody } from "@/components/markdown-body";
import {
  getAllEnBlogSlugs,
  getEnPostBySlug,
} from "@/lib/blog/posts-en";
import { buttonVariants } from "@/components/ui/button-variants";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { cn } from "@/lib/utils";

type PageProps = { params: Promise<{ slug: string }> };

export const revalidate = 3600;

export function generateStaticParams() {
  return getAllEnBlogSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = getEnPostBySlug(slug);
  if (!post) return { title: "Not found" };
  return {
    title: post.title,
    description: post.description,
    alternates: {
      canonical: `/en/blog/${post.slug}`,
      languages: {
        ja: absoluteUrl("/blog"),
        en: absoluteUrl(`/en/blog/${post.slug}`),
      },
    },
    openGraph: {
      title: `${post.title} · Takarakuji AI`,
      description: post.description,
      url: absoluteUrl(`/en/blog/${post.slug}`),
      type: "article",
      publishedTime: post.publishedAt,
      locale: "en_US",
      alternateLocale: ["ja_JP"],
    },
  };
}

export default async function EnglishBlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = getEnPostBySlug(slug);
  if (!post) notFound();

  const origin = getSiteOrigin();
  const url = `${origin}/en/blog/${post.slug}`;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    datePublished: post.publishedAt,
    inLanguage: "en",
    author: { "@type": "Organization", name: "Takarakuji AI" },
    publisher: {
      "@type": "Organization",
      name: "Takarakuji AI",
      url: origin,
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
  };

  return (
    <div lang="en" className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 sm:px-6 sm:py-14">
        <Link
          href="/en/blog"
          className={cn(
            buttonVariants({ variant: "ghost", size: "sm" }),
            "text-muted-foreground -ml-2 mb-8 gap-1",
          )}
        >
          <ArrowLeftIcon className="size-4" />
          English blog index
        </Link>
        <header className="mb-10 space-y-2">
          <p className="text-muted-foreground text-sm">
            <time dateTime={post.publishedAt}>{post.publishedAt}</time>
          </p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            {post.title}
          </h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            {post.description}
          </p>
        </header>
        <MarkdownBody markdown={post.bodyMarkdown} />
      </article>
    </div>
  );
}

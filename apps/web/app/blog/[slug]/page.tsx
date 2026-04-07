import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeftIcon } from "lucide-react";

import { MarkdownBody } from "@/components/markdown-body";
import { buttonVariants } from "@/components/ui/button-variants";
import { getAllBlogSlugs, getPostBySlug } from "@/lib/blog/posts";
import { cn } from "@/lib/utils";

type PageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return getAllBlogSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return { title: "記事が見つかりません" };
  return {
    title: post.title,
    description: post.description,
    alternates: { canonical: `/blog/${post.slug}` },
    openGraph: {
      title: `${post.title} · Million Pocket`,
      description: post.description,
      url: `/blog/${post.slug}`,
      type: "article",
      publishedTime: post.publishedAt,
    },
  };
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    datePublished: post.publishedAt,
    inLanguage: "ja",
    author: { "@type": "Organization", name: "Million Pocket" },
    publisher: { "@type": "Organization", name: "Million Pocket" },
  };

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 sm:px-6 sm:py-14">
        <Link
          href="/blog"
          className={cn(
            buttonVariants({ variant: "ghost", size: "sm" }),
            "text-muted-foreground -ml-2 mb-8 gap-1",
          )}
        >
          <ArrowLeftIcon className="size-4" />
          ブログ一覧
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

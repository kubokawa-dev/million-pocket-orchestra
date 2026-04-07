"use client";

import { CheckIcon, LinkIcon, Share2Icon } from "lucide-react";
import { useCallback, useState } from "react";

import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

type PageShareToolbarProps = {
  /** 共有する絶対 URL */
  url: string;
  /** SNS 用の短いタイトル */
  title: string;
  className?: string;
};

export function PageShareToolbar({
  url,
  title,
  className,
}: PageShareToolbarProps) {
  const [copied, setCopied] = useState(false);

  const onCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  }, [url]);

  const xHref = `https://twitter.com/intent/tweet?${new URLSearchParams({
    url,
    text: title,
  }).toString()}`;

  return (
    <div
      className={cn(
        "border-border/60 bg-muted/30 flex flex-wrap items-center gap-2 rounded-lg border px-3 py-2",
        className,
      )}
    >
      <span className="text-muted-foreground flex items-center gap-1 text-xs font-medium">
        <Share2Icon className="size-3.5" />
        共有
      </span>
      <button
        type="button"
        className={cn(
          buttonVariants({ variant: "secondary", size: "sm" }),
          "h-8 gap-1 text-xs",
        )}
        onClick={onCopy}
      >
        {copied ? (
          <CheckIcon className="size-3.5" />
        ) : (
          <LinkIcon className="size-3.5" />
        )}
        {copied ? "コピーしたよ" : "URL をコピー"}
      </button>
      <a
        href={xHref}
        target="_blank"
        rel="noopener noreferrer"
        className={cn(
          buttonVariants({ variant: "outline", size: "sm" }),
          "h-8 text-xs",
        )}
      >
        X でポスト
      </a>
    </div>
  );
}

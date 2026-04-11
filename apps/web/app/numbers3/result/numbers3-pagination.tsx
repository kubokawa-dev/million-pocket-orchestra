import Link from "next/link";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";

import { buttonVariants } from "@/components/ui/button-variants";
import { NUMBERS3_PAGE_SIZE } from "@/lib/numbers3";
import { cn } from "@/lib/utils";

type Numbers3PaginationProps = {
  totalCount: number;
  currentPage: number;
};

export function Numbers3Pagination({
  totalCount,
  currentPage,
}: Numbers3PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalCount / NUMBERS3_PAGE_SIZE));
  const page = Math.min(Math.max(1, currentPage), totalPages);

  const prevHref = page <= 1 ? null : `/numbers3/result?page=${page - 1}`;
  const nextHref =
    page >= totalPages ? null : `/numbers3/result?page=${page + 1}`;

  const btnClass = cn(
    buttonVariants({ variant: "outline", size: "sm" }),
    "inline-flex min-w-[5.5rem] justify-center no-underline",
  );

  return (
    <div className="flex flex-col items-stretch gap-4 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-muted-foreground text-center text-sm sm:text-left">
        <span className="text-foreground font-medium tabular-nums">
          {totalCount.toLocaleString("ja-JP")}
        </span>
        件中 · 1ページ{" "}
        <span className="tabular-nums">{NUMBERS3_PAGE_SIZE}</span> 件
      </p>
      <div className="flex items-center justify-center gap-2 sm:justify-end">
        {prevHref ? (
          <Link
            href={prevHref}
            className={btnClass}
            aria-label="前のページ"
            scroll={true}
          >
            <ChevronLeftIcon data-icon="inline-start" />
            前へ
          </Link>
        ) : (
          <span className={cn(btnClass, "pointer-events-none opacity-50")} aria-disabled>
            <ChevronLeftIcon data-icon="inline-start" />
            前へ
          </span>
        )}
        <span
          className="bg-background border-border text-foreground inline-flex min-w-[7.5rem] items-center justify-center rounded-lg border px-3 py-1.5 text-sm font-medium tabular-nums shadow-sm"
          aria-live="polite"
        >
          {page} / {totalPages}
        </span>
        {nextHref ? (
          <Link
            href={nextHref}
            className={btnClass}
            aria-label="次のページ"
            scroll={true}
          >
            次へ
            <ChevronRightIcon data-icon="inline-end" />
          </Link>
        ) : (
          <span className={cn(btnClass, "pointer-events-none opacity-50")} aria-disabled>
            次へ
            <ChevronRightIcon data-icon="inline-end" />
          </span>
        )}
      </div>
    </div>
  );
}

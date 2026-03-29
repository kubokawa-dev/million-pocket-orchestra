"use client";

import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";
import { parseAsInteger, useQueryState } from "nuqs";

import { Button } from "@/components/ui/button";
import { NUMBERS4_PAGE_SIZE } from "@/lib/numbers4";
import { cn } from "@/lib/utils";

type Numbers4PaginationProps = {
  totalCount: number;
};

export function Numbers4Pagination({ totalCount }: Numbers4PaginationProps) {
  const [page, setPage] = useQueryState(
    "page",
    parseAsInteger.withDefault(1).withOptions({ history: "push" }),
  );

  const totalPages = Math.max(1, Math.ceil(totalCount / NUMBERS4_PAGE_SIZE));
  const current = Math.min(Math.max(1, page ?? 1), totalPages);

  return (
    <div
      className={cn(
        "flex flex-col items-stretch gap-4",
        "sm:flex-row sm:items-center sm:justify-between",
      )}
    >
      <p className="text-muted-foreground text-center text-sm sm:text-left">
        <span className="text-foreground font-medium tabular-nums">
          {totalCount.toLocaleString("ja-JP")}
        </span>
        件中 · 1ページ{" "}
        <span className="tabular-nums">{NUMBERS4_PAGE_SIZE}</span> 件
      </p>
      <div className="flex items-center justify-center gap-2 sm:justify-end">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={current <= 1}
          onClick={() => void setPage(current - 1)}
          aria-label="前のページ"
          className="min-w-[5.5rem]"
        >
          <ChevronLeftIcon data-icon="inline-start" />
          前へ
        </Button>
        <span
          className="bg-background border-border text-foreground inline-flex min-w-[7.5rem] items-center justify-center rounded-lg border px-3 py-1.5 text-sm font-medium tabular-nums shadow-sm"
          aria-live="polite"
        >
          {current} / {totalPages}
        </span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={current >= totalPages}
          onClick={() => void setPage(current + 1)}
          aria-label="次のページ"
          className="min-w-[5.5rem]"
        >
          次へ
          <ChevronRightIcon data-icon="inline-end" />
        </Button>
      </div>
    </div>
  );
}

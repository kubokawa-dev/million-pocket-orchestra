"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { SiteNav } from "@/components/site-nav";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const pathname = usePathname();
  const isInvestorPage = pathname === "/investors" || pathname.startsWith("/investors/");

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full border-b backdrop-blur-md",
        isInvestorPage
          ? "border-[#c8a45a]/20 bg-[#090b08]/80 text-[#f6ecd2] supports-[backdrop-filter]:bg-[#090b08]/70"
          : "border-border/60 bg-background/80 supports-[backdrop-filter]:bg-background/70",
      )}
    >
      <div className="mx-auto flex max-w-[1600px] flex-col gap-3 px-4 py-3 sm:h-14 sm:flex-row sm:items-center sm:justify-between sm:gap-6 sm:py-0 sm:px-6">
        <div className="flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-1 sm:shrink-0">
          <Link
            href="/"
            className={cn(
              "text-base font-semibold tracking-tight transition-colors",
              isInvestorPage
                ? "text-[#fff8e7] hover:text-[#f4d58d]"
                : "text-foreground hover:text-foreground/80",
            )}
          >
            宝くじAI
          </Link>
          <span
            className={cn(
              "hidden text-xs sm:inline",
              isInvestorPage ? "text-[#cbbd98]" : "text-muted-foreground",
            )}
            aria-hidden
          >
            ·
          </span>
          {isInvestorPage ? (
            <span className="hidden max-w-[14rem] truncate text-xs font-medium uppercase tracking-[0.18em] text-[#d7b56c] sm:inline">
              Private Investor Brief
            </span>
          ) : (
            <Link
              href="/responsible-use#ethical"
              className="text-muted-foreground hover:text-foreground hidden max-w-[11rem] truncate text-xs font-medium underline-offset-4 transition-colors hover:underline sm:inline"
            >
              倫理的配慮
            </Link>
          )}
        </div>
        <SiteNav />
      </div>
    </header>
  );
}

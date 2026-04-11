import Link from "next/link";

import { SiteNav } from "@/components/site-nav";

export function SiteHeader() {
  return (
    <header className="bg-background/80 supports-[backdrop-filter]:bg-background/70 sticky top-0 z-50 w-full border-b border-border/60 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1600px] flex-col gap-3 px-4 py-3 sm:h-14 sm:flex-row sm:items-center sm:justify-between sm:gap-6 sm:py-0 sm:px-6">
        <div className="flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-1 sm:shrink-0">
          <Link
            href="/"
            className="text-foreground hover:text-foreground/80 text-base font-semibold tracking-tight transition-colors"
          >
            宝くじAI
          </Link>
          <span className="text-muted-foreground hidden text-xs sm:inline" aria-hidden>
            ·
          </span>
          <Link
            href="/responsible-use#ethical"
            className="text-muted-foreground hover:text-foreground hidden max-w-[11rem] truncate text-xs font-medium underline-offset-4 transition-colors hover:underline sm:inline"
          >
            倫理的配慮
          </Link>
        </div>
        <SiteNav />
      </div>
    </header>
  );
}

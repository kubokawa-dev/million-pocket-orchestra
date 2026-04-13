"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const footerLinks = [
  { href: "/investors", label: "投資家向け" },
  { href: "/blog", label: "ブログ" },
  { href: "/faq", label: "よくある質問" },
  { href: "/responsible-use#ethical", label: "倫理的配慮・健全な利用" },
  { href: "/terms", label: "利用規約（草案）" },
  { href: "/data-sources", label: "データ・API" },
  { href: "/numbers3", label: "ナンバーズ3" },
  { href: "/numbers4", label: "ナンバーズ4" },
  { href: "/loto6", label: "ロト6" },
  { href: "/loto6/stats", label: "ロト6 統計" },
  { href: "/en", label: "English" },
  { href: "/en/blog", label: "Blog (EN)" },
  { href: "/llms.txt", label: "llms.txt（AI向け要約）" },
] as const;

export function SiteFooter() {
  const pathname = usePathname();
  const isInvestorPage = pathname === "/investors" || pathname.startsWith("/investors/");

  return (
    <footer
      className={cn(
        "mt-auto border-t",
        isInvestorPage
          ? "border-[#c8a45a]/18 bg-[#090b08] text-[#d7ccb3]"
          : "border-border/60 bg-background/80",
      )}
    >
      <div className="mx-auto flex max-w-[1600px] flex-col gap-4 px-4 py-8 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="text-sm">
          <span className={cn("font-medium", isInvestorPage ? "text-[#fff8e7]" : "text-foreground")}>
            宝くじAI
          </span>
          <span className={cn(isInvestorPage ? "text-[#cbbd98]" : "text-muted-foreground")}>
            {isInvestorPage
              ? " · Investor-facing narrative layer"
              : "（ナンバーズ3・4 / ロト6）"}
          </span>
        </p>
        <nav aria-label="フッターナビゲーション">
          <ul className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
            {footerLinks.map(({ href, label }) => (
              <li key={href}>
                <Link
                  href={href}
                  className={cn(
                    "underline-offset-4 transition-colors hover:underline",
                    isInvestorPage
                      ? "hover:text-[#fff8e7] text-[#d7ccb3]"
                      : "hover:text-foreground",
                  )}
                >
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </footer>
  );
}

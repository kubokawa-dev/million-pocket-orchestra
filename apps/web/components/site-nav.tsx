"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "ホーム" },
  { href: "/numbers3", label: "ナンバーズ3" },
  { href: "/numbers4", label: "ナンバーズ4" },
  { href: "/loto6", label: "ロト6" },
  { href: "/blog", label: "ブログ" },
  { href: "/faq", label: "FAQ" },
  { href: "/responsible-use#ethical", label: "倫理的配慮" },
] as const;

export function SiteNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="メインナビゲーション"
      className="-mx-1 flex max-w-[100vw] gap-1 overflow-x-auto px-1 py-0.5 [scrollbar-width:none] sm:max-w-none [&::-webkit-scrollbar]:hidden"
    >
      {links.map(({ href, label }) => {
        const pathOnly = href.split("#")[0] ?? href;
        const active =
          pathOnly === "/"
            ? pathname === "/"
            : pathname === pathOnly || pathname.startsWith(`${pathOnly}/`);

        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
              active
                ? "bg-foreground text-background shadow-sm"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

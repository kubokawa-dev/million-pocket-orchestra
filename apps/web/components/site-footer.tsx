import Link from "next/link";

const footerLinks = [
  { href: "/blog", label: "ブログ" },
  { href: "/faq", label: "よくある質問" },
  { href: "/data-sources", label: "データ・API" },
  { href: "/numbers3", label: "ナンバーズ3" },
  { href: "/numbers4", label: "ナンバーズ4" },
  { href: "/loto6", label: "ロト6" },
  { href: "/en", label: "English" },
  { href: "/en/blog", label: "Blog (EN)" },
  { href: "/llms.txt", label: "llms.txt（AI向け要約）" },
] as const;

export function SiteFooter() {
  return (
    <footer className="border-border/60 bg-background/80 mt-auto border-t">
      <div className="text-muted-foreground mx-auto flex max-w-[1600px] flex-col gap-4 px-4 py-8 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="text-sm">
          <span className="text-foreground font-medium">宝くじAI</span>
          <span className="text-muted-foreground">（ナンバーズ3・4 / ロト6）</span>
        </p>
        <nav aria-label="フッターナビゲーション">
          <ul className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
            {footerLinks.map(({ href, label }) => (
              <li key={href}>
                <Link
                  href={href}
                  className="hover:text-foreground underline-offset-4 transition-colors hover:underline"
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

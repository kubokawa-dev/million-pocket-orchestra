import Link from "next/link";
import { ExternalLinkIcon } from "lucide-react";

import { PageShareToolbar } from "@/components/page-share-toolbar";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Numbers4DrawRow } from "@/lib/numbers4";
import { NUMBERS4_OFFICIAL_LINKS } from "@/lib/numbers4-official-sources";
import { absoluteUrl } from "@/lib/site";
import { cn } from "@/lib/utils";

type Numbers4DrawPageChromeProps = {
  drawNumber: number;
  row: Numbers4DrawRow | null;
  prevDraw: number | null;
  nextDraw: number | null;
  sameMonthDraws: number[];
};

export function Numbers4DrawPageChrome({
  drawNumber,
  row,
  prevDraw,
  nextDraw,
  sameMonthDraws,
}: Numbers4DrawPageChromeProps) {
  const pageUrl = absoluteUrl(`/numbers4/result/${drawNumber}`);
  const shareTitle = `第${drawNumber}回 ナンバーズ4 | 宝くじAI`;

  return (
    <div className="mx-auto w-full max-w-[1600px] space-y-4 px-4 pt-6 sm:px-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {prevDraw != null ? (
            <Link
              href={`/numbers4/result/${prevDraw}`}
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "tabular-nums",
              )}
            >
              ← 第 {prevDraw} 回
            </Link>
          ) : null}
          {nextDraw != null ? (
            <Link
              href={`/numbers4/result/${nextDraw}`}
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "tabular-nums",
              )}
            >
              第 {nextDraw} 回 →
            </Link>
          ) : null}
          <Link
            href="/numbers4/result"
            className={cn(
              buttonVariants({ variant: "ghost", size: "sm" }),
              "text-muted-foreground",
            )}
          >
            当選番号一覧
          </Link>
        </div>
        <PageShareToolbar url={pageUrl} title={shareTitle} className="lg:max-w-md" />
      </div>

      <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">公式結果の確認（必ずご自身で照合を）</CardTitle>
          <CardDescription className="text-pretty text-sm leading-relaxed">
            このサイトは<strong className="text-foreground">非公式</strong>
            です。当せん番号・払戻は必ず次の公式情報で確認してください。DB
            取り込みのタイムラグで表示が遅れる場合があります。
            {row?.draw_date ? (
              <>
                {" "}
                本ページの抽選日:{" "}
                <span className="text-foreground font-medium tabular-nums">
                  {row.draw_date.trim()}
                </span>
                。
              </>
            ) : null}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
          {NUMBERS4_OFFICIAL_LINKS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                buttonVariants({ variant: "secondary", size: "sm" }),
                "inline-flex h-auto min-h-9 flex-1 flex-col items-start gap-0.5 py-2 sm:flex-none",
              )}
            >
              <span className="flex items-center gap-1 font-medium">
                {item.label}
                <ExternalLinkIcon className="size-3.5 opacity-70" />
              </span>
              <span className="text-muted-foreground font-normal">{item.note}</span>
            </a>
          ))}
        </CardContent>
      </Card>

      {sameMonthDraws.length > 0 ? (
        <Card className="border-border/60 bg-muted/20">
          <CardHeader className="py-3 pb-2">
            <CardTitle className="text-sm font-medium">
              同じ月の他の回（内部リンク）
            </CardTitle>
            <CardDescription className="text-xs">
              回号をまたいだ閲覧・クロール用の導線です。
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2 pb-4 pt-0">
            {sameMonthDraws.map((n) => (
              <Link
                key={n}
                href={`/numbers4/result/${n}`}
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  "tabular-nums",
                )}
              >
                第 {n} 回
              </Link>
            ))}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

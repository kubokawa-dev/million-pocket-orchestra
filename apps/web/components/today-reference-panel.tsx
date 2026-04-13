import Link from "next/link";
import {
  ArrowRightIcon,
  BadgeInfoIcon,
  CalendarDaysIcon,
  DatabaseIcon,
  ShieldCheckIcon,
} from "lucide-react";

import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

type TodayReferencePanelProps = {
  title: string;
  latestLabel: string;
  latestValue: string;
  primaryHref: string;
  primaryLabel: string;
  secondaryHref: string;
  secondaryLabel: string;
  apiHref: string;
  apiLabel: string;
  statsHref?: string;
  statsLabel?: string;
  accentClassName?: string;
};

export function TodayReferencePanel({
  title,
  latestLabel,
  latestValue,
  primaryHref,
  primaryLabel,
  secondaryHref,
  secondaryLabel,
  apiHref,
  apiLabel,
  statsHref,
  statsLabel,
  accentClassName = "border-cyan-500/20 bg-cyan-500/5",
}: TodayReferencePanelProps) {
  return (
    <Card className={cn("border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10", accentClassName)}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <CalendarDaysIcon className="text-muted-foreground size-5" />
          <CardTitle className="text-lg">{title}</CardTitle>
        </div>
        <CardDescription>
          今日見るべき入口と、検証に使うべき入口を先に分けています。
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-xl border border-border/70 bg-background/70 px-4 py-3">
          <p className="text-muted-foreground text-xs font-medium tracking-wide">
            {latestLabel}
          </p>
          <p className="text-foreground mt-1 text-lg font-semibold">{latestValue}</p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <Link
            href={primaryHref}
            className={cn(buttonVariants({ size: "lg" }), "w-full justify-center gap-2 shadow-sm sm:w-auto")}
          >
            {primaryLabel}
            <ArrowRightIcon className="size-4" />
          </Link>
          <Link
            href={secondaryHref}
            className={cn(buttonVariants({ variant: "outline", size: "lg" }), "w-full justify-center gap-2 sm:w-auto")}
          >
            {secondaryLabel}
            <ArrowRightIcon className="size-4" />
          </Link>
          {statsHref && statsLabel ? (
            <Link
              href={statsHref}
              className={cn(buttonVariants({ variant: "outline", size: "lg" }), "w-full justify-center gap-2 sm:w-auto")}
            >
              {statsLabel}
              <ArrowRightIcon className="size-4" />
            </Link>
          ) : null}
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-border/70 bg-background/60 px-4 py-3">
            <div className="mb-2 flex items-center gap-2 text-foreground">
              <ShieldCheckIcon className="size-4" />
              <p className="text-sm font-medium">信頼の置きどころ</p>
            </div>
            <p className="text-muted-foreground text-xs leading-relaxed sm:text-sm">
              公式結果は必ず公式情報で確認。ここでのモデル表示は参考用で、当せんを保証しません。
            </p>
          </div>
          <div className="rounded-xl border border-border/70 bg-background/60 px-4 py-3">
            <div className="mb-2 flex items-center gap-2 text-foreground">
              <DatabaseIcon className="size-4" />
              <p className="text-sm font-medium">AI / ツール向け入口</p>
            </div>
            <Link
              href={apiHref}
              className="text-primary inline-flex items-center gap-1 text-xs font-medium underline-offset-4 hover:underline sm:text-sm"
            >
              {apiLabel}
              <ArrowRightIcon className="size-3.5" />
            </Link>
            <p className="text-muted-foreground mt-1 text-xs leading-relaxed sm:text-sm">
              最新スナップショットを機械可読で参照できます。
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-dashed border-border/70 bg-muted/20 px-4 py-3">
          <div className="mb-2 flex items-center gap-2 text-foreground">
            <BadgeInfoIcon className="size-4" />
            <p className="text-sm font-medium">使い方の基本</p>
          </div>
          <p className="text-muted-foreground text-xs leading-relaxed sm:text-sm">
            まず最新結果か今日の参考表示を開き、そのあとで統計やトレンドを見て、最後に公式情報で照合する流れが安全です。
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

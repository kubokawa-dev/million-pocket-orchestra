import Link from "next/link";
import { ArrowRightIcon, SparklesIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col">
      <section className="flex flex-1 flex-col justify-center px-4 py-16 sm:px-6 sm:py-20 lg:py-28">
        <div className="mx-auto w-full max-w-2xl text-center">
          <Badge variant="secondary" className="mb-5">
            <SparklesIcon data-icon="inline-start" />
            Numbers4
          </Badge>
          <h1 className="text-foreground mb-5 text-4xl font-semibold tracking-tight sm:text-5xl sm:leading-tight">
            抽選結果を、
            <br className="sm:hidden" />
            すっきり見やすく
          </h1>
          <p className="text-muted-foreground mx-auto mb-10 max-w-lg text-base leading-relaxed sm:text-lg">
            ナンバーズ4の過去当選番号を一覧でチェック。スマホでも横スクロールで全項目を確認できます。
          </p>
          <div className="flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
            <Link
              href="/numbers4"
              className={cn(
                buttonVariants({ size: "lg" }),
                "gap-2 shadow-sm sm:min-w-[220px]",
              )}
            >
              予測ダッシュボード
              <ArrowRightIcon data-icon="inline-end" className="size-4" />
            </Link>
            <Link
              href="/numbers4/result"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "justify-center sm:min-w-[200px]",
              )}
            >
              当選番号一覧
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

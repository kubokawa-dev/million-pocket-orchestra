import Link from "next/link";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatContributorSlugLine } from "@/lib/numbers4-predictions/ensemble-contributors";
import type { Numbers4DrawWinningModelHit } from "@/lib/numbers4-predictions/types";
import { cn } from "@/lib/utils";

export type Numbers4RecentModelHitsProps = {
  hits: Numbers4DrawWinningModelHit[];
  /** 省略時は「直近 N 回 · …」 */
  title?: string;
  /** 省略時は公式当選＋method 照合の標準説明 */
  description?: ReactNode;
  /** グレー帯の先頭に足す一文（省略可） */
  bannerLead?: string;
  /** 表が空のとき */
  emptyMessage?: string;
  /** 公式当選バッジ（目立たせたいとき） */
  emphasizeOfficial?: boolean;
};

function SlugCell({
  slugs,
  variant,
}: {
  slugs: string[];
  variant: "exact" | "box";
}) {
  if (slugs.length === 0) {
    return (
      <span className="text-muted-foreground text-xs tabular-nums">0</span>
    );
  }
  return (
    <div className="flex max-h-24 flex-wrap gap-1 overflow-y-auto">
      {slugs.map((s) => (
        <Badge
          key={s}
          variant="outline"
          className={cn(
            "font-mono text-[0.65rem] font-normal",
            variant === "exact" &&
              "border-emerald-600/40 bg-emerald-500/10 text-emerald-950 dark:text-emerald-100",
            variant === "box" &&
              "border-amber-600/40 bg-amber-500/10 text-amber-950 dark:text-amber-100",
          )}
          title={formatContributorSlugLine(s)}
        >
          {s}
        </Badge>
      ))}
    </div>
  );
}

const defaultDescription = (
  <>
    <span className="block">
      <strong className="text-foreground">当選列の4桁は、宝くじの実際の抽選結果</strong>
      （当サイトに取り込んだ公式当選番号）です。アンサンブル上位の予測リストから数字を拾っているわけではありません。
    </span>
    <span className="block">
      そのうえで、
      <strong className="text-foreground">同じ回号</strong> の{" "}
      <code className="font-mono text-xs">method</code>{" "}
      ドキュメントの直近ラン候補（最大96件）に、その公式当選番号が含まれていたモデルを出しています。
    </span>
    <span className="block">
      <strong className="text-foreground">緑</strong>
      ＝ストレート一致、
      <strong className="text-foreground">黄</strong>
      ＝完全一致は無いがボックス相当の並び替えが候補にあったモデルです。
    </span>
  </>
);

export function Numbers4RecentModelHits({
  hits,
  title,
  description,
  bannerLead,
  emptyMessage,
  emphasizeOfficial,
}: Numbers4RecentModelHitsProps) {
  const withHits = hits.filter(
    (h) => h.exact_slugs.length > 0 || h.box_only_slugs.length > 0,
  );

  const resolvedTitle =
    title ??
    `直近 ${hits.length} 回 · 公式当選番号が各モデル候補に載っていたか`;

  return (
    <Card
      className={cn(
        "border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10",
        emphasizeOfficial &&
          "border-sky-600/20 bg-gradient-to-br from-sky-500/[0.06] to-transparent",
      )}
    >
      <CardHeader className="border-border/60 border-b">
        <div className="flex flex-wrap items-center gap-2">
          {emphasizeOfficial ? (
            <Badge
              variant="secondary"
              className="border-sky-500/30 bg-sky-500/15 font-normal text-sky-900 dark:text-sky-100"
            >
              公式当選ベース
            </Badge>
          ) : null}
          <CardTitle className="text-lg">{resolvedTitle}</CardTitle>
        </div>
        <CardDescription className="text-pretty space-y-1.5 text-sm leading-relaxed">
          {description ?? defaultDescription}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 pb-0 pt-0">
        {hits.length === 0 ? (
          <p className="text-muted-foreground px-4 py-8 text-center text-sm sm:px-6">
            {emptyMessage ??
              "照合対象の当選データがありません（DB 未接続か、まだ結果が入っていません）。"}
          </p>
        ) : (
          <>
            <div className="text-muted-foreground border-border/60 bg-muted/30 px-4 py-2 text-xs sm:px-6">
              {bannerLead != null ? <span className="block">{bannerLead}</span> : null}
              <span className="block">
                候補に無かった回は表では「0」とだけ表示されます（
                <code className="font-mono text-[0.65rem]">method</code>{" "}
                ファイルが無い回も同様）。
              </span>
              <span>
                いずれかの一致があった回:{" "}
                <span className="text-foreground font-medium tabular-nums">
                  {withHits.length}
                </span>
                {" / "}
                {hits.length} 回
              </span>
            </div>
            <div className="max-h-[min(70vh,36rem)] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-muted-foreground w-[5.5rem] px-3 text-xs sm:px-4">
                      回号
                    </TableHead>
                    <TableHead className="text-muted-foreground w-[4.5rem] px-3 text-xs sm:px-4">
                      当選
                    </TableHead>
                    <TableHead className="text-muted-foreground min-w-[8rem] px-3 text-xs sm:px-4">
                      ストレート一致
                    </TableHead>
                    <TableHead className="text-muted-foreground min-w-[8rem] px-3 text-xs sm:px-4">
                      ボックスのみ
                    </TableHead>
                    <TableHead className="text-muted-foreground w-[1%] px-3 text-right text-xs sm:px-4">
                      予測
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {hits.map((h) => (
                    <TableRow
                      key={h.draw_number}
                      className="border-border/60 align-top"
                    >
                      <TableCell className="px-3 py-2.5 text-sm tabular-nums sm:px-4">
                        第{h.draw_number}回
                      </TableCell>
                      <TableCell className="px-3 py-2.5 font-mono text-sm font-medium tabular-nums sm:px-4">
                        {h.numbers_normalized ?? "—"}
                      </TableCell>
                      <TableCell className="px-3 py-2.5 sm:px-4">
                        <SlugCell slugs={h.exact_slugs} variant="exact" />
                      </TableCell>
                      <TableCell className="px-3 py-2.5 sm:px-4">
                        <SlugCell slugs={h.box_only_slugs} variant="box" />
                      </TableCell>
                      <TableCell className="px-3 py-2.5 text-right sm:px-4">
                        <Link
                          href={`/numbers4/result/${h.draw_number}`}
                          className="text-primary text-xs font-medium hover:underline"
                        >
                          開く
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

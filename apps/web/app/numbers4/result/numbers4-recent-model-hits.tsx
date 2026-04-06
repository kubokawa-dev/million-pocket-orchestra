import Link from "next/link";

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

type Numbers4RecentModelHitsProps = {
  hits: Numbers4DrawWinningModelHit[];
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

export function Numbers4RecentModelHits({ hits }: Numbers4RecentModelHitsProps) {
  const withHits = hits.filter(
    (h) => h.exact_slugs.length > 0 || h.box_only_slugs.length > 0,
  );

  return (
    <Card className="border-border/80 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
      <CardHeader className="border-border/60 border-b">
        <CardTitle className="text-lg">
          直近 {hits.length} 回 · 当選番号が予測に載っていたモデル
        </CardTitle>
        <CardDescription className="text-pretty space-y-1 text-sm leading-relaxed">
          <span className="block">
            各回の{" "}
            <code className="font-mono text-xs">method</code>{" "}
            ドキュメントの直近ラン候補（最大96件）を当選番号と照合しています。
          </span>
          <span className="block">
            <strong className="text-foreground">緑</strong>
            ＝ストレート一致、
            <strong className="text-foreground">黄</strong>
            ＝完全一致は無いがボックス相当の並び替えが候補にあったモデルです。
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 pb-0 pt-0">
        <div className="text-muted-foreground border-border/60 bg-muted/30 px-4 py-2 text-xs sm:px-6">
          候補に無かった回は表では「0」とだけ表示されます（予測ファイルが無い回も同様）。
          いずれかの一致があった回:{" "}
          <span className="text-foreground font-medium tabular-nums">
            {withHits.length}
          </span>
          {" / "}
          {hits.length} 回
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
      </CardContent>
    </Card>
  );
}

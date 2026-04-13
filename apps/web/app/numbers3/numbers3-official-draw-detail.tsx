import Link from "next/link";
import { CalendarDaysIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import {
  NUMBERS3_DRAW_COLUMNS,
  type Numbers3DrawRow,
  formatNumbers3Cell,
} from "@/lib/numbers3";

type Props = {
  row: Numbers3DrawRow;
};

/** numbers3_draws の公式当選のみ（予測 JSON が無い回のフォールバック） */
export function Numbers3OfficialDrawDetail({ row }: Props) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="mx-auto w-full max-w-3xl flex-1 px-4 py-8 sm:max-w-4xl sm:px-6 sm:py-10">
        <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-stretch">
          <Card className="border-border/80 flex-1 shadow-sm ring-1 ring-black/5 dark:ring-white/10">
            <CardHeader className="pb-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="secondary">Numbers3</Badge>
                <span className="text-muted-foreground text-xs font-medium tabular-nums">
                  第 {row.draw_number} 回
                </span>
                <Badge variant="outline" className="text-[0.65rem]">
                  公式結果のみ
                </Badge>
              </div>
              <CardTitle className="font-heading pt-1 text-2xl sm:text-3xl">
                当選番号
              </CardTitle>
              <CardDescription className="flex items-center gap-1.5 text-sm">
                <CalendarDaysIcon className="size-3.5 opacity-70" />
                抽選日 {row.draw_date}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p
                className="font-mono text-5xl font-semibold tracking-[0.2em] sm:text-6xl sm:tracking-[0.25em]"
                translate="no"
              >
                {row.numbers}
              </p>
              <p className="text-muted-foreground mt-4 text-sm">
                この回の予測データ（ensemble / method / budget_plan）が見つかりませんでした。
                別回の予測は{" "}
                <Button
                  render={<Link href="/numbers3" />}
                  nativeButton={false}
                  variant="link"
                  className="h-auto p-0 text-sm"
                >
                  ナンバーズ3 トップ
                </Button>
                から開いてください。
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="border-border/80 overflow-hidden shadow-sm ring-1 ring-black/5 dark:ring-white/10">
          <CardHeader className="border-border/60 border-b pb-4">
            <CardTitle className="text-base sm:text-lg">全項目</CardTitle>
            <CardDescription>
              内部で保持している当選情報の各項目を、そのまま一覧表示しています。
            </CardDescription>
          </CardHeader>
          <CardContent className="px-0 pb-0 pt-0">
            <div className="w-full overflow-x-auto">
              <Table className="min-w-[min(100%,480px)]">
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-muted-foreground w-[38%] px-4 sm:w-[32%] sm:px-6">
                      項目
                    </TableHead>
                    <TableHead className="text-muted-foreground px-4 sm:px-6">
                      値
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {NUMBERS3_DRAW_COLUMNS.map((col) => (
                    <TableRow
                      key={col.key}
                      className="border-border/60 hover:bg-muted/30"
                    >
                      <TableCell className="text-muted-foreground px-4 py-3 text-sm font-medium sm:px-6">
                        {col.label}
                      </TableCell>
                      <TableCell
                        className={
                          col.key === "numbers"
                            ? "px-4 py-3 font-mono text-sm font-medium tracking-wide sm:px-6"
                            : "text-foreground px-4 py-3 text-sm tabular-nums sm:px-6"
                        }
                      >
                        {formatNumbers3Cell(col.key, row)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

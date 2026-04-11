import Link from "next/link";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  LOTO6_DRAW_COLUMNS,
  type Loto6DrawRow,
  formatLoto6Cell,
} from "@/lib/loto6";
import { cn } from "@/lib/utils";

type Loto6DrawsTableProps = {
  rows: Loto6DrawRow[];
};

export function Loto6DrawsTable({ rows }: Loto6DrawsTableProps) {
  return (
    <div>
      <Table className="min-w-[1280px]">
        <TableHeader className="bg-muted/80 supports-[backdrop-filter]:bg-muted/70 sticky top-0 z-10 backdrop-blur-sm [&_tr]:border-border/80">
          <TableRow className="hover:bg-transparent">
            {LOTO6_DRAW_COLUMNS.map((col) => (
              <TableHead
                key={col.key}
                className="text-muted-foreground h-11 px-3 text-xs font-semibold tracking-wide uppercase sm:px-4"
              >
                {col.label}
              </TableHead>
            ))}
            <TableHead className="text-muted-foreground h-11 w-[1%] px-3 text-right text-xs font-semibold tracking-wide uppercase sm:px-4">
              操作
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={LOTO6_DRAW_COLUMNS.length + 1}
                className="text-muted-foreground h-32 text-center text-sm"
              >
                データがありません
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row) => (
              <TableRow
                key={row.draw_number}
                className="hover:bg-muted/40 border-border/60"
              >
                {LOTO6_DRAW_COLUMNS.map((col) => (
                  <TableCell
                    key={col.key}
                    className={cn(
                      "text-foreground px-3 py-2.5 text-sm tabular-nums sm:px-4",
                      (col.key === "numbers" || col.key === "bonus_number") &&
                        "font-mono font-medium tracking-wide",
                    )}
                  >
                    {formatLoto6Cell(col.key, row)}
                  </TableCell>
                ))}
                <TableCell className="px-3 py-2.5 text-right sm:px-4">
                  <Link
                    href={`/loto6/result/${row.draw_number}`}
                    className={cn(
                      buttonVariants({ variant: "outline", size: "sm" }),
                      "inline-flex min-h-8 min-w-[4.25rem] justify-center",
                    )}
                  >
                    詳細
                  </Link>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <p className="text-muted-foreground px-4 py-2 text-center text-xs sm:hidden">
        ← 横にスワイプして全列を表示
      </p>
    </div>
  );
}

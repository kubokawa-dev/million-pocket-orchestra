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

/** `numbers3_draws` の全カラム一覧（PredictionsHub の公式フォールバックと併用） */
export function Numbers3OfficialDrawDetail({ row }: Props) {
  return (
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
  );
}

export const NUMBERS3_PAGE_SIZE = 25;

export type Numbers3DrawRow = {
  draw_number: number;
  draw_date: string;
  numbers: string;
};

export const NUMBERS3_DRAW_COLUMNS: {
  key: keyof Numbers3DrawRow;
  label: string;
}[] = [
  { key: "draw_number", label: "回号" },
  { key: "draw_date", label: "抽選日" },
  { key: "numbers", label: "当選番号" },
];

export function formatNumbers3Cell(
  key: keyof Numbers3DrawRow,
  row: Numbers3DrawRow,
): string {
  const v = row[key];
  if (v === null || v === undefined) return "—";
  return String(v);
}

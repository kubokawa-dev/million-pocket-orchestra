export const NUMBERS4_PAGE_SIZE = 25;

export type Numbers4DrawRow = {
  draw_number: number;
  draw_date: string;
  numbers: string;
  tier1_winners: number | null;
  tier1_payout_yen: number | string | null;
  tier2_winners: number | null;
  tier2_payout_yen: number | string | null;
  tier3_winners: number | null;
  tier3_payout_yen: number | string | null;
  tier4_winners: number | null;
  tier4_payout_yen: number | string | null;
};

export const NUMBERS4_DRAW_COLUMNS: {
  key: keyof Numbers4DrawRow;
  label: string;
}[] = [
  { key: "draw_number", label: "回号" },
  { key: "draw_date", label: "抽選日" },
  { key: "numbers", label: "当選番号" },
  { key: "tier1_winners", label: "1等 当選口数" },
  { key: "tier1_payout_yen", label: "1等 払戻金（円）" },
  { key: "tier2_winners", label: "2等 当選口数" },
  { key: "tier2_payout_yen", label: "2等 払戻金（円）" },
  { key: "tier3_winners", label: "3等 当選口数" },
  { key: "tier3_payout_yen", label: "3等 払戻金（円）" },
  { key: "tier4_winners", label: "4等 当選口数" },
  { key: "tier4_payout_yen", label: "4等 払戻金（円）" },
];

export function formatYen(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const n = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("ja-JP");
}

export function formatCell(
  key: keyof Numbers4DrawRow,
  row: Numbers4DrawRow,
): string {
  const v = row[key];
  if (v === null || v === undefined) return "—";
  if (key.endsWith("_payout_yen")) return formatYen(v as number | string);
  return String(v);
}

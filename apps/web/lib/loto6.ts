import { formatYen } from "@/lib/numbers4";

export const LOTO6_PAGE_SIZE = 25;

/** `loto6_draws` 行（Supabase） */
export type Loto6DrawRow = {
  draw_number: number;
  draw_date: string;
  numbers: string;
  bonus_number: number;
  tier1_winners: number | null;
  tier1_payout_yen: number | string | null;
  tier2_winners: number | null;
  tier2_payout_yen: number | string | null;
  tier3_winners: number | null;
  tier3_payout_yen: number | string | null;
  tier4_winners: number | null;
  tier4_payout_yen: number | string | null;
  tier5_winners: number | null;
  tier5_payout_yen: number | string | null;
  carryover_yen: number | string | null;
};

export const LOTO6_DRAW_COLUMNS: {
  key: keyof Loto6DrawRow;
  label: string;
}[] = [
  { key: "draw_number", label: "回号" },
  { key: "draw_date", label: "抽選日" },
  { key: "numbers", label: "本数字" },
  { key: "bonus_number", label: "ボーナス" },
  { key: "tier1_winners", label: "1等 口数" },
  { key: "tier1_payout_yen", label: "1等 払戻（円）" },
  { key: "tier2_winners", label: "2等 口数" },
  { key: "tier2_payout_yen", label: "2等 払戻（円）" },
  { key: "tier3_winners", label: "3等 口数" },
  { key: "tier3_payout_yen", label: "3等 払戻（円）" },
  { key: "tier4_winners", label: "4等 口数" },
  { key: "tier4_payout_yen", label: "4等 払戻（円）" },
  { key: "tier5_winners", label: "5等 口数" },
  { key: "tier5_payout_yen", label: "5等 払戻（円）" },
  { key: "carryover_yen", label: "キャリーオーバー（円）" },
];

export function formatLoto6NumbersCell(numbers: string): string {
  const parts = numbers.split(",").map((s) => s.trim()).filter(Boolean);
  if (parts.length === 0) return "—";
  return parts.join(" · ");
}

export function formatLoto6Cell(
  key: keyof Loto6DrawRow,
  row: Loto6DrawRow,
): string {
  if (key === "numbers") {
    return formatLoto6NumbersCell(row.numbers);
  }
  const v = row[key];
  if (v === null || v === undefined) return "—";
  if (
    key.endsWith("_payout_yen") ||
    key === "carryover_yen"
  ) {
    return formatYen(v as number | string);
  }
  return String(v);
}

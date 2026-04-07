import { createClient } from "@/lib/supabase/server";
import { numbers4DrawDateToIsoDate } from "@/lib/numbers4-draw-page-seo";

export async function fetchAdjacentDrawNumbers(
  drawNumber: number,
): Promise<{ prev: number | null; next: number | null }> {
  if (!Number.isFinite(drawNumber) || drawNumber < 1) {
    return { prev: null, next: null };
  }
  try {
    const supabase = await createClient();
    const [older, newer] = await Promise.all([
      supabase
        .from("numbers4_draws")
        .select("draw_number")
        .lt("draw_number", drawNumber)
        .order("draw_number", { ascending: false })
        .limit(1)
        .maybeSingle(),
      supabase
        .from("numbers4_draws")
        .select("draw_number")
        .gt("draw_number", drawNumber)
        .order("draw_number", { ascending: true })
        .limit(1)
        .maybeSingle(),
    ]);
    return {
      prev:
        older.data?.draw_number != null
          ? Number(older.data.draw_number)
          : null,
      next:
        newer.data?.draw_number != null
          ? Number(newer.data.draw_number)
          : null,
    };
  } catch {
    return { prev: null, next: null };
  }
}

/**
 * 同一カレンダー月の回号一覧（自分自身は除外）。draw_date がパース不能なら []。
 */
export async function fetchSameMonthDrawNumbers(
  drawDateRaw: string | null | undefined,
  excludeDrawNumber: number,
): Promise<number[]> {
  const iso = numbers4DrawDateToIsoDate(drawDateRaw);
  if (!iso || iso.length < 7) return [];
  const ym = iso.slice(0, 7);
  const [yStr, mStr] = ym.split("-");
  const y = parseInt(yStr, 10);
  const m = parseInt(mStr, 10);
  if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) {
    return [];
  }
  const nextMonth = m === 12 ? `${y + 1}-01` : `${y}-${String(m + 1).padStart(2, "0")}`;
  const monthStart = `${ym}-01`;
  const monthEndExclusive = `${nextMonth}-01`;

  try {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from("numbers4_draws")
      .select("draw_number")
      .gte("draw_date", monthStart)
      .lt("draw_date", monthEndExclusive)
      .order("draw_number", { ascending: true });
    if (error || !data?.length) return [];
    return data
      .map((r) => Number(r.draw_number))
      .filter(
        (n) =>
          Number.isFinite(n) && n > 0 && n !== excludeDrawNumber,
      );
  } catch {
    return [];
  }
}

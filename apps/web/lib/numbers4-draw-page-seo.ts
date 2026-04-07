import type { Numbers4DrawRow } from "@/lib/numbers4";

/** Open Graph の publishedTime 用（YYYY-MM-DD 優先） */
export function numbers4DrawDateToIsoDate(drawDate: string | null | undefined): string | undefined {
  if (drawDate == null || String(drawDate).trim() === "") return undefined;
  const t = String(drawDate).trim();
  if (/^\d{4}-\d{2}-\d{2}/.test(t)) return t.slice(0, 10);
  const d = new Date(t);
  if (!Number.isNaN(d.getTime())) return d.toISOString().slice(0, 10);
  return undefined;
}

export function buildNumbers4DrawPageDescription(
  drawNumber: number,
  row: Numbers4DrawRow | null,
): string {
  const datePart = row?.draw_date?.trim()
    ? `抽選日 ${row.draw_date.trim()}。`
    : "";
  const nums = row?.numbers != null ? String(row.numbers).trim() : "";
  const winningPart =
    nums !== ""
      ? `当選番号 ${nums}。`
      : "当選番号は公式結果の取り込み後に表示されます。";

  return `ナンバーズ4 第${drawNumber}回の${datePart}${winningPart}アンサンブル・手法別・予算プランの日次予測と照合を宝くじAIで一覧できます。`;
}

/** メタ description 用の英語サフィックス（検索・SNS 向け） */
export function numbers4DrawEnglishMetaSuffix(drawNumber: number): string {
  return ` EN: Unofficial Japan Numbers4 draw #${drawNumber} — results & model predictions; always verify on official lottery sites.`;
}

import type { Numbers3DrawRow } from "@/lib/numbers3";

/** Open Graph の publishedTime 用（YYYY-MM-DD 優先） */
export function numbers3DrawDateToIsoDate(
  drawDate: string | null | undefined,
): string | undefined {
  if (drawDate == null || String(drawDate).trim() === "") return undefined;
  const t = String(drawDate).trim();
  if (/^\d{4}-\d{2}-\d{2}/.test(t)) return t.slice(0, 10);
  const d = new Date(t);
  if (!Number.isNaN(d.getTime())) return d.toISOString().slice(0, 10);
  return undefined;
}

export function buildNumbers3DrawPageDescription(
  drawNumber: number,
  row: Numbers3DrawRow | null,
): string {
  const datePart = row?.draw_date?.trim()
    ? `抽選日 ${row.draw_date.trim()}。`
    : "";
  const nums = row?.numbers != null ? String(row.numbers).trim() : "";
  const winningPart =
    nums !== ""
      ? `当選番号 ${nums}。`
      : "当選番号は公式結果の取り込み後に表示されます。";

  return `ナンバーズ3 第${drawNumber}回の${datePart}${winningPart}アンサンブル・手法別・予算プランの日次モデル試算と照合を宝くじAIで一覧できます（当せんの保証はありません）。`;
}

export function numbers3DrawEnglishMetaSuffix(drawNumber: number): string {
  return ` EN: Unofficial Japan Numbers3 draw #${drawNumber} — results & reference model outputs (not win predictions); verify on official lottery sites.`;
}

/** 当選番号との照合（ナンバーズ4・4桁） */

export type HitKind = "none" | "straight" | "box";

export function normalizeNumbers4(num: string | null | undefined): string | null {
  if (num == null) return null;
  const d = String(num).replace(/\D/g, "");
  if (d.length < 1 || d.length > 4) return null;
  return d.padStart(4, "0");
}

export function digitsSortedKey(num: string | null | undefined): string | null {
  const n = normalizeNumbers4(num);
  if (!n) return null;
  return [...n].sort().join("");
}

/** ストレート一致 or 桁の multiset 一致（ボックス相当の簡易判定） */
export function classifyHit(
  prediction: string | null | undefined,
  winning: string | null | undefined,
): HitKind {
  const p = normalizeNumbers4(prediction);
  const w = normalizeNumbers4(winning);
  if (!p || !w) return "none";
  if (p === w) return "straight";
  if (digitsSortedKey(p) === digitsSortedKey(w)) return "box";
  return "none";
}

export function hitLabel(kind: HitKind): string {
  if (kind === "straight") return "ストレート一致";
  if (kind === "box") return "ボックス相当";
  return "";
}

/**
 * 当選番号の各数字の出現回数（マルチセット）。
 * 予測側の強調は「左から見て、当選に残りがあるときだけ」使う。
 */
export function createWinningDigitPool(
  winning: string | null | undefined,
): Map<string, number> | null {
  const w = normalizeNumbers4(winning);
  if (!w) return null;
  const m = new Map<string, number>();
  for (const ch of w) {
    if (ch >= "0" && ch <= "9") {
      m.set(ch, (m.get(ch) ?? 0) + 1);
    }
  }
  return m;
}

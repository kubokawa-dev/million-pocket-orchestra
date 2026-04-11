/** 本数字（6球）の一致数。ボーナスは別判定 */

export function parseLoto6MainNumbers(numbers: string | null | undefined): number[] {
  if (!numbers) return [];
  return numbers
    .split(",")
    .map((s) => parseInt(s.trim(), 10))
    .filter((n) => Number.isFinite(n) && n >= 1 && n <= 43);
}

export function countLoto6MainHits(predMain: number[], actualMain: number[]): number {
  const a = new Set(actualMain);
  return predMain.filter((x) => a.has(x)).length;
}

export function isLoto6BonusHit(
  predBonus: number | null | undefined,
  actualBonus: number | null | undefined,
): boolean {
  if (predBonus == null || actualBonus == null) return false;
  return predBonus === actualBonus;
}

import { getEnsembleWeightJaLabel } from "../numbers4-predictions/ensemble-weight-labels";
import { digitsSortedKey, normalizeNumbers3 } from "./prediction-hit-utils";
import type { MethodPredictionRow } from "../numbers4-predictions/types";

export type EnsembleContributorBreakdown = {
  exactSlugs: string[];
  boxOnlySlugs: string[];
};

export function contributorsForEnsembleNumber(
  numberRaw: string | undefined | null,
  methodRows: MethodPredictionRow[],
): EnsembleContributorBreakdown {
  const n = normalizeNumbers3(numberRaw ?? "");
  if (!n) {
    return { exactSlugs: [], boxOnlySlugs: [] };
  }
  const boxKey = digitsSortedKey(n);
  if (!boxKey) {
    return { exactSlugs: [], boxOnlySlugs: [] };
  }

  const exactSlugs: string[] = [];
  const boxOnlySlugs: string[] = [];

  for (const m of methodRows) {
    let exact = false;
    let box = false;
    for (const p of m.topPredictions) {
      if (p.number === n) {
        exact = true;
        break;
      }
      if (digitsSortedKey(p.number) === boxKey) {
        box = true;
      }
    }
    if (exact) exactSlugs.push(m.slug);
    else if (box) boxOnlySlugs.push(m.slug);
  }

  return { exactSlugs, boxOnlySlugs };
}

export function formatContributorSlugLine(slug: string): string {
  const ja = getEnsembleWeightJaLabel(slug);
  return ja != null && ja !== "" ? `${slug}（${ja}）` : slug;
}

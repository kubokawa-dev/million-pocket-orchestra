import {
  buildNumbers3ModelReportCards,
  buildNumbers4ModelReportCards,
  type ModelReportCard,
} from "@/lib/model-report-cards";

export type ModelGovernanceSummary = {
  sampleSize: number;
  preferred: { slug: string; label: string }[];
  watchlist: { slug: string; label: string }[];
  deprioritized: { slug: string; label: string }[];
};

function classifyNumbers4Card(card: ModelReportCard): "preferred" | "watch" | "deprioritized" {
  const hitRate = card.hitRatePct;
  const top10 = card.top10Pct ?? 0;

  if (top10 >= 18 || hitRate >= 35) return "preferred";
  if (top10 <= 6 && hitRate <= 18) return "deprioritized";
  return "watch";
}

function classifyNumbers3Card(card: ModelReportCard): "preferred" | "watch" | "deprioritized" {
  const hitRate = card.hitRatePct;
  const exactHits = card.exactHits ?? 0;
  const boxHits = card.boxHits ?? 0;

  if (hitRate >= 25 || exactHits >= 2) return "preferred";
  if (hitRate <= 10 && exactHits === 0 && boxHits <= 1) return "deprioritized";
  return "watch";
}

function summarize(
  cards: ModelReportCard[],
  classifier: (card: ModelReportCard) => "preferred" | "watch" | "deprioritized",
): ModelGovernanceSummary {
  const preferred: { slug: string; label: string }[] = [];
  const watchlist: { slug: string; label: string }[] = [];
  const deprioritized: { slug: string; label: string }[] = [];

  for (const card of cards) {
    const bucket = classifier(card);
    const entry = { slug: card.slug, label: card.label };
    if (bucket === "preferred") preferred.push(entry);
    else if (bucket === "watch") watchlist.push(entry);
    else deprioritized.push(entry);
  }

  return {
    sampleSize: cards[0]?.sampleSize ?? 0,
    preferred,
    watchlist,
    deprioritized,
  };
}

export async function buildNumbers4ModelGovernance(
  lastN = 30,
): Promise<ModelGovernanceSummary> {
  const cards = await buildNumbers4ModelReportCards(lastN, { limit: 14 });
  return summarize(cards, classifyNumbers4Card);
}

export async function buildNumbers3ModelGovernance(
  lastN = 20,
): Promise<ModelGovernanceSummary> {
  const cards = await buildNumbers3ModelReportCards(lastN, { limit: 14 });
  return summarize(cards, classifyNumbers3Card);
}

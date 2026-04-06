import { loadNumbers4PredictionBundleForDraw, resolveTargetDrawNumber } from "./apps/web/lib/numbers4-predictions/load-6949";

async function main() {
  const latestDraw = await resolveTargetDrawNumber();
  console.log("Latest draw:", latestDraw);
  const bundle = await loadNumbers4PredictionBundleForDraw(latestDraw);
  if (!bundle || !bundle.ensemble || !bundle.ensemble.predictions) {
    console.log("No bundle or predictions");
    return;
  }
  const preds = bundle.ensemble.predictions;
  const lastRun = preds[preds.length - 1];
  console.log("Hot models:", lastRun.hot_models);
}

main().catch(console.error);

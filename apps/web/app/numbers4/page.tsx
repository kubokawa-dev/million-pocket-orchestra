import type { Metadata } from "next";

import { Numbers4PredictionsHub } from "./numbers4-predictions-hub";

export const metadata: Metadata = {
  title: "ナンバーズ4 予測",
  description:
    "ナンバーズ4の日次予測（アンサンブル・予算プラン・各メソッド）を確認できます。",
};

export default function Numbers4Page() {
  return <Numbers4PredictionsHub />;
}

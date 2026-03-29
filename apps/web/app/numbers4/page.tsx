import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { resolveTargetDrawNumber } from "@/lib/numbers4-predictions/load-6949";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ナンバーズ4 予測",
  description:
    "ナンバーズ4の日次予測（アンサンブル・予算プラン・各メソッド）を確認できます。",
};

/** 最新回の `/numbers4/result/[回]` へ誘導（予測 UI は result 配下に集約） */
export default async function Numbers4Page() {
  const n = await resolveTargetDrawNumber();
  redirect(`/numbers4/result/${n}`);
}

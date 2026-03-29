import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Numbers4PredictionsHub } from "../../numbers4-predictions-hub";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { draw_number: raw } = await params;
  const n = parseInt(raw, 10);
  if (!Number.isFinite(n)) {
    return { title: "ナンバーズ4" };
  }
  return {
    title: `第${n}回 予測`,
    description: `ナンバーズ4 第${n}回の日次予測（アンサンブル・予算プラン・各手法）`,
  };
}

export default async function Numbers4ResultDrawPredictionsPage({
  params,
}: PageProps) {
  const { draw_number: raw } = await params;
  const drawNumber = parseInt(raw, 10);
  if (!Number.isFinite(drawNumber)) {
    notFound();
  }

  return (
    <Numbers4PredictionsHub
      targetDrawNumber={drawNumber}
      showBackToResultList
    />
  );
}

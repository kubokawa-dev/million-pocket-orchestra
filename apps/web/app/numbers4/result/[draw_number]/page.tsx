import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Numbers4PredictionsHub } from "../../numbers4-predictions-hub";
import {
  buildNumbers4DrawPageDescription,
  numbers4DrawDateToIsoDate,
} from "@/lib/numbers4-draw-page-seo";
import { getCachedNumbers4DrawFullRow } from "@/lib/numbers4-predictions/load-6949";
import { getSiteOrigin } from "@/lib/site";

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

  const row = await getCachedNumbers4DrawFullRow(n);
  const description = buildNumbers4DrawPageDescription(n, row);
  const title = `第${n}回 ナンバーズ4 予測・当選照合`;
  const ogDate = numbers4DrawDateToIsoDate(row?.draw_date);

  return {
    title,
    description,
    keywords: [
      "ナンバーズ4",
      `第${n}回`,
      "予測",
      "当選番号",
      "アンサンブル",
      "ボックス",
      "たからくじAI",
      "Million Pocket",
    ],
    alternates: { canonical: `/numbers4/result/${n}` },
    openGraph: {
      title: `${title} | Million Pocket`,
      description,
      url: `/numbers4/result/${n}`,
      type: "article",
      ...(ogDate ? { publishedTime: ogDate } : {}),
    },
    twitter: {
      card: "summary",
      title: `${title} | Million Pocket`,
      description,
    },
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

  const row = await getCachedNumbers4DrawFullRow(drawNumber);
  const origin = getSiteOrigin();
  const description = buildNumbers4DrawPageDescription(drawNumber, row);
  const pageName = `第${drawNumber}回 ナンバーズ4 予測・当選照合`;
  const pageUrl = `${origin}/numbers4/result/${drawNumber}`;
  const ogDate = numbers4DrawDateToIsoDate(row?.draw_date);

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "BreadcrumbList",
        "@id": `${pageUrl}#breadcrumb`,
        itemListElement: [
          {
            "@type": "ListItem",
            position: 1,
            name: "ホーム",
            item: origin,
          },
          {
            "@type": "ListItem",
            position: 2,
            name: "ナンバーズ4",
            item: `${origin}/numbers4`,
          },
          {
            "@type": "ListItem",
            position: 3,
            name: "当選番号一覧",
            item: `${origin}/numbers4/result`,
          },
          {
            "@type": "ListItem",
            position: 4,
            name: `第${drawNumber}回`,
            item: pageUrl,
          },
        ],
      },
      {
        "@type": "WebPage",
        "@id": `${pageUrl}#webpage`,
        url: pageUrl,
        name: pageName,
        description,
        isPartOf: { "@id": `${origin}/#website` },
        inLanguage: "ja",
        ...(ogDate ? { dateModified: ogDate } : {}),
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Numbers4PredictionsHub
        targetDrawNumber={drawNumber}
        showBackToResultList
      />
    </>
  );
}

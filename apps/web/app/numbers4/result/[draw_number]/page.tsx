import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Numbers4DrawPageChrome } from "@/components/numbers4-draw-page-chrome";
import { Numbers4PredictionsHub } from "../../numbers4-predictions-hub";
import {
  buildNumbers4DrawPageDescription,
  numbers4DrawDateToIsoDate,
  numbers4DrawEnglishMetaSuffix,
} from "@/lib/numbers4-draw-page-seo";
import {
  fetchAdjacentDrawNumbers,
  fetchSameMonthDrawNumbers,
} from "@/lib/numbers4-draw-neighbors";
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
  const description =
    buildNumbers4DrawPageDescription(n, row) + numbers4DrawEnglishMetaSuffix(n);
  const title = `第${n}回 ナンバーズ4 モデル試算と当選照合`;
  const ogDate = numbers4DrawDateToIsoDate(row?.draw_date);

  return {
    title,
    description,
    keywords: [
      "ナンバーズ4",
      `第${n}回`,
      "モデル試算",
      "当選番号",
      "アンサンブル",
      "ボックス",
      "宝くじAI",
    ],
    alternates: { canonical: `/numbers4/result/${n}` },
    openGraph: {
      title: `${title} | 宝くじAI`,
      description,
      url: `/numbers4/result/${n}`,
      type: "article",
      ...(ogDate ? { publishedTime: ogDate } : {}),
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} | 宝くじAI`,
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
  const [adjacent, sameMonthDraws] = await Promise.all([
    fetchAdjacentDrawNumbers(drawNumber),
    fetchSameMonthDrawNumbers(row?.draw_date, drawNumber),
  ]);
  const origin = getSiteOrigin();
  const description = buildNumbers4DrawPageDescription(drawNumber, row);
  const pageName = `第${drawNumber}回 ナンバーズ4 モデル試算と当選照合`;
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
      <Numbers4DrawPageChrome
        drawNumber={drawNumber}
        row={row}
        prevDraw={adjacent.prev}
        nextDraw={adjacent.next}
        sameMonthDraws={sameMonthDraws}
      />
      <Numbers4PredictionsHub
        targetDrawNumber={drawNumber}
        showBackToResultList
      />
    </>
  );
}

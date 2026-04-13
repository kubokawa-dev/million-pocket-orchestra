import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Numbers3DrawPageChrome } from "@/components/numbers3-draw-page-chrome";
import {
  buildNumbers3DrawPageDescription,
  numbers3DrawDateToIsoDate,
  numbers3DrawEnglishMetaSuffix,
} from "@/lib/numbers3-draw-page-seo";
import {
  fetchNumbers3AdjacentDrawNumbers,
  fetchNumbers3SameMonthDrawNumbers,
} from "@/lib/numbers3-draw-neighbors";
import { getCachedNumbers3DrawFullRow } from "@/lib/numbers3-predictions/load-numbers3";
import { getSiteOrigin } from "@/lib/site";

import { Numbers3PredictionsHub } from "../../numbers3-predictions-hub";

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
    return { title: "ナンバーズ3" };
  }

  const row = await getCachedNumbers3DrawFullRow(n);
  const description =
    buildNumbers3DrawPageDescription(n, row) + numbers3DrawEnglishMetaSuffix(n);
  const title = `第${n}回 ナンバーズ3 モデル試算と当選照合`;
  const ogDate = numbers3DrawDateToIsoDate(row?.draw_date);

  return {
    title,
    description,
    keywords: [
      "ナンバーズ3",
      `第${n}回`,
      "モデル試算",
      "当選番号",
      "アンサンブル",
      "ボックス",
      "宝くじAI",
    ],
    alternates: { canonical: `/numbers3/result/${n}` },
    openGraph: {
      title: `${title} | 宝くじAI`,
      description,
      url: `/numbers3/result/${n}`,
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

export default async function Numbers3ResultDrawPredictionsPage({
  params,
}: PageProps) {
  const { draw_number: raw } = await params;
  const drawNumber = parseInt(raw, 10);
  if (!Number.isFinite(drawNumber)) {
    notFound();
  }

  const row = await getCachedNumbers3DrawFullRow(drawNumber);
  const [adjacent, sameMonthDraws] = await Promise.all([
    fetchNumbers3AdjacentDrawNumbers(drawNumber),
    fetchNumbers3SameMonthDrawNumbers(row?.draw_date, drawNumber),
  ]);
  const origin = getSiteOrigin();
  const description = buildNumbers3DrawPageDescription(drawNumber, row);
  const pageName = `第${drawNumber}回 ナンバーズ3 モデル試算と当選照合`;
  const pageUrl = `${origin}/numbers3/result/${drawNumber}`;
  const ogDate = numbers3DrawDateToIsoDate(row?.draw_date);

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
            name: "ナンバーズ3",
            item: `${origin}/numbers3`,
          },
          {
            "@type": "ListItem",
            position: 3,
            name: "当選番号一覧",
            item: `${origin}/numbers3/result`,
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
      <Numbers3DrawPageChrome
        drawNumber={drawNumber}
        row={row}
        prevDraw={adjacent.prev}
        nextDraw={adjacent.next}
        sameMonthDraws={sameMonthDraws}
      />
      <Numbers3PredictionsHub
        targetDrawNumber={drawNumber}
        showBackToResultList
      />
    </>
  );
}

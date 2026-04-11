import type { Metadata } from "next";

import { HomeLanding } from "@/components/home-landing";
import { absoluteUrl, getSiteOrigin } from "@/lib/site";

export const metadata: Metadata = {
  alternates: {
    canonical: "/",
    languages: {
      ja: absoluteUrl("/"),
      en: absoluteUrl("/en"),
      zh: absoluteUrl("/zh"),
      ko: absoluteUrl("/ko"),
      es: absoluteUrl("/es"),
      hi: absoluteUrl("/hi"),
      ar: absoluteUrl("/ar"),
    },
  },
  openGraph: {
    url: getSiteOrigin(),
    title: "宝くじAI | ナンバーズ3・4・ロト6の本気ダッシュボード",
    description:
      "ナンバーズ3・ロト6の当選一覧（等級・払戻つき）と、ナンバーズ4のマルチモデル試算・統計・トレンドまで。当せんの保証はなく、参加の情報整理を支援する非公式ダッシュボードです。",
  },
};

const homeJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${getSiteOrigin()}/#website`,
      url: getSiteOrigin(),
      name: "宝くじAI",
      alternateName: [
        "Takarakuji AI",
        "takarakuji-ai.space",
        "تاكاراكوجي AI",
        "Japan Numbers3, Numbers4 & Loto6 lottery dashboard",
        "لوحة يانصيب أرقام اليابان",
      ],
      description:
        "ナンバーズ3・4・ロト6の当選番号・抽選結果の閲覧と、複数モデルによる日次試算出力・統計・トレンド可視化をまとめたWebアプリ（当せん保証・購入推奨はしません）。 English: Unofficial Japan Numbers3/4/Loto6 results and reference analytics; see /en and /ar for overviews.",
      inLanguage: "ja",
      publisher: { "@id": `${getSiteOrigin()}/#organization` },
    },
    {
      "@type": "Organization",
      "@id": `${getSiteOrigin()}/#organization`,
      name: "宝くじAI",
      url: getSiteOrigin(),
      sameAs: [] as string[],
    },
  ],
};

export default function Home() {
  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(homeJsonLd),
        }}
      />
      <HomeLanding />
    </div>
  );
}

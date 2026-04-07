import type { Metadata } from "next";

import { HomeLanding } from "@/components/home-landing";
import { getSiteOrigin } from "@/lib/site";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
  openGraph: {
    url: getSiteOrigin(),
    title: "Million Pocket（たからくじAI）| ナンバーズ4の本気ダッシュボード",
    description:
      "当選番号一覧からマルチモデル予測、統計・トレンドまで。Numbers4好きのためのWebアプリ。スマホ最適化UIで数字遊びを加速。",
  },
};

const homeJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${getSiteOrigin()}/#website`,
      url: getSiteOrigin(),
      name: "Million Pocket",
      alternateName: ["たからくじAI", "Takarakuji AI", "takarakuji-ai.space"],
      description:
        "ナンバーズ4の当選番号・抽選結果の閲覧と、複数モデルによる日次予測・統計・トレンド可視化をまとめたWebアプリ。",
      inLanguage: "ja",
      publisher: { "@id": `${getSiteOrigin()}/#organization` },
    },
    {
      "@type": "Organization",
      "@id": `${getSiteOrigin()}/#organization`,
      name: "Million Pocket",
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

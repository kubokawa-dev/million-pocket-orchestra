import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_JP } from "next/font/google";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { Analytics } from "@vercel/analytics/next";

import { AgeAcknowledgmentBar } from "@/components/age-acknowledgment-bar";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { buildSiteVerification } from "@/lib/site-verification";
import { getSiteOrigin } from "@/lib/site";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const notoSansJP = Noto_Sans_JP({
  variable: "--font-noto-sans-jp",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const siteOrigin = getSiteOrigin();
const siteVerification = buildSiteVerification();

export const metadata: Metadata = {
  metadataBase: new URL(siteOrigin),
  title: {
    default: "宝くじAI | ナンバーズ3・4 抽選結果と参加支援（モデル試算）",
    template: "%s · 宝くじAI",
  },
  description:
    "ナンバーズ3・4の当選番号・抽選結果の閲覧に加え、ナンバーズ4では複数モデルの日次「試算」出力や統計を一覧できます。当せんの保証や購入の推奨は行いません（参加の情報整理・戦略検討の補助）。（takarakuji-ai.space） English: Unofficial Japan Numbers3/4 dashboard — results and reference model outputs; not affiliated with any operator.",
  applicationName: "宝くじAI",
  keywords: [
    "ナンバーズ3",
    "ナンバーズ３",
    "ナンバーズ4",
    "ナンバーズ４",
    "宝くじ",
    "抽選結果",
    "当選番号",
    "予測",
    "モデル試算",
    "参加戦略",
    "宝くじAI",
    "ブログ",
    "FAQ",
    "Numbers3",
    "Numbers4",
    "Numbers 4",
    "Japan lottery",
    "Japanese lottery",
    "Takarakuji",
    "lottery results",
    "winning numbers",
    "lottery statistics",
    "machine learning",
    "lottery analytics",
    "digit lottery",
    "اليانصيب الياباني",
    "نمبرز 4",
  ],
  authors: [{ name: "宝くじAI" }],
  creator: "宝くじAI",
  openGraph: {
    type: "website",
    locale: "ja_JP",
    alternateLocale: ["en_US", "zh_CN", "ko_KR", "es_ES", "hi_IN", "ar_SA"],
    url: siteOrigin,
    siteName: "宝くじAI",
    title: "宝くじAI | ナンバーズ3・4 抽選結果と参加支援（モデル試算）",
    description:
      "ナンバーズ3の当選一覧（等級つき）と、ナンバーズ4の当選番号・日次モデル試算・統計をスマホでも見やすく。当せんを約束するサービスではありません。",
  },
  twitter: {
    card: "summary_large_image",
    title: "宝くじAI",
    description:
      "ナンバーズ3・4の抽選結果と、モデル試算・統計のダッシュボード。当せんの保証はありません。",
  },
  alternates: {
    types: {
      "application/rss+xml": "/feed.xml",
    },
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  ...(siteVerification ? { verification: siteVerification } : {}),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ja"
      className={`${geistSans.variable} ${geistMono.variable} ${notoSansJP.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <NuqsAdapter>
          <div className="app-surface app-dot-grid flex min-h-full flex-1 flex-col">
            <SiteHeader />
            <main className="flex flex-1 flex-col">{children}</main>
            <SiteFooter />
            <AgeAcknowledgmentBar />
          </div>
        </NuqsAdapter>
        <Analytics />
      </body>
    </html>
  );
}

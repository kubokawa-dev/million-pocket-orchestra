import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_JP } from "next/font/google";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { Analytics } from "@vercel/analytics/next";

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
    default: "宝くじAI | ナンバーズ4 抽選結果・予測",
    template: "%s · 宝くじAI",
  },
  description:
    "ナンバーズ4の当選番号・抽選結果を一覧でチェック。複数のAI・統計モデルによる日次予測やボックス順位の統計もまとめて閲覧できます。（takarakuji-ai.space）",
  applicationName: "宝くじAI",
  keywords: [
    "ナンバーズ4",
    "宝くじ",
    "抽選結果",
    "当選番号",
    "予測",
    "宝くじAI",
    "ブログ",
    "FAQ",
  ],
  authors: [{ name: "宝くじAI" }],
  creator: "宝くじAI",
  openGraph: {
    type: "website",
    locale: "ja_JP",
    alternateLocale: ["en_US", "zh_CN", "ko_KR", "es_ES", "hi_IN", "ar_SA"],
    url: siteOrigin,
    siteName: "宝くじAI",
    title: "宝くじAI | ナンバーズ4 抽選結果・予測",
    description:
      "ナンバーズ4の当選番号一覧と、複数モデルによる日次予測・統計をスマホでも見やすく。",
  },
  twitter: {
    card: "summary_large_image",
    title: "宝くじAI",
    description:
      "ナンバーズ4の抽選結果と予測ダッシュボード。当選番号をすっきり一覧で。",
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
          </div>
        </NuqsAdapter>
        <Analytics />
      </body>
    </html>
  );
}

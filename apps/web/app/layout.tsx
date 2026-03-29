import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_JP } from "next/font/google";
import { NuqsAdapter } from "nuqs/adapters/next/app";

import { SiteHeader } from "@/components/site-header";

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

export const metadata: Metadata = {
  title: {
    default: "Million Pocket",
    template: "%s · Million Pocket",
  },
  description: "ナンバーズ4の当選番号・抽選結果を一覧・詳細で確認できます。",
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
          </div>
        </NuqsAdapter>
      </body>
    </html>
  );
}

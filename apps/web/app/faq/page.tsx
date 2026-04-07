import type { Metadata } from "next";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { faqItems } from "@/lib/faq-content";

export const metadata: Metadata = {
  title: "よくある質問（FAQ）",
  description:
    "Million Pocket（たからくじAI）の使い方、データの出所、予測の位置づけなどよくある質問と回答。",
  alternates: { canonical: "/faq" },
  openGraph: {
    title: "よくある質問 | Million Pocket（たからくじAI）",
    description:
      "ナンバーズ4・当選番号・予測についてのFAQ。構造化データ（FAQPage）対応。",
    url: "/faq",
  },
};

export default function FaqPage() {
  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqItems.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            よくある質問
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            Million Pocket（たからくじAI）について、よくいただく内容をまとめました。
          </p>
        </header>

        <div className="space-y-4">
          {faqItems.map((item) => (
            <Card key={item.question} className="border-border/80 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-base leading-snug sm:text-lg">
                  {item.question}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground/90 text-sm leading-relaxed">
                  {item.answer}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

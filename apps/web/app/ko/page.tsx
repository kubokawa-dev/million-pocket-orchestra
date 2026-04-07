import type { Metadata } from "next";
import Link from "next/link";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const koFaq = [
  {
    question: "Takarakuji AI란 무엇인가요?",
    answer:
      "일본의 Numbers4 복권에 초점을 맞춘 비공식 웹 앱입니다. 공식 추첨 결과를 열람하고, 통계와 트렌드를 탐색하며, 여러 일일 예측 모델을 비교할 수 있습니다. 인터페이스는 주로 일본어이며, 이 페이지는 해외 방문자를 위한 한국어 개요입니다.",
  },
  {
    question: "이 사이트는 공식이거나 복권에 소속되어 있나요?",
    answer:
      "아닙니다. 미즈호 은행, 일본 복권 또는 어떤 운영자와도 관련이 없습니다. 정보에 의존하기 전에 항상 공식 출처에서 결과를 확인하세요.",
  },
  {
    question: "예측이 당첨을 보장하나요?",
    answer:
      "아닙니다. 예측은 공개된 과거 데이터를 기반으로 한 실험적인 것으로, 연구와 오락 목적으로만 제공됩니다. 재정적 또는 도박 조언이 아닙니다.",
  },
  {
    question: "당첨 번호는 어디서 볼 수 있나요?",
    answer:
      "/numbers4/result의 결과 색인 또는 허브에서 연결된 각 추첨 페이지를 이용하세요. 주요 UI 레이블은 일본어입니다.",
  },
] as const;

const pageDescription =
  "비공식 Numbers4(일본) 대시보드: 결과 목록, 통계, 트렌드, 다중 모델 일일 예측. 한국어 개요; 앱 UI는 주로 일본어입니다.";

export const metadata: Metadata = {
  title: "Takarakuji AI — Numbers4 결과 및 예측 (개요)",
  description: pageDescription,
  alternates: {
    canonical: "/ko",
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
    type: "website",
    locale: "ko_KR",
    alternateLocale: ["ja_JP", "en_US"],
    url: absoluteUrl("/ko"),
    title: "Takarakuji AI — Numbers4 결과 및 예측",
    description: "Numbers4 추첨 결과, 통계, 모델 예측을 열람하세요. 비공식 분석 사이트입니다.",
  },
};

export default function KoreanOverviewPage() {
  const origin = getSiteOrigin();

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "ko",
    mainEntity: koFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/ko#webpage`,
    url: `${origin}/ko`,
    name: "Takarakuji AI — 한국어 개요",
    description: pageDescription,
    inLanguage: "ko",
    isPartOf: { "@id": `${origin}/#website` },
  };

  return (
    <div lang="ko" className="flex flex-1 flex-col">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }} />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide">한국어 개요 · LLM 친화적 요약</p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">Takarakuji AI</h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            비공식 <strong className="text-foreground">Numbers4</strong>(일본) 대시보드: 당첨 번호, 통계, 트렌드, 여러 일일 예측 모델 — 공개 데이터 기반.{" "}
            <strong className="text-foreground">어떤</strong> 복권 운영자와도 관련 없습니다.{" "}
            <Link href="/" className="text-primary font-medium underline-offset-4 hover:underline">일본어 홈</Link>
            {" · "}
            <Link href="/en" className="text-primary font-medium underline-offset-4 hover:underline">English</Link>
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">주요 페이지 (일본어 UI)</h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li><Link href="/numbers4" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4</Link> — 예측 및 도구 허브</li>
            <li><Link href="/numbers4/result" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/result</Link> — 결과 색인</li>
            <li><Link href="/numbers4/stats" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/stats</Link>, <Link href="/numbers4/trend" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/trend</Link> — 분석</li>
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">자주 묻는 질문</h2>
          <div className="space-y-6">
            {koFaq.map((item) => (
              <div key={item.question} className="space-y-2">
                <h3 className="text-foreground text-base font-medium">{item.question}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">{item.answer}</p>
              </div>
            ))}
          </div>
        </section>

        <div>
          <Link href="/numbers4" className={cn(buttonVariants({ size: "lg" }), "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500")}>
            Numbers4 허브 열기
          </Link>
        </div>
      </div>
    </div>
  );
}

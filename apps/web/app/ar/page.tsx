import type { Metadata } from "next";
import Link from "next/link";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const arFaq = [
  {
    question: "ما هو تاكاراكوجي AI؟",
    answer:
      "تطبيق ويب غير رسمي يركّز على يانصيب Numbers4 الياباني: تصفّح نتائج السحب الرسمية، واستكشف الإحصائيات والاتجاهات، وقارن بين نماذج التنبّؤ اليومية المتعددة. الواجهة باللغة اليابانية بشكل أساسي؛ تلخّص هذه الصفحة الخدمة بالعربية للزوّار الدوليين.",
  },
  {
    question: "هل هذا الموقع رسمي أو تابع للقرعة؟",
    answer:
      "لا. لا علاقة له ببنك ميزوهو أو اليانصيب الياباني أو أي مشغّل رسمي. تحقّق دائمًا من النتائج عبر المصادر الرسمية قبل الاعتماد عليها.",
  },
  {
    question: "هل التنبؤات تضمن الفوز؟",
    answer:
      "لا. التنبؤات تجريبية ومبنية على بيانات تاريخية عامة. وهي للبحث والترفيه فقط، وليست نصيحة مالية أو تشجيعًا على المقامرة.",
  },
  {
    question: "أين يمكنني رؤية الأرقام الفائزة؟",
    answer:
      "استخدم فهرس النتائج في /numbers4/result أو صفحات كل سحب المرتبطة بالمركز. العناوين الأساسية باللغة اليابانية.",
  },
] as const;

const pageDescription =
  "لوحة معلومات غير رسمية لنمبرز 4 (اليابان): قوائم النتائج، الإحصائيات، الاتجاهات، والتنبؤات اليومية متعددة النماذج. نظرة عامة بالعربية؛ واجهة التطبيق يابانية بشكل أساسي.";

export const metadata: Metadata = {
  title: "تاكاراكوجي AI — نتائج وتنبؤات Numbers4 (نظرة عامة)",
  description: pageDescription,
  keywords: [
    "Numbers4",
    "نمبرز 4",
    "اليانصيب الياباني",
    "يانصيب اليابان",
    "نتائج السحب",
    "الأرقام الفائزة",
    "تاكاراكوجي",
    "Takarakuji AI",
    "Japan lottery",
    "Japanese lottery",
    "lottery statistics",
    "draw results",
  ],
  alternates: {
    canonical: "/ar",
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
    locale: "ar_SA",
    alternateLocale: ["ja_JP", "en_US"],
    url: absoluteUrl("/ar"),
    title: "تاكاراكوجي AI — نتائج وتنبؤات Numbers4",
    description:
      "تصفّح نتائج سحب Numbers4، الإحصائيات، وتنبؤات النماذج. موقع تحليلي غير رسمي؛ غير مرتبط بأي مشغّل يانصيب.",
  },
  twitter: {
    card: "summary",
    title: "تاكاراكوجي AI — Numbers4",
    description:
      "لوحة نتائج وتنبؤات Numbers4 غير رسمية (اليابان). صفحة نظرة عامة بالعربية.",
  },
};

export default function ArabicOverviewPage() {
  const origin = getSiteOrigin();
  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "ar",
    mainEntity: arFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/ar#webpage`,
    url: `${origin}/ar`,
    name: "تاكاراكوجي AI — نظرة عامة بالعربية",
    description: pageDescription,
    inLanguage: "ar",
    isPartOf: { "@id": `${origin}/#website` },
    about: {
      "@type": "Thing",
      name: "Numbers4",
      description:
        "لعبة يانصيب أرقام في اليابان (أربعة أرقام). هذا الموقع غير رسمي.",
    },
  };

  return (
    <div lang="ar" dir="rtl" className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide">
            نظرة عامة بالعربية · ملخص صديق للذكاء الاصطناعي
          </p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            تاكاراكوجي AI
          </h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            لوحة معلومات غير رسمية لـ{" "}
            <strong className="text-foreground">Numbers4</strong> (اليابان):
            الأرقام الفائزة، الإحصائيات، الاتجاهات، ونماذج تنبؤ يومية متعددة
            — مبنية على بيانات عامة.{" "}
            <strong className="text-foreground">غير</strong> مرتبط بأي مشغّل
            يانصيب.{" "}
            <Link
              href="/"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              الصفحة الرئيسية (يابانية)
            </Link>
            {" · "}
            <Link
              href="/en"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              English
            </Link>
            .
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">
            الصفحات الرئيسية (واجهة يابانية)
          </h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li>
              <Link
                href="/numbers4"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4
              </Link>{" "}
              — مركز التنبؤات والأدوات
            </li>
            <li>
              <Link
                href="/numbers4/result"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/result
              </Link>{" "}
              — فهرس النتائج
            </li>
            <li>
              <Link
                href="/numbers4/stats"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/stats
              </Link>
              ،{" "}
              <Link
                href="/numbers4/trend"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /numbers4/trend
              </Link>{" "}
              — التحليلات
            </li>
            <li>
              <Link
                href="/llms.txt"
                className="text-primary font-medium underline-offset-4 hover:underline"
              >
                /llms.txt
              </Link>{" "}
              — ملخص الموقع للآلات
            </li>
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">
            الأسئلة الشائعة
          </h2>
          <div className="space-y-6">
            {arFaq.map((item) => (
              <div key={item.question} className="space-y-2">
                <h3 className="text-foreground text-base font-medium">
                  {item.question}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
                  {item.answer}
                </p>
              </div>
            ))}
          </div>
        </section>

        <div>
          <Link
            href="/numbers4"
            className={cn(
              buttonVariants({ size: "lg" }),
              "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500",
            )}
          >
            افتح مركز Numbers4
          </Link>
        </div>
      </div>
    </div>
  );
}

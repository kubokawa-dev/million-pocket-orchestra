import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowLeftIcon,
  Building2Icon,
  Globe2Icon,
  LineChartIcon,
  ShieldCheckIcon,
  SparklesIcon,
} from "lucide-react";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const arFaq = [
  {
    question: "ما هو تاكاراكوجي AI؟",
    answer:
      "منصّة ويب غير رسمية تنطلق من بيانات ألعاب الأرقام في اليابان، وتجمع بين نتائج السحب، والإحصاءات، والاتجاهات، ومخرجات النماذج المرجعية اليومية ضمن واجهة واحدة. هذه الصفحة العربية ليست مجرد ترجمة مختصرة، بل بوابة تعريفية للزوّار والشركاء الدوليين.",
  },
  {
    question: "هل الموقع رسمي أو تابع لمشغّل اليانصيب؟",
    answer:
      "لا. لا توجد أي علاقة تشغيلية مع بنك ميزوهو أو اليانصيب الياباني أو أي جهة رسمية. يجب دائمًا الرجوع إلى المصادر الرسمية عند التحقق من النتائج.",
  },
  {
    question: "هل التنبؤات أو مخرجات النماذج تضمن الفوز؟",
    answer:
      "لا. هذه مخرجات تحليلية وتجريبية مبنية على بيانات عامة وتاريخية، والغرض منها البحث والترفيه وتنظيم المعلومات، وليست نصيحة مالية أو دعوة للمقامرة.",
  },
  {
    question: "لماذا قد يهم هذا المنتج شريكًا استراتيجيًا؟",
    answer:
      "لأن القيمة لا تكمن في لعبة واحدة فقط، بل في تراكم البيانات، والانضباط في العرض، وإمكانية التوسّع متعدد اللغات والأسواق ضمن فئة منظّمة وحساسة للثقة.",
  },
] as const;

const strategicPoints = [
  {
    icon: Globe2Icon,
    title: "من اليابان إلى جمهور دولي",
    body:
      "المنتج مبني على سوق ياباني محدد، لكن طبقة العرض والتموضع أصبحت مناسبة للإنجليزية والعربية ومداخل دولية أخرى.",
  },
  {
    icon: LineChartIcon,
    title: "أصل بيانات يتراكم بمرور الوقت",
    body:
      "كل سحب جديد، وكل تقرير نموذج، وكل مقارنة تاريخية تضيف قيمة مركبة. هذا أقرب إلى أصل معلوماتي منه إلى صفحة محتوى عابرة.",
  },
  {
    icon: ShieldCheckIcon,
    title: "نبرة مسؤولة وهادئة",
    body:
      "الموقع لا يبيع الوهم. هذا مهم جدًا عند مخاطبة رأس مال طويل الأجل أو شركاء يفضّلون منتجات منضبطة وقابلة للدفاع.",
  },
] as const;

const nextDoors = [
  {
    href: "/investors",
    title: "الملف الاستثماري",
    body: "نسخة أقرب إلى العرض الخاص بالشركاء ورأس المال الاستراتيجي.",
  },
  {
    href: "/en",
    title: "المدخل الإنجليزي",
    body: "عرض عام مناسب للمراجعة الدولية السريعة والمشاركة.",
  },
  {
    href: "/data-sources",
    title: "مصادر البيانات",
    body: "أول محطة لمن يريد التحقق من الجدية والشفافية قبل أي خطوة أخرى.",
  },
  {
    href: "/numbers4",
    title: "المنتج الرئيسي",
    body: "الدخول إلى الواجهة الأساسية حيث تظهر النماذج والتحليلات والنتائج.",
  },
] as const;

const pageDescription =
  "بوابة عربية لتاكاراكوجي AI: عرض تحليلي غير رسمي ينطلق من Numbers4 في اليابان ويتجه نحو سردية أوسع لمنتج بيانات وتحليلات متعدد اللغات.";

export const metadata: Metadata = {
  title: "تاكاراكوجي AI — بوابة عربية للشركاء والزوار الدوليين",
  description: pageDescription,
  keywords: [
    "Numbers4",
    "نمبرز 4",
    "اليانصيب الياباني",
    "تحليلات اليانصيب",
    "نتائج السحب",
    "تحليلات متعددة النماذج",
    "تاكاراكوجي AI",
    "Japan lottery",
    "Japanese lottery analytics",
    "Arabic overview",
    "strategic partner brief",
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
    title: "تاكاراكوجي AI — بوابة عربية",
    description:
      "مدخل عربي لمنتج تحليلي غير رسمي يبدأ من بيانات Numbers4 في اليابان ويتوسع كسردية بيانات وتحليلات متعددة اللغات.",
  },
  twitter: {
    card: "summary_large_image",
    title: "تاكاراكوجي AI — البوابة العربية",
    description: pageDescription,
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
    name: "تاكاراكوجي AI — بوابة عربية",
    description: pageDescription,
    inLanguage: "ar",
    isPartOf: { "@id": `${origin}/#website` },
    about: {
      "@type": "Thing",
      name: "Takarakuji AI",
      description:
        "بوابة تحليلات غير رسمية تبدأ من ألعاب الأرقام في اليابان مع تركيز على البيانات والشرح متعدد اللغات.",
    },
  };

  return (
    <div lang="ar" dir="rtl" className="flex flex-1 flex-col bg-[#fbf7ef]">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }}
      />

      <section className="px-4 pt-10 pb-8 sm:px-6 sm:pt-14 sm:pb-10">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-[2rem] border border-[#d6c6a0] bg-[linear-gradient(135deg,rgba(255,248,230,0.96),rgba(245,237,217,0.92)_52%,rgba(231,223,204,0.96)_100%)] shadow-[0_18px_60px_rgba(84,68,31,0.14)]">
          <div className="grid gap-8 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-10">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#b6914b]/25 bg-[#fffaf0] px-3 py-1 text-xs font-semibold tracking-[0.2em] text-[#8a6b2f]">
                <SparklesIcon className="size-3.5" />
                بوابة عربية مختارة
              </div>
              <div className="space-y-4">
                <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
                  Takarakuji AI / Arabic Strategic Entry
                </p>
                <h1 className="font-heading text-3xl font-semibold leading-tight tracking-tight text-[#21190f] sm:text-4xl lg:text-5xl">
                  من لوحة أرقام يابانية إلى أصل بيانات وتحليلات يمكن تقديمه بثقة
                  لشركاء دوليين.
                </h1>
                <p className="max-w-2xl text-sm leading-8 text-[#4d3d27] sm:text-base">
                  إذا كنت تزور الموقع من الخليج أو من خارج اليابان، فهذه الصفحة
                  هي المدخل الأفضل لفهم الفكرة: منتج تحليلي غير رسمي، منضبط في
                  النبرة، يتعامل مع البيانات والنتائج والنماذج كطبقة معرفة قابلة
                  للتوسّع، لا كوسيلة للمبالغة أو الإيحاء بضمان الربح.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link
                  href="/investors"
                  className={cn(
                    buttonVariants({ size: "lg" }),
                    "h-11 rounded-full bg-[#1d3b2f] px-5 text-white shadow-sm hover:bg-[#244a3b]",
                  )}
                >
                  افتح الملف الاستثماري
                  <ArrowLeftIcon className="size-4" />
                </Link>
                <Link
                  href="/en"
                  className={cn(
                    buttonVariants({ variant: "outline", size: "lg" }),
                    "h-11 rounded-full border-[#b6914b]/30 bg-white/70 px-5 text-[#2b2115] hover:bg-white",
                  )}
                >
                  English
                </Link>
                <Link
                  href="/numbers4"
                  className={cn(
                    buttonVariants({ variant: "ghost", size: "lg" }),
                    "h-11 rounded-full px-5 text-[#5a4528] hover:bg-white/70 hover:text-[#21190f]",
                  )}
                >
                  المنتج الرئيسي
                </Link>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
              {[
                { label: "السوق الحالي", value: "اليابان" },
                { label: "مداخل اللغة", value: "7" },
                { label: "الطابع", value: "هادئ ومنضبط" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-[1.4rem] border border-[#d8c9a8] bg-white/65 px-5 py-4"
                >
                  <p className="text-xs tracking-[0.18em] text-[#8a7651]">
                    {item.label}
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-[#21190f]">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="mx-auto grid max-w-5xl gap-4 md:grid-cols-3">
          {strategicPoints.map(({ icon: Icon, title, body }) => (
            <div
              key={title}
              className="rounded-[1.5rem] border border-[#dfd3b8] bg-white/70 p-5 shadow-[0_10px_30px_rgba(84,68,31,0.06)]"
            >
              <div className="inline-flex size-10 items-center justify-center rounded-2xl bg-[#f3ead5] text-[#8a6b2f]">
                <Icon className="size-5" />
              </div>
              <h2 className="mt-4 text-lg font-semibold text-[#21190f]">{title}</h2>
              <p className="mt-3 text-sm leading-7 text-[#5a4528]">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="px-4 py-8 sm:px-6 sm:py-10">
        <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[1.75rem] border border-[#d8c9a8] bg-white/75 p-6 sm:p-8">
            <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
              لماذا قد يلفت هذا انتباه مستثمر طويل الأجل؟
            </p>
            <h2 className="mt-3 font-heading text-2xl font-semibold leading-tight text-[#21190f] sm:text-3xl">
              لأن القيمة هنا في الانضباط وتراكم الأصل، لا في الصخب.
            </h2>
            <div className="mt-5 space-y-4 text-sm leading-8 text-[#4d3d27] sm:text-base">
              <p>
                كثير من المشاريع المشابهة تبدو مؤقتة أو مبالغًا فيها. أما هنا،
                فالسردية الأقوى هي أن هناك أصلًا معلوماتيًا يتوسع ببطء وبثبات:
                نتائج، أرشيف، نماذج، شرح، وصفحات دولية، وإطار استخدام مسؤول.
              </p>
              <p>
                هذا النوع من المنتجات يمكن أن يتطور إلى طبقة تحليل أو بحث أو
                شراكات إعلامية وبيانات، بدل أن يبقى مجرد موقع يتحدث عن الأرقام.
              </p>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-[#d8c9a8] bg-[#1d3b2f] p-6 text-[#f5ecdb] sm:p-8">
            <p className="text-sm font-medium tracking-[0.18em] text-[#d9c49a]">
              مسار الزائر الجاد
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-7 sm:text-base">
              {nextDoors.map((item) => (
                <li key={item.href} className="flex gap-3">
                  <Building2Icon className="mt-1 size-4 shrink-0 text-[#d9c49a]" />
                  <div>
                    <Link
                      href={item.href}
                      className="font-semibold text-[#fff7e7] underline-offset-4 hover:underline"
                    >
                      {item.title}
                    </Link>
                    <p className="mt-1 text-[#e4d9c1]">{item.body}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="rounded-[1.75rem] border border-[#dfd3b8] bg-white/75 p-6 sm:p-8">
          <h2 className="text-xl font-semibold text-[#21190f] sm:text-2xl">
            الأسئلة الشائعة
          </h2>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            {arFaq.map((item) => (
              <div
                key={item.question}
                className="rounded-[1.25rem] border border-[#ece2cb] bg-[#fffdf8] p-5"
              >
                <h3 className="text-base font-semibold text-[#21190f]">
                  {item.question}
                </h3>
                <p className="mt-2 text-sm leading-7 text-[#5a4528]">
                  {item.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 pt-2 pb-16 sm:px-6 sm:pb-20">
        <div className="mx-auto flex max-w-5xl flex-wrap gap-3 rounded-[1.75rem] border border-[#d6c6a0] bg-[linear-gradient(135deg,rgba(255,250,240,0.96),rgba(244,235,216,0.9))] p-6 sm:items-center sm:justify-between sm:p-8">
          <div className="max-w-2xl">
            <p className="text-sm font-medium tracking-[0.18em] text-[#8a7651]">
              الخطوة التالية الموصى بها
            </p>
            <h2 className="mt-2 font-heading text-2xl font-semibold text-[#21190f]">
              ابدأ من الملف الاستثماري، ثم راجع مصادر البيانات والمنتج الأساسي.
            </h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/investors"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 rounded-full bg-[#1d3b2f] px-5 text-white shadow-sm hover:bg-[#244a3b]",
              )}
            >
              الملف الاستثماري
            </Link>
            <Link
              href="/data-sources"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "h-11 rounded-full border-[#b6914b]/30 bg-white/70 px-5 text-[#2b2115] hover:bg-white",
              )}
            >
              مصادر البيانات
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

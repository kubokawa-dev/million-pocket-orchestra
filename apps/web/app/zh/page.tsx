import type { Metadata } from "next";
import Link from "next/link";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const zhFaq = [
  {
    question: "什么是 Takarakuji AI？",
    answer:
      "这是一个非官方网页应用，专注于日本的 Numbers4 彩票：浏览官方开奖结果、探索统计数据和趋势，以及比较多种每日预测模型。界面主要为日语；本页面为国际访客提供中文概述。",
  },
  {
    question: "这是官方或附属于彩票的网站吗？",
    answer:
      "不是。本站与瑞穗银行、日本彩票或任何运营商无关。在依赖任何信息之前，请务必通过官方渠道核实结果。",
  },
  {
    question: "预测能保证中奖吗？",
    answer:
      "不能。预测基于公开历史数据，仅供研究和娱乐参考，不构成财务或博彩建议。",
  },
  {
    question: "在哪里可以查看中奖号码？",
    answer:
      "请访问 /numbers4/result 的结果索引页或从中心页面链接的各期页面。主要界面标签为日语。",
  },
] as const;

const pageDescription =
  "非官方 Numbers4（日本）仪表板：结果列表、统计数据、趋势和多模型每日预测。中文概述；应用界面主要为日语。";

export const metadata: Metadata = {
  title: "Takarakuji AI — Numbers4 结果与预测（概述）",
  description: pageDescription,
  alternates: {
    canonical: "/zh",
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
    locale: "zh_CN",
    alternateLocale: ["ja_JP", "en_US"],
    url: absoluteUrl("/zh"),
    title: "Takarakuji AI — Numbers4 结果与预测",
    description:
      "浏览 Numbers4 开奖结果、统计数据和模型预测。非官方分析网站；与任何彩票运营商无关。",
  },
};

export default function ChineseOverviewPage() {
  const origin = getSiteOrigin();

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "zh",
    mainEntity: zhFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/zh#webpage`,
    url: `${origin}/zh`,
    name: "Takarakuji AI — 中文概述",
    description: pageDescription,
    inLanguage: "zh",
    isPartOf: { "@id": `${origin}/#website` },
  };

  return (
    <div lang="zh" className="flex flex-1 flex-col">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }} />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide">中文概述 · LLM 友好摘要</p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">Takarakuji AI</h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            非官方 <strong className="text-foreground">Numbers4</strong>（日本）仪表板：中奖号码、统计数据、趋势和多种每日预测模型——基于公开数据构建。
            <strong className="text-foreground">与</strong>任何彩票运营商无关。{" "}
            <Link href="/" className="text-primary font-medium underline-offset-4 hover:underline">日语首页</Link>
            {" · "}
            <Link href="/en" className="text-primary font-medium underline-offset-4 hover:underline">English</Link>
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">主要页面（日语界面）</h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li><Link href="/numbers4" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4</Link> — 预测与工具中心</li>
            <li><Link href="/numbers4/result" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/result</Link> — 结果索引</li>
            <li><Link href="/numbers4/stats" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/stats</Link>、<Link href="/numbers4/trend" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/trend</Link> — 分析</li>
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">常见问题</h2>
          <div className="space-y-6">
            {zhFaq.map((item) => (
              <div key={item.question} className="space-y-2">
                <h3 className="text-foreground text-base font-medium">{item.question}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">{item.answer}</p>
              </div>
            ))}
          </div>
        </section>

        <div>
          <Link href="/numbers4" className={cn(buttonVariants({ size: "lg" }), "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500")}>
            打开 Numbers4 中心
          </Link>
        </div>
      </div>
    </div>
  );
}

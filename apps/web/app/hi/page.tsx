import type { Metadata } from "next";
import Link from "next/link";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const hiFaq = [
  {
    question: "Takarakuji AI क्या है?",
    answer:
      "यह जापान की Numbers4 लॉटरी पर केंद्रित एक अनौपचारिक वेब ऐप है: आधिकारिक ड्रॉ परिणाम ब्राउज़ करें, सांख्यिकी और रुझान देखें, और कई दैनिक पूर्वानुमान मॉडलों की तुलना करें। इंटरफ़ेस मुख्य रूप से जापानी में है; यह पृष्ठ अंतरराष्ट्रीय आगंतुकों के लिए हिंदी में सारांश प्रदान करता है।",
  },
  {
    question: "क्या यह साइट आधिकारिक है या लॉटरी से संबद्ध है?",
    answer:
      "नहीं। इसका मिज़ुहो बैंक, जापान लॉटरी या किसी ऑपरेटर से कोई संबंध नहीं है। किसी भी जानकारी पर भरोसा करने से पहले हमेशा आधिकारिक स्रोतों से परिणाम सत्यापित करें।",
  },
  {
    question: "क्या पूर्वानुमान जीत की गारंटी देते हैं?",
    answer:
      "नहीं। पूर्वानुमान प्रयोगात्मक हैं और सार्वजनिक ऐतिहासिक डेटा पर आधारित हैं। ये केवल शोध और मनोरंजन के लिए हैं, वित्तीय या जुआ सलाह नहीं हैं।",
  },
  {
    question: "विजेता नंबर कहाँ देख सकते हैं?",
    answer:
      "/numbers4/result पर परिणाम सूचकांक या हब से जुड़े प्रति-ड्रॉ पृष्ठों का उपयोग करें। मुख्य UI लेबल जापानी में हैं।",
  },
] as const;

const pageDescription =
  "अनौपचारिक Numbers4 (जापान) डैशबोर्ड: परिणाम सूची, सांख्यिकी, रुझान और बहु-मॉडल दैनिक पूर्वानुमान। हिंदी अवलोकन; ऐप UI मुख्य रूप से जापानी है।";

export const metadata: Metadata = {
  title: "Takarakuji AI — Numbers4 परिणाम और पूर्वानुमान (अवलोकन)",
  description: pageDescription,
  alternates: {
    canonical: "/hi",
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
    locale: "hi_IN",
    alternateLocale: ["ja_JP", "en_US"],
    url: absoluteUrl("/hi"),
    title: "Takarakuji AI — Numbers4 परिणाम और पूर्वानुमान",
    description: "Numbers4 ड्रॉ परिणाम, सांख्यिकी और मॉडल पूर्वानुमान ब्राउज़ करें। अनौपचारिक विश्लेषण साइट।",
  },
};

export default function HindiOverviewPage() {
  const origin = getSiteOrigin();

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "hi",
    mainEntity: hiFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/hi#webpage`,
    url: `${origin}/hi`,
    name: "Takarakuji AI — हिंदी अवलोकन",
    description: pageDescription,
    inLanguage: "hi",
    isPartOf: { "@id": `${origin}/#website` },
  };

  return (
    <div lang="hi" className="flex flex-1 flex-col">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }} />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide">हिंदी अवलोकन · AI-अनुकूल सारांश</p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">Takarakuji AI</h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            अनौपचारिक <strong className="text-foreground">Numbers4</strong> (जापान) डैशबोर्ड: विजेता नंबर, सांख्यिकी, रुझान और कई दैनिक पूर्वानुमान मॉडल — सार्वजनिक डेटा पर आधारित।{" "}
            किसी भी लॉटरी ऑपरेटर से <strong className="text-foreground">संबद्ध नहीं</strong>।{" "}
            <Link href="/" className="text-primary font-medium underline-offset-4 hover:underline">जापानी होम</Link>
            {" · "}
            <Link href="/en" className="text-primary font-medium underline-offset-4 hover:underline">English</Link>
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">मुख्य पृष्ठ (जापानी UI)</h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li><Link href="/numbers4" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4</Link> — पूर्वानुमान और उपकरण केंद्र</li>
            <li><Link href="/numbers4/result" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/result</Link> — परिणाम सूचकांक</li>
            <li><Link href="/numbers4/stats" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/stats</Link>, <Link href="/numbers4/trend" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/trend</Link> — विश्लेषण</li>
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">अक्सर पूछे जाने वाले प्रश्न</h2>
          <div className="space-y-6">
            {hiFaq.map((item) => (
              <div key={item.question} className="space-y-2">
                <h3 className="text-foreground text-base font-medium">{item.question}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">{item.answer}</p>
              </div>
            ))}
          </div>
        </section>

        <div>
          <Link href="/numbers4" className={cn(buttonVariants({ size: "lg" }), "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500")}>
            Numbers4 केंद्र खोलें
          </Link>
        </div>
      </div>
    </div>
  );
}

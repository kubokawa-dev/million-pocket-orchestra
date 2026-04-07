import type { Metadata } from "next";
import Link from "next/link";

import { absoluteUrl, getSiteOrigin } from "@/lib/site";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

const esFaq = [
  {
    question: "¿Qué es Takarakuji AI?",
    answer:
      "Una aplicación web no oficial centrada en la lotería Numbers4 de Japón: consulta los resultados oficiales de los sorteos, explora estadísticas y tendencias, y compara múltiples modelos de predicción diaria. La interfaz está principalmente en japonés; esta página resume el servicio en español para visitantes internacionales.",
  },
  {
    question: "¿Es este sitio oficial o está afiliado a la lotería?",
    answer:
      "No. No está afiliado a Mizuho Bank, la Lotería de Japón ni ningún operador. Siempre verifica los resultados en fuentes oficiales antes de confiar en ellos.",
  },
  {
    question: "¿Las predicciones garantizan premios?",
    answer:
      "No. Las predicciones son experimentales y se basan en datos históricos públicos. Son solo para investigación y entretenimiento, no constituyen asesoramiento financiero ni de apuestas.",
  },
  {
    question: "¿Dónde puedo ver los números ganadores?",
    answer:
      "Usa el índice de resultados en /numbers4/result o las páginas de cada sorteo enlazadas desde el centro. Las etiquetas principales están en japonés.",
  },
] as const;

const pageDescription =
  "Panel no oficial de Numbers4 (Japón): listados de resultados, estadísticas, tendencias y predicciones diarias con múltiples modelos. Resumen en español; la interfaz de la app es principalmente en japonés.";

export const metadata: Metadata = {
  title: "Takarakuji AI — Resultados y predicciones de Numbers4 (resumen)",
  description: pageDescription,
  alternates: {
    canonical: "/es",
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
    locale: "es_ES",
    alternateLocale: ["ja_JP", "en_US"],
    url: absoluteUrl("/es"),
    title: "Takarakuji AI — Resultados y predicciones de Numbers4",
    description: "Consulta resultados de sorteos Numbers4, estadísticas y predicciones de modelos. Sitio analítico no oficial.",
  },
};

export default function SpanishOverviewPage() {
  const origin = getSiteOrigin();

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    inLanguage: "es",
    mainEntity: esFaq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };

  const webPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${origin}/es#webpage`,
    url: `${origin}/es`,
    name: "Takarakuji AI — Resumen en español",
    description: pageDescription,
    inLanguage: "es",
    isPartOf: { "@id": `${origin}/#website` },
  };

  return (
    <div lang="es" className="flex flex-1 flex-col">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageJsonLd) }} />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <p className="text-muted-foreground text-sm font-medium tracking-wide">Resumen en español · Resumen amigable para IA</p>
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">Takarakuji AI</h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            Panel no oficial de <strong className="text-foreground">Numbers4</strong> (Japón): números ganadores, estadísticas, tendencias y múltiples modelos de predicción diaria — construido con datos públicos.{" "}
            <strong className="text-foreground">No</strong> afiliado a ningún operador de lotería.{" "}
            <Link href="/" className="text-primary font-medium underline-offset-4 hover:underline">Inicio (japonés)</Link>
            {" · "}
            <Link href="/en" className="text-primary font-medium underline-offset-4 hover:underline">English</Link>
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-foreground text-lg font-semibold">Páginas principales (interfaz en japonés)</h2>
          <ul className="text-muted-foreground list-inside list-disc space-y-2 text-sm leading-relaxed sm:text-base">
            <li><Link href="/numbers4" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4</Link> — Centro de predicciones y herramientas</li>
            <li><Link href="/numbers4/result" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/result</Link> — Índice de resultados</li>
            <li><Link href="/numbers4/stats" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/stats</Link>, <Link href="/numbers4/trend" className="text-primary font-medium underline-offset-4 hover:underline">/numbers4/trend</Link> — Análisis</li>
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-foreground text-lg font-semibold">Preguntas frecuentes</h2>
          <div className="space-y-6">
            {esFaq.map((item) => (
              <div key={item.question} className="space-y-2">
                <h3 className="text-foreground text-base font-medium">{item.question}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">{item.answer}</p>
              </div>
            ))}
          </div>
        </section>

        <div>
          <Link href="/numbers4" className={cn(buttonVariants({ size: "lg" }), "bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500")}>
            Abrir centro Numbers4
          </Link>
        </div>
      </div>
    </div>
  );
}

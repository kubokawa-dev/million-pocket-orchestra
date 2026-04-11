import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLinkIcon } from "lucide-react";

import { buildBreadcrumbJsonLd } from "@/lib/breadcrumb-jsonld";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "倫理的配慮・健全な利用について",
  description:
    "宝くじAIの位置づけ、偶然性と過去データの限界、年齢条件、依存症相談先など。非公式サービスとしての利用上の注意。",
  alternates: { canonical: "/responsible-use" },
  openGraph: {
    title: "倫理的配慮・健全な利用について | 宝くじAI",
    description:
      "当選の保証はなく、購入を推奨するサービスでもありません。透明性と自己責任のための説明です。",
    url: "/responsible-use",
  },
};

const externalResources = [
  {
    href: "https://izonsho.mhlw.go.jp/",
    label: "依存症対策ポータル（厚生労働省）",
    note: "ギャンブル等の依存症に関する公的な情報・相談先の案内",
  },
] as const;

export default function ResponsibleUsePage() {
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "倫理的配慮・健全な利用について", path: "/responsible-use" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-8 px-4 py-10 sm:px-6 sm:py-14">
        <header className="scroll-mt-24 space-y-3" id="ethical">
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            倫理的配慮・健全な利用について
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            利用前に必ずお読みください。宝くじAIを長く、誤解なく使っていただくための説明です（法的助言ではありません）。
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">サービスの位置づけ</CardTitle>
            <CardDescription>
              「当選予想」ではなく、閲覧・整理・参加の検討を補助するツール
            </CardDescription>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
            <p>
              当サイトは<strong className="text-foreground">抽選結果の閲覧</strong>や
              <strong className="text-foreground">公開データに基づく試算・可視化</strong>
              をまとめる非公式のWebアプリです。
              <strong className="text-foreground">当せん・的中の保証は一切ありません。</strong>
            </p>
            <p>
              画面上の<strong className="text-foreground">パターン分析や順位</strong>は、主に
              <strong className="text-foreground">参加行動や候補リストの整理</strong>
              をしやすくするためのものです。最適な購入や当せんを保証する「参加行動最適化」ではありません。
            </p>
            <p>
              表示されるモデル試算や統計は、過去のデータやモデルから得られる
              <strong className="text-foreground">参考情報</strong>
              であり、将来の結果を約束するものではありません。娯楽・学習・情報整理としてご利用ください。
            </p>
            <p>
              <strong className="text-foreground">宝くじの購入を推奨するサービスではありません。</strong>
              購入の有無・金額は、ご自身の判断と責任で決めてください。条件のたたき台は
              <Link href="/terms" className="text-foreground font-medium underline-offset-4 hover:underline">
                利用規約（草案）
              </Link>
              をご覧ください。
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">過去データと「パターン」について</CardTitle>
            <CardDescription>見え方と現実のズレに注意</CardDescription>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
            <p>
              グラフや順位・頻度などは、主に<strong className="text-foreground">参加行動やモデル出力の整理</strong>
              をしやすくするためのものです。抽選は本質的に偶然性が大きく、
              <strong className="text-foreground">
                過去に似た形が出たからといって、同じ傾向が続くとは限りません。
              </strong>
            </p>
            <p>
              分析結果には常に<strong className="text-foreground">解釈の余地と限界</strong>
              があります。気持ちよく見えるパターンは、人間の認知バイアス（見たいものが見えやすい）の影響も受けやすい点にご注意ください。
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">年齢・利用条件</CardTitle>
            <CardDescription>自己宣言ベースの確認</CardDescription>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
            <p>
              日本の宝くじは<strong className="text-foreground">18歳未満の購入が禁止</strong>
              されています。当サイトも、
              <strong className="text-foreground">18歳未満の方を対象としません。</strong>
              画面下部のバナーから、年齢条件への同意をお願いしています。
            </p>
            <p>
              ブラウザに保存される同意は技術的な補助であり、本人確認を代替するものではありません。保護者の方は、ご家庭のルールに沿ってご利用ください。
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">予算と生活の優先順位</CardTitle>
            <CardDescription>過度な支出を防ぐために</CardDescription>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
            <p>
              生活費・借入返済・学費など、先に確保すべきお金の後回しにしないでください。無理な継続購入は、依存のリスクを高めます。
            </p>
            <p>
              将来の資産形成や投資の話は<strong className="text-foreground">一般的な説明にとどまるべき領域</strong>
              です。個別の金融商品の勧誘や確実な利回りの提示は行いません。
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">相談・公的な情報</CardTitle>
            <CardDescription>不安が強いときは、専門の支援情報へ</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-relaxed">
            <p className="text-muted-foreground">
              「止められない」「隠して購入している」などの感覚がある場合は、一人で抱え込まず、公的な相談窓口や医療・支援機関の情報を参照してください。
            </p>
            <ul className="space-y-2">
              {externalResources.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground inline-flex items-center gap-1.5 font-medium underline-offset-4 hover:underline"
                  >
                    {item.label}
                    <ExternalLinkIcon className="size-3.5 shrink-0 opacity-70" aria-hidden />
                  </a>
                  <p className="text-muted-foreground mt-0.5 text-xs">{item.note}</p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Link href="/terms" className={cn(buttonVariants({ variant: "default" }), "shadow-sm")}>
            利用規約（草案）
          </Link>
          <Link href="/faq" className={cn(buttonVariants({ variant: "secondary" }), "shadow-sm")}>
            FAQ へ
          </Link>
          <Link href="/data-sources" className={cn(buttonVariants({ variant: "outline" }))}>
            データの出所・API
          </Link>
          <Link href="/" className={cn(buttonVariants({ variant: "ghost" }))}>
            ホームへ
          </Link>
        </div>
      </div>
    </div>
  );
}

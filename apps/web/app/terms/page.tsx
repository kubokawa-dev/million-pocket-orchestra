import type { Metadata } from "next";
import Link from "next/link";

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
  title: "利用規約（草案）",
  description:
    "宝くじAIの利用条件、免責、年齢制限などのたたき台。正式運用前に専門家のレビューを推奨します。",
  alternates: { canonical: "/terms" },
  openGraph: {
    title: "利用規約（草案） | 宝くじAI",
    description:
      "非公式サービスとしての利用目的、責任の範囲、禁止事項のドラフトです。",
    url: "/terms",
  },
};

const sections: {
  id: string;
  title: string;
  body: readonly string[];
}[] = [
  {
    id: "preamble",
    title: "はじめに",
    body: [
      "この利用規約（以下「本規約」）は、本ウェブサイト「宝くじAI」（以下「本サービス」）の利用条件を定めるものです。本サービスを利用する前に、全文をお読みください。",
      "本規約は運営上のたたき台（草案）です。収益化・組織化・広告掲載などを行う場合は、弁護士等の専門家によるレビューと、必要に応じた個別契約・プライバシーポリシーの整備を強く推奨します。",
    ],
  },
  {
    id: "service",
    title: "第1条（サービスの性質）",
    body: [
      "本サービスは、日本の数字選択式宝くじ（ナンバーズ3・ナンバーズ4・ロト6等）に関する公開情報の閲覧・整理、および公開データに基づくモデル出力（試算・ランキング・統計表示等）を提供する、第三者による非公式のウェブアプリケーションです。",
      "本サービスは、みずほ銀行、宝くじの発売主体、その他の公式機関と一切関係ありません。画面上の当せん番号・払戻情報等は、公開データの二次的な表示であり、常に公式の発表・媒体で最終確認してください。",
      "本サービスが提供するモデル出力や可視化は、参加の検討や情報整理を補助するための参考情報にすぎず、当せん・的中・利益を保証するものではありません。「当選予想」や投資助言ではありません。",
    ],
  },
  {
    id: "eligibility",
    title: "第2条（利用資格・年齢）",
    body: [
      "利用者は、日本の関連法令に従い、満18歳以上であることを自己申告のうえで利用するものとします。18歳未満の方は本サービスを利用しないでください。",
      "ブラウザに保存される年齢確認の記録は、利用体験上の補助であり、本人確認を代替するものではありません。",
    ],
  },
  {
    id: "prohibited",
    title: "第3条（禁止事項）",
    body: [
      "法令または公序良俗に違反する行為、他者の権利を侵害する行為、本サービスまたは第三者のシステムに過度な負荷を与える行為、不正アクセスやスクレイピングの禁止範囲を超える自動取得を行うこと。",
      "本サービスを通じて得た情報を、第三者に対し「公式の保証」や「確実な当せん情報」として流布すること。",
      "その他、運営者が不適切と判断する行為。",
    ],
  },
  {
    id: "disclaimer",
    title: "第4条（免責）",
    body: [
      "本サービスの利用により生じたいかなる損害（逸失利益、精神的損害、データ消失等を含みますがこれらに限りません）について、運営者に故意または重過失がある場合を除き、運営者は責任を負いません。",
      "本サービスは現状有姿で提供され、正確性・完全性・有用性・特定目的適合性について、明示または黙示を問わず何ら保証しません。",
      "公開データの取り込み遅延・欠落・誤表示が生じうることを利用者は予め承諾するものとします。購入の可否・金額の決定は、常に利用者自身の判断と責任において行ってください。",
    ],
  },
  {
    id: "ip",
    title: "第5条（著作権等）",
    body: [
      "本サービスに含まれるデザイン、文章、プログラム、データベース構造等に関する権利は、運営者または正当な権利者に帰属します。私的利用の範囲を超える複製・改変・再配布を禁止します。",
    ],
  },
  {
    id: "changes",
    title: "第6条（規約の変更）",
    body: [
      "運営者は、必要に応じて本規約を変更できます。変更後の規約は、本サービス上に掲示した時点から効力を生じるものとします。掲載日以降の利用により、変更に同意したものとみなします。",
    ],
  },
  {
    id: "law",
    title: "第7条（準拠法・管轄）",
    body: [
      "本規約の準拠法は日本法とします。",
      "本サービスに関連して紛争が生じた場合、運営者と利用者は誠意をもって協議するものとします。協議によっても解決しない場合、東京地方裁判所を第一審の専属的合意管轄裁判所とします（運営体制の変更に伴い、管轄の見直しを行う場合があります）。",
    ],
  },
];

export default function TermsPage() {
  const breadcrumbJsonLd = buildBreadcrumbJsonLd([
    { name: "利用規約（草案）", path: "/terms" },
  ]);

  return (
    <div className="flex flex-1 flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <div className="mx-auto w-full max-w-2xl flex-1 space-y-8 px-4 py-10 sm:px-6 sm:py-14">
        <header className="space-y-3">
          <h1 className="text-foreground font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            利用規約（草案）
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed sm:text-base">
            最終更新: 2026年4月12日（例示日。運用時は実日付に更新してください）
          </p>
        </header>

        <Card className="border-amber-500/25 bg-amber-500/5 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">ドラフトであること</CardTitle>
            <CardDescription>
              本ページは利用者との公平性と透明性のためのたたき台です。事業化する際は必ず専門家レビューを行ってください。
            </CardDescription>
          </CardHeader>
        </Card>

        <div className="space-y-6">
          {sections.map((section) => (
            <section key={section.id} id={section.id} className="scroll-mt-24">
              <h2 className="text-foreground mb-3 text-lg font-semibold tracking-tight">
                {section.title}
              </h2>
              <div className="text-muted-foreground space-y-3 text-sm leading-relaxed">
                {section.body.map((p, i) => (
                  <p key={`${section.id}-${i}`}>{p}</p>
                ))}
              </div>
            </section>
          ))}
        </div>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">関連ページ</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Link
              href="/responsible-use#ethical"
              className={cn(buttonVariants({ variant: "secondary", size: "sm" }), "shadow-sm")}
            >
              健全な利用について
            </Link>
            <Link href="/faq" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
              FAQ
            </Link>
            <Link href="/data-sources" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
              データの出所
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

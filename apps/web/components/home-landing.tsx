import Link from "next/link";
import {
  ArrowRightIcon,
  BarChart3Icon,
  BookOpenIcon,
  CircleHelpIcon,
  FlameIcon,
  LayersIcon,
  ListOrderedIcon,
  SparklesIcon,
  ZapIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

const featureCards = [
  {
    href: "/numbers4/result",
    icon: ListOrderedIcon,
    title: "当選番号を一気見せ",
    tag: "公式結果",
    description:
      "過去の抽選を表でサクッと追跡。スマホは横スクロールで全列いける、見やすさガチ勢。",
    accent: "from-violet-500/15 to-transparent",
  },
  {
    href: "/numbers4",
    icon: LayersIcon,
    title: "マルチモデル予測ハブ",
    tag: "アンサンブル",
    description:
      "統計・ML・パターン系など、複数の頭脳をぶち込んだ日次予測を1画面にダッシュボード表示。",
    accent: "from-cyan-500/15 to-transparent",
  },
  {
    href: "/numbers4/stats",
    icon: BarChart3Icon,
    title: "ボックス順位の統計",
    tag: "検証モード",
    description:
      "「予測リストのどのあたりに当たりがいた？」をモデル別に集計。数字オタク歓喜のビュー。",
    accent: "from-amber-500/15 to-transparent",
  },
  {
    href: "/numbers4/trend",
    icon: FlameIcon,
    title: "Hot Model トレンド",
    tag: "今どれがアツい？",
    description:
      "直近の成績から“いま推しのモデル”を可視化。盛り上がりたい日のお供に。",
    accent: "from-rose-500/15 to-transparent",
  },
] as const;

export function HomeLanding() {
  return (
    <div className="flex flex-1 flex-col">
      {/* Hero */}
      <section className="relative px-4 pt-12 pb-12 sm:px-6 sm:pt-16 sm:pb-16 lg:pt-20 lg:pb-20">
        <div className="border-border/60 from-card/30 to-background/40 relative mx-auto max-w-3xl rounded-3xl border bg-gradient-to-b px-5 py-12 text-center shadow-sm ring-1 ring-black/5 sm:px-10 sm:py-14 dark:ring-white/10">
          <div className="mb-5 flex flex-wrap items-center justify-center gap-2">
            <Badge className="gap-1 border-0 bg-gradient-to-r from-violet-600 to-cyan-600 px-3 py-1 text-white shadow-sm">
              <SparklesIcon className="size-3.5" />
              宝くじAI
            </Badge>
            <Badge variant="secondary" className="font-medium">
              Numbers4 特化
            </Badge>
          </div>
          <h1 className="text-foreground font-heading text-balance text-4xl font-bold tracking-tight sm:text-5xl sm:leading-[1.1] lg:text-[2.75rem]">
            ナンバーズ4の
            <span className="bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-600 bg-clip-text text-transparent dark:from-violet-400 dark:via-fuchsia-400 dark:to-cyan-400">
              数字遊び
            </span>
            、
            <br className="hidden sm:block" />
            ここが本気のメインステージ。
          </h1>
          <p className="text-muted-foreground mx-auto mt-5 max-w-xl text-pretty text-base leading-relaxed sm:text-lg">
            <strong className="text-foreground font-semibold">宝くじAI</strong>
            は、当選番号の閲覧から複数AI・統計モデルの予測、成績の見える化までをまとめた
            <strong className="text-foreground font-semibold">ナンバーズ4専用ダッシュボード</strong>
            。Xで語れるネタも、じっくり検証も、どっちもアリ。
          </p>
          <div className="mt-8 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
            <Link
              href="/numbers4"
              className={cn(
                buttonVariants({ size: "lg" }),
                "gap-2 bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-md hover:from-violet-500 hover:to-cyan-500 sm:min-w-[240px]",
              )}
            >
              <ZapIcon className="size-4" />
              いま一番アツいゾーンへ
              <ArrowRightIcon className="size-4" />
            </Link>
            <Link
              href="/numbers4/result"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "justify-center border-border/80 bg-background/60 backdrop-blur-sm sm:min-w-[200px]",
              )}
            >
              当選番号一覧
            </Link>
          </div>
          <p className="text-muted-foreground mt-8 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs sm:text-sm">
            <Link href="/blog" className="text-primary font-medium underline-offset-4 hover:underline">
              使い方ブログ
            </Link>
            <span className="text-border">|</span>
            <Link href="/faq" className="text-primary font-medium underline-offset-4 hover:underline">
              FAQ
            </Link>
            <span className="text-border">|</span>
            <Link href="/en" className="text-primary font-medium underline-offset-4 hover:underline">
              English
            </Link>
            <span className="text-border">|</span>
            <Link
              href="/en/blog"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              Blog (EN)
            </Link>
            <span className="text-border">|</span>
            <Link
              href="/llms.txt"
              className="text-primary font-medium underline-offset-4 hover:underline"
            >
              AI向け要約
            </Link>
          </p>
        </div>
      </section>

      {/* Pitch strip */}
      <section className="px-4 pb-10 sm:px-6">
        <div className="mx-auto flex max-w-4xl flex-wrap justify-center gap-2">
          {[
            "複数モデル同時表示",
            "予算プラン付き",
            "スマホ最適化UI",
            "照合ハイライト",
            "統計・トレンド付き",
          ].map((label) => (
            <span
              key={label}
              className="border-border/70 bg-background/80 text-foreground/85 rounded-full border px-3 py-1 text-xs font-medium shadow-sm backdrop-blur-sm sm:text-sm"
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className="px-4 pb-16 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <div className="mb-8 text-center">
            <h2 className="text-foreground font-heading text-2xl font-bold tracking-tight sm:text-3xl">
              このサイトでできること
            </h2>
            <p className="text-muted-foreground mx-auto mt-2 max-w-2xl text-sm sm:text-base">
              ただの当選番号リストじゃ終わらない。予測・検証・トレンドまで、Numbers4好きのための機能を詰め込みました。
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {featureCards.map(
              ({ href, icon: Icon, title, tag, description, accent }) => (
                <Link key={href} href={href} className="group block h-full">
                  <Card
                    className={cn(
                      "border-border/70 h-full overflow-hidden bg-gradient-to-br to-card shadow-sm ring-1 ring-black/5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md dark:ring-white/10",
                      accent,
                    )}
                  >
                    <CardHeader className="pb-2">
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-xl">
                          <Icon className="size-5" />
                        </div>
                        <Badge variant="outline" className="text-[0.65rem] font-normal">
                          {tag}
                        </Badge>
                      </div>
                      <CardTitle className="text-base leading-snug group-hover:underline">
                        {title}
                      </CardTitle>
                      <CardDescription className="text-xs leading-relaxed sm:text-sm">
                        {description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <span className="text-primary inline-flex items-center gap-1 text-xs font-semibold">
                        ページを開く
                        <ArrowRightIcon className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                      </span>
                    </CardContent>
                  </Card>
                </Link>
              ),
            )}
          </div>
        </div>
      </section>

      {/* Story + disclaimer */}
      <section className="px-4 pb-16 sm:px-6">
        <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-5 lg:gap-8">
          <Card className="border-border/70 lg:col-span-3 lg:shadow-sm">
            <CardHeader>
              <CardTitle className="font-heading text-lg sm:text-xl">
                宝くじAI って何者？
              </CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                略して「数字とにらめっこするための、ちゃんとしたWebアプリ」です。
              </CardDescription>
            </CardHeader>
            <CardContent className="text-muted-foreground space-y-3 text-sm leading-relaxed">
              <p>
                ナンバーズ4の<strong className="text-foreground">公式に近い形の当選情報</strong>
                を一覧しつつ、リポジトリとDBに載った
                <strong className="text-foreground">日次予測データ</strong>
                をダッシュボード表示。アンサンブル・手法別・予算プランなど、種類が多いほど比較が楽しくなる構成にしています。
              </p>
              <p>
                「バズる予感のするUI」と「じっくり数字を追う体験」、両方取りにいきました。SNSでスクショ載せたくなるくらい、見せ方にはこだわってます。
              </p>
            </CardContent>
          </Card>
          <div className="flex flex-col gap-4 lg:col-span-2">
            <Card className="border-border/70 border-dashed bg-muted/20 shadow-none">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <CircleHelpIcon className="text-muted-foreground size-5" />
                  <CardTitle className="text-base">ちゃんと言っておくね</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="text-muted-foreground text-xs leading-relaxed sm:text-sm">
                予測は<strong className="text-foreground">過去データやモデルに基づく試算</strong>
                であり、当選や的中を保証するものではありません。娯楽・学習・情報整理として楽しんでください。購入を推奨するサービスではありません。
              </CardContent>
            </Card>
            <Link
              href="/blog"
              className={cn(
                buttonVariants({ variant: "secondary", size: "lg" }),
                "h-auto justify-start gap-3 py-4 text-left shadow-sm",
              )}
            >
              <BookOpenIcon className="size-5 shrink-0" />
              <span>
                <span className="text-foreground block text-sm font-semibold">
                  はじめてでも大丈夫
                </span>
                <span className="text-muted-foreground block text-xs font-normal">
                  ブログで画面の読み方を解説しています
                </span>
              </span>
              <ArrowRightIcon className="text-muted-foreground ml-auto size-4 shrink-0" />
            </Link>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="px-4 pb-20 sm:px-6">
        <div className="from-primary/10 via-violet-500/10 to-cyan-500/10 border-primary/20 relative mx-auto max-w-3xl overflow-hidden rounded-3xl border bg-gradient-to-br px-6 py-10 text-center sm:px-10 sm:py-12">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,oklch(0.7_0.2_280/0.2),transparent_50%)]" />
          <div className="relative">
            <h2 className="text-foreground font-heading text-xl font-bold sm:text-2xl">
              さあ、第1ゲームはナンバーズ4ダッシュボード
            </h2>
            <p className="text-muted-foreground mx-auto mt-2 max-w-md text-sm sm:text-base">
              当選を眺めるだけでも、予測を覗くだけでもOK。あなたの見たい回から飛び込んでみて。
            </p>
            <div className="mt-6 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:justify-center">
              <Link
                href="/numbers4"
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "gap-2 shadow-md sm:min-w-[220px]",
                )}
              >
                ナンバーズ4ゾーンへ
                <ArrowRightIcon className="size-4" />
              </Link>
              <Link
                href="/numbers4/result"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "border-background/20 bg-background/70 backdrop-blur-sm sm:min-w-[180px]",
                )}
              >
                当選番号から入る
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export type HomeLandingFeatureCardCopy = {
  href: string;
  title: string;
  tag: string;
  description: string;
  accent: string;
};

export type HomeLandingLanguageLink = {
  href: string;
  label: string;
  current?: boolean;
};

export type HomeLandingCopy = {
  hero: {
    badgeBrand: string;
    badgeFocus: string;
    titleLine1: string;
    titleHighlight: string;
    titleLine2: string;
    titleLine3: string;
    titleLineBreakBeforeLine3: boolean;
    introLead: string;
    introMid: string;
    /** Second emphasized phrase (e.g. product positioning); omit for a single-strong intro. */
    introEmphasis?: string;
    introTail: string;
    ctaPrimary: string;
    ctaSecondary: string;
    languageLinks: readonly HomeLandingLanguageLink[];
  };
  pitchLabels: readonly string[];
  features: {
    sectionTitle: string;
    sectionSubtitle: string;
    openPage: string;
    cards: readonly HomeLandingFeatureCardCopy[];
  };
  story: {
    title: string;
    subtitle: string;
    p1Lead: string;
    p1Strong1: string;
    p1Mid: string;
    p1Strong2: string;
    p1Tail: string;
    p2: string;
  };
  disclaimer: {
    title: string;
    bodyLead: string;
    bodyStrong: string;
    bodyTail: string;
  };
  blogCard: {
    title: string;
    subtitle: string;
  };
  bottomCta: {
    title: string;
    subtitle: string;
    primary: string;
    secondary: string;
  };
};

export const homeLandingCopyJa: HomeLandingCopy = {
  hero: {
    badgeBrand: "宝くじAI",
    badgeFocus: "Numbers4 特化",
    titleLine1: "ナンバーズ4の",
    titleHighlight: "数字遊び",
    titleLine2: "、",
    titleLine3: "ここが本気のメインステージ。",
    titleLineBreakBeforeLine3: true,
    introLead: "宝くじAI",
    introMid:
      "は、当選番号の閲覧から複数AI・統計モデルの予測、成績の見える化までをまとめた",
    introEmphasis: "ナンバーズ4専用ダッシュボード",
    introTail: "。Xで語れるネタも、じっくり検証も、どっちもアリ。",
    ctaPrimary: "いま一番アツいゾーンへ",
    ctaSecondary: "当選番号一覧",
    languageLinks: [
      { href: "/blog", label: "使い方ブログ" },
      { href: "/faq", label: "FAQ" },
      { href: "/en", label: "English" },
      { href: "/en/blog", label: "Blog (EN)" },
      { href: "/zh", label: "中文" },
      { href: "/ko", label: "한국어" },
      { href: "/es", label: "Español" },
      { href: "/hi", label: "हिन्दी" },
      { href: "/ar", label: "العربية" },
      { href: "/llms.txt", label: "AI向け要約" },
    ],
  },
  pitchLabels: [
    "複数モデル同時表示",
    "予算プラン付き",
    "スマホ最適化UI",
    "照合ハイライト",
    "統計・トレンド付き",
  ],
  features: {
    sectionTitle: "このサイトでできること",
    sectionSubtitle:
      "ただの当選番号リストじゃ終わらない。予測・検証・トレンドまで、Numbers4好きのための機能を詰め込みました。",
    openPage: "ページを開く",
    cards: [
      {
        href: "/numbers4/result",
        title: "当選番号を一気見せ",
        tag: "公式結果",
        description:
          "過去の抽選を表でサクッと追跡。スマホは横スクロールで全列いける、見やすさガチ勢。",
        accent: "from-violet-500/15 to-transparent",
      },
      {
        href: "/numbers4",
        title: "マルチモデル予測ハブ",
        tag: "アンサンブル",
        description:
          "統計・ML・パターン系など、複数の頭脳をぶち込んだ日次予測を1画面にダッシュボード表示。",
        accent: "from-cyan-500/15 to-transparent",
      },
      {
        href: "/numbers4/stats",
        title: "ボックス順位の統計",
        tag: "検証モード",
        description:
          "「予測リストのどのあたりに当たりがいた？」をモデル別に集計。数字オタク歓喜のビュー。",
        accent: "from-amber-500/15 to-transparent",
      },
      {
        href: "/numbers4/trend",
        title: "Hot Model トレンド",
        tag: "今どれがアツい？",
        description:
          "直近の成績から“いま推しのモデル”を可視化。盛り上がりたい日のお供に。",
        accent: "from-rose-500/15 to-transparent",
      },
    ],
  },
  story: {
    title: "宝くじAI って何者？",
    subtitle: "略して「数字とにらめっこするための、ちゃんとしたWebアプリ」です。",
    p1Lead: "ナンバーズ4の",
    p1Strong1: "公式に近い形の当選情報",
    p1Mid: "を一覧しつつ、リポジトリとDBに載った",
    p1Strong2: "日次予測データ",
    p1Tail:
      "をダッシュボード表示。アンサンブル・手法別・予算プランなど、種類が多いほど比較が楽しくなる構成にしています。",
    p2: "「バズる予感のするUI」と「じっくり数字を追う体験」、両方取りにいきました。SNSでスクショ載せたくなるくらい、見せ方にはこだわってます。",
  },
  disclaimer: {
    title: "ちゃんと言っておくね",
    bodyLead: "予測は",
    bodyStrong: "過去データやモデルに基づく試算",
    bodyTail:
      "であり、当選や的中を保証するものではありません。娯楽・学習・情報整理として楽しんでください。購入を推奨するサービスではありません。",
  },
  blogCard: {
    title: "はじめてでも大丈夫",
    subtitle: "ブログで画面の読み方を解説しています",
  },
  bottomCta: {
    title: "さあ、第1ゲームはナンバーズ4ダッシュボード",
    subtitle: "当選を眺めるだけでも、予測を覗くだけでもOK。あなたの見たい回から飛び込んでみて。",
    primary: "ナンバーズ4ゾーンへ",
    secondary: "当選番号から入る",
  },
};

export const homeLandingCopyEn: HomeLandingCopy = {
  hero: {
    badgeBrand: "Takarakuji AI",
    badgeFocus: "Numbers4-focused",
    titleLine1: "All-in on ",
    titleHighlight: "Numbers4",
    titleLine2: " — draws, predictions, stats, and trends in one dashboard.",
    titleLine3: "",
    titleLineBreakBeforeLine3: false,
    introLead: "Takarakuji AI",
    introMid:
      " is an unofficial hub for Japan’s Numbers4 game: browse draws, compare multiple daily prediction models, and explore performance analytics. ",
    introTail:
      "Most in-app labels are in Japanese — this landing is in English for international visitors.",
    ctaPrimary: "Open the predictions hub",
    ctaSecondary: "Browse winning numbers",
    languageLinks: [
      { href: "/", label: "日本語" },
      { href: "/en", label: "English", current: true },
      { href: "/blog", label: "How-to (JA)" },
      { href: "/faq", label: "FAQ (JA)" },
      { href: "/en/blog", label: "Blog (EN)" },
      { href: "/zh", label: "中文" },
      { href: "/ko", label: "한국어" },
      { href: "/es", label: "Español" },
      { href: "/hi", label: "हिन्दी" },
      { href: "/ar", label: "العربية" },
      { href: "/llms.txt", label: "llms.txt" },
    ],
  },
  pitchLabels: [
    "Multi-model view",
    "Budget-style plans",
    "Mobile-first UI",
    "Match highlights",
    "Stats & trends",
  ],
  features: {
    sectionTitle: "What you can do here",
    sectionSubtitle:
      "More than a plain results list — explore predictions, validation views, and trend analytics built for Numbers4 enthusiasts.",
    openPage: "Open page",
    cards: [
      {
        href: "/numbers4/result",
        title: "Winning numbers at a glance",
        tag: "Results",
        description:
          "Scan past draws in a dense, scannable table — horizontal scroll on mobile so every column stays reachable.",
        accent: "from-violet-500/15 to-transparent",
      },
      {
        href: "/numbers4",
        title: "Multi-model prediction hub",
        tag: "Ensemble",
        description:
          "Daily forecasts from statistics, ML, and pattern-style models on one dashboard-style screen.",
        accent: "from-cyan-500/15 to-transparent",
      },
      {
        href: "/numbers4/stats",
        title: "Box-rank statistics",
        tag: "Validation",
        description:
          "See where hits landed across prediction lists, broken down by model — built for deep number crunching.",
        accent: "from-amber-500/15 to-transparent",
      },
      {
        href: "/numbers4/trend",
        title: "Hot model trends",
        tag: "Momentum",
        description:
          "Spot which models are heating up from recent performance — a fun lens for following the race.",
        accent: "from-rose-500/15 to-transparent",
      },
    ],
  },
  story: {
    title: "What is Takarakuji AI?",
    subtitle: "A focused web app for exploring Numbers4 draws, models, and analytics.",
    p1Lead: "We surface ",
    p1Strong1: "official-style winning-number data",
    p1Mid: " alongside ",
    p1Strong2: "daily prediction datasets",
    p1Tail:
      " from the project’s repository and database — ensembles, methods, and budget-style plans side by side so comparisons stay interesting.",
    p2: "We care about both a polished, shareable UI and a calm, analytical workflow for digging into the digits.",
  },
  disclaimer: {
    title: "Please read this",
    bodyLead: "Predictions are ",
    bodyStrong: "experimental estimates from public history and models",
    bodyTail:
      ". They do not guarantee wins or hits. For entertainment, learning, and organizing information only — not gambling or financial advice.",
  },
  blogCard: {
    title: "New here?",
    subtitle: "The Japanese blog walks through how to read each screen.",
  },
  bottomCta: {
    title: "Start from the Numbers4 dashboard",
    subtitle:
      "Skim results, peek at models, or jump to a specific draw — pick your own entry point.",
    primary: "Go to Numbers4 hub",
    secondary: "Start from results",
  },
};

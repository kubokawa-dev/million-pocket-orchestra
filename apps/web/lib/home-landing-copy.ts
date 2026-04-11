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

/** トップ／フッタ CTA の見た目（ナンバーズ3・4・ロト6で色分け） */
export type HomeLandingHeroCta = {
  href: string;
  label: string;
  lottery: "numbers3" | "numbers4" | "loto6";
  variant: "solid" | "outline";
};

export type HomeLandingCopy = {
  hero: {
    badgeBrand: string;
    badgeFocus: string;
    titleLine1: string;
    titleHighlight: string;
    /** 省略時はサイト共通のバイオレット系グラデを使用 */
    titleHighlightClassName?: string;
    titleLine2: string;
    titleLine3: string;
    titleLineBreakBeforeLine3: boolean;
    introLead: string;
    introMid: string;
    /** Second emphasized phrase (e.g. product positioning); omit for a single-strong intro. */
    introEmphasis?: string;
    introTail: string;
    ctas: readonly HomeLandingHeroCta[];
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
    ctas: readonly HomeLandingHeroCta[];
  };
};

export const homeLandingCopyJa: HomeLandingCopy = {
  hero: {
    badgeBrand: "宝くじAI",
    badgeFocus: "N3 / N4 / Loto6",
    titleLine1: "ナンバーズ3・4・",
    titleHighlight: "ロト6",
    titleHighlightClassName:
      "bg-gradient-to-r from-amber-600 via-orange-500 to-amber-600 bg-clip-text text-transparent dark:from-amber-300 dark:via-orange-400 dark:to-amber-200",
    titleLine2: "の",
    titleLine3: "数字遊び、ここが本気のメインステージ。",
    titleLineBreakBeforeLine3: true,
    introLead: "宝くじAI",
    introMid:
      "は、ナンバーズ3・4の当選閲覧からロト6の等級つき一覧まで、複数AI・統計モデルの予測や成績の見える化をまとめた",
    introEmphasis: "日本の数字系宝くじダッシュボード",
    introTail: "。3桁も4桁も6球も、Xで語れるネタもじっくり検証も、全部アリ。",
    ctas: [
      {
        href: "/numbers4",
        label: "ナンバーズ4 ハブへ",
        lottery: "numbers4",
        variant: "solid",
      },
      {
        href: "/numbers3",
        label: "ナンバーズ3 ハブへ",
        lottery: "numbers3",
        variant: "solid",
      },
      {
        href: "/loto6",
        label: "ロト6 ハブへ",
        lottery: "loto6",
        variant: "solid",
      },
      {
        href: "/numbers4/result",
        label: "ナンバーズ4 当選一覧",
        lottery: "numbers4",
        variant: "outline",
      },
      {
        href: "/numbers3/result",
        label: "ナンバーズ3 当選一覧",
        lottery: "numbers3",
        variant: "outline",
      },
      {
        href: "/loto6/result",
        label: "ロト6 当選一覧",
        lottery: "loto6",
        variant: "outline",
      },
    ],
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
    "3桁・4桁・ロト6",
    "複数モデル同時表示",
    "予算プラン付き",
    "スマホ最適化UI",
    "照合ハイライト",
    "統計・トレンド付き",
  ],
  features: {
    sectionTitle: "このサイトでできること",
    sectionSubtitle:
      "ただの当選番号リストじゃ終わらない。ナンバーズ3・ロト6は等級つきでガッツリ、ナンバーズ4は予測・検証・トレンドまで一気通貫。",
    openPage: "ページを開く",
    cards: [
      {
        href: "/numbers3/result",
        title: "ナンバーズ3 当選を一覧",
        tag: "3桁",
        description:
          "等級別の口数・払戻つきでガッツリ表示。過去データをサクッと追いかけたい人向け。",
        accent: "from-emerald-500/15 to-transparent",
      },
      {
        href: "/numbers3",
        title: "ナンバーズ3 入口",
        tag: "ハブ",
        description:
          "最新回へのショートカットと一覧導線。3桁の予測まわりもここから育てていきます。",
        accent: "from-teal-500/15 to-transparent",
      },
      {
        href: "/numbers4/result",
        title: "ナンバーズ4 当選を一気見せ",
        tag: "4桁",
        description:
          "過去の抽選を表でサクッと追跡。スマホは横スクロールで全列いける、見やすさガチ勢。",
        accent: "from-violet-500/15 to-transparent",
      },
      {
        href: "/numbers4",
        title: "ナンバーズ4 マルチモデル予測",
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
      {
        href: "/loto6/result",
        title: "ロト6 当選を一覧",
        tag: "6球+ボーナス",
        description:
          "本数字・ボーナス・等級別口数・払戻・キャリーオーバーまで表で一気見せ。横スクロールで全列いけるよ。",
        accent: "from-amber-500/18 to-transparent",
      },
      {
        href: "/loto6",
        title: "ロト6 入口",
        tag: "ハブ",
        description:
          "最新回へのショートカットと一覧への導線。ナンバーズと並べて数字チェックしたい人向け。",
        accent: "from-orange-500/15 to-transparent",
      },
      {
        href: "/loto6/stats",
        title: "ロト6 出現回数",
        tag: "統計",
        description:
          "1〜43の本数字・ボーナスの出現回数を窓を変えて一覧。次の予測の肌感チェックにも使えるよ。",
        accent: "from-yellow-500/14 to-transparent",
      },
    ],
  },
  story: {
    title: "宝くじAI って何者？",
    subtitle: "略して「数字とにらめっこするための、ちゃんとしたWebアプリ」です。",
    p1Lead: "ナンバーズ3・4・ロト6の",
    p1Strong1: "公式に近い形の当選情報",
    p1Mid: "を一覧しつつ、サイト側に蓄積した",
    p1Strong2: "日次予測データ",
    p1Tail:
      "をダッシュボード表示（※予測の厚みはナンバーズ4が先行）。アンサンブル・手法別・予算プランなど、種類が多いほど比較が楽しくなる構成にしています。",
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
    title: "さあ、ナンバーズ3・4・ロト6のダッシュボードへ",
    subtitle:
      "3桁・6球は当選データを厚めに、4桁は予測も統計も。眺めるだけでも、覗くだけでもOK。好きな入口からどうぞ。",
    ctas: [
      {
        href: "/numbers4",
        label: "ナンバーズ4 ハブ",
        lottery: "numbers4",
        variant: "solid",
      },
      {
        href: "/numbers3",
        label: "ナンバーズ3 ハブ",
        lottery: "numbers3",
        variant: "solid",
      },
      {
        href: "/loto6",
        label: "ロト6 ハブ",
        lottery: "loto6",
        variant: "solid",
      },
      {
        href: "/numbers4/result",
        label: "ナンバーズ4 当選一覧",
        lottery: "numbers4",
        variant: "outline",
      },
      {
        href: "/numbers3/result",
        label: "ナンバーズ3 当選一覧",
        lottery: "numbers3",
        variant: "outline",
      },
      {
        href: "/loto6/result",
        label: "ロト6 当選一覧",
        lottery: "loto6",
        variant: "outline",
      },
    ],
  },
};

export const homeLandingCopyEn: HomeLandingCopy = {
  hero: {
    badgeBrand: "Takarakuji AI",
    badgeFocus: "N3 / N4 / Loto6",
    titleLine1: "Japan ",
    titleHighlight: "Numbers3, Numbers4 & Loto6",
    titleLine2: " — draws, predictions, stats, and trends in one place.",
    titleLine3: "",
    titleLineBreakBeforeLine3: false,
    introLead: "Takarakuji AI",
    introMid:
      " is an unofficial hub for Japan’s Numbers3, Numbers4, and Loto6: browse draws (tier payouts for Numbers3 and Loto6), compare multiple daily prediction models on Numbers4, and explore performance analytics. ",
    introTail:
      "Most in-app labels are in Japanese — this landing is in English for international visitors.",
    ctas: [
      {
        href: "/numbers4",
        label: "Numbers4 hub",
        lottery: "numbers4",
        variant: "solid",
      },
      {
        href: "/numbers3",
        label: "Numbers3 hub",
        lottery: "numbers3",
        variant: "solid",
      },
      {
        href: "/loto6",
        label: "Loto6 hub",
        lottery: "loto6",
        variant: "solid",
      },
      {
        href: "/numbers4/result",
        label: "Numbers4 results",
        lottery: "numbers4",
        variant: "outline",
      },
      {
        href: "/numbers3/result",
        label: "Numbers3 results",
        lottery: "numbers3",
        variant: "outline",
      },
      {
        href: "/loto6/result",
        label: "Loto6 results",
        lottery: "loto6",
        variant: "outline",
      },
    ],
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
    "3-digit, 4-digit & Loto6",
    "Multi-model view",
    "Budget-style plans",
    "Mobile-first UI",
    "Match highlights",
    "Stats & trends",
  ],
  features: {
    sectionTitle: "What you can do here",
    sectionSubtitle:
      "More than plain lists — Numbers3 and Loto6 with tier payouts, plus Numbers4 predictions, validation views, and trend analytics.",
    openPage: "Open page",
    cards: [
      {
        href: "/numbers3/result",
        title: "Numbers3 results list",
        tag: "3-digit",
        description:
          "Browse past draws with winners and payouts per tier — optimized for quick scanning on mobile.",
        accent: "from-emerald-500/15 to-transparent",
      },
      {
        href: "/numbers3",
        title: "Numbers3 hub",
        tag: "Entry",
        description:
          "Shortcuts to the latest draw and the results index — the home for 3-digit workflows on this site.",
        accent: "from-teal-500/15 to-transparent",
      },
      {
        href: "/numbers4/result",
        title: "Numbers4 results at a glance",
        tag: "4-digit",
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
      {
        href: "/loto6/result",
        title: "Loto6 results list",
        tag: "6+1",
        description:
          "Main numbers, bonus ball, winners and payouts by tier, plus carryover — full-width table with horizontal scroll on mobile.",
        accent: "from-amber-500/18 to-transparent",
      },
      {
        href: "/loto6",
        title: "Loto6 hub",
        tag: "Entry",
        description:
          "Shortcuts to the latest draw and the results index — browse alongside Numbers games in one place.",
        accent: "from-orange-500/15 to-transparent",
      },
      {
        href: "/loto6/stats",
        title: "Loto6 frequency stats",
        tag: "Stats",
        description:
          "Per-ball counts for mains and bonus across a configurable window — handy context before reading predictions.",
        accent: "from-yellow-500/14 to-transparent",
      },
    ],
  },
  story: {
    title: "What is Takarakuji AI?",
    subtitle: "A focused web app for exploring Numbers3/4 draws, Loto6 results, models, and analytics.",
    p1Lead: "We surface ",
    p1Strong1: "official-style winning-number data",
    p1Mid: " for Numbers3, Numbers4, and Loto6 alongside ",
    p1Strong2: "daily prediction datasets",
    p1Tail:
      " (prediction depth is richest on Numbers4 for now) — ensembles, methods, and budget-style plans side by side so comparisons stay interesting.",
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
    title: "Jump into Numbers3, Numbers4, or Loto6",
    subtitle:
      "Browse 3-digit and Loto6 draws with payouts, or dive into 4-digit predictions and analytics — pick your entry point.",
    ctas: [
      {
        href: "/numbers4",
        label: "Numbers4 hub",
        lottery: "numbers4",
        variant: "solid",
      },
      {
        href: "/numbers3",
        label: "Numbers3 hub",
        lottery: "numbers3",
        variant: "solid",
      },
      {
        href: "/loto6",
        label: "Loto6 hub",
        lottery: "loto6",
        variant: "solid",
      },
      {
        href: "/numbers4/result",
        label: "Numbers4 results",
        lottery: "numbers4",
        variant: "outline",
      },
      {
        href: "/numbers3/result",
        label: "Numbers3 results",
        lottery: "numbers3",
        variant: "outline",
      },
      {
        href: "/loto6/result",
        label: "Loto6 results",
        lottery: "loto6",
        variant: "outline",
      },
    ],
  },
};

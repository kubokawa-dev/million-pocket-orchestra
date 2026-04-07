import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "宝くじAI — ナンバーズ4 ダッシュボード",
    short_name: "宝くじAI",
    description:
      "ナンバーズ4の当選番号・予測・統計をまとめた非公式ダッシュボード",
    start_url: "/",
    display: "standalone",
    background_color: "#0f0b1a",
    theme_color: "#7c3aed",
    categories: ["entertainment", "utilities"],
    lang: "ja",
    icons: [
      {
        src: "/opengraph-image",
        sizes: "1200x630",
        type: "image/png",
        purpose: "any",
      },
    ],
  };
}

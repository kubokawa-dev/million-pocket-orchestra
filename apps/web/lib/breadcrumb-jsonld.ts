import { getSiteOrigin } from "@/lib/site";

export type BreadcrumbItem = {
  name: string;
  path: string;
};

/**
 * BreadcrumbList JSON-LD を生成する。
 * 先頭にホームを自動追加するので、items はホーム以降のみ渡す。
 */
export function buildBreadcrumbJsonLd(items: BreadcrumbItem[]) {
  const origin = getSiteOrigin();
  const all: BreadcrumbItem[] = [{ name: "ホーム", path: "" }, ...items];

  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: all.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: item.path === "" ? origin : `${origin}${item.path}`,
    })),
  };
}

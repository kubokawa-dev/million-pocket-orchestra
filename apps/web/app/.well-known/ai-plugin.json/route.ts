import { getSiteOrigin } from "@/lib/site";

export function GET() {
  const origin = getSiteOrigin();

  const plugin = {
    schema_version: "v1",
    name_for_human: "Takarakuji AI (宝くじAI)",
    name_for_model: "takarakuji_ai",
    description_for_human:
      "Unofficial Numbers4 (Japan) dashboard: draw results, multi-model predictions, statistics, and trends.",
    description_for_model:
      "Provides Japan Numbers4 lottery draw results, multi-model daily predictions, box-rank statistics, and model performance trends. Data is unofficial and sourced from public records. Not affiliated with any lottery operator. For research and entertainment only.",
    auth: { type: "none" },
    api: {
      type: "openapi",
      url: `${origin}/api/numbers4/latest`,
      is_user_authenticated: false,
    },
    logo_url: `${origin}/opengraph-image`,
    contact_email: "",
    legal_info_url: `${origin}/faq`,
  };

  return new Response(JSON.stringify(plugin, null, 2), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=86400",
    },
  });
}

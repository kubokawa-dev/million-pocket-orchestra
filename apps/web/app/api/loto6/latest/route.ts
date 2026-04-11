import { NextResponse } from "next/server";

import { resolvePublicSupabaseConfig } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";
import { getSiteOrigin } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function GET() {
  const origin = getSiteOrigin();

  let hasSupabase = false;
  try {
    hasSupabase = resolvePublicSupabaseConfig() !== null;
  } catch {
    // no supabase
  }

  if (!hasSupabase) {
    return NextResponse.json(
      {
        error: "Draw data service unavailable",
        site: origin,
        docs: `${origin}/llms.txt`,
      },
      { status: 503 },
    );
  }

  try {
    const supabase = await createClient();
    const { data: draws, error: drawsError } = await supabase
      .from("loto6_draws")
      .select("*")
      .order("draw_number", { ascending: false })
      .limit(10);

    if (drawsError) {
      return NextResponse.json({ error: drawsError.message }, { status: 500 });
    }

    return NextResponse.json(
      {
        site: "Takarakuji AI (宝くじAI)",
        description:
          "Unofficial Loto6 (Japan) draw results. Not affiliated with any lottery operator.",
        disclaimer:
          "Data is for research and entertainment only. Not financial or gambling advice. Verify with official sources.",
        origin,
        latest_draws: draws ?? [],
        links: {
          home: origin,
          hub: `${origin}/loto6`,
          results: `${origin}/loto6/result`,
          data_sources: `${origin}/data-sources`,
          openapi: `${origin}/api/openapi.json`,
        },
      },
      {
        headers: {
          "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
  } catch {
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}

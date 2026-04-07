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
        error: "Database not available",
        site: origin,
        docs: `${origin}/llms.txt`,
      },
      { status: 503 },
    );
  }

  try {
    const supabase = await createClient();

    // Get latest 10 draws
    const { data: draws, error: drawsError } = await supabase
      .from("numbers4_draws")
      .select("draw_number, draw_date, numbers")
      .order("draw_number", { ascending: false })
      .limit(10);

    if (drawsError) {
      return NextResponse.json({ error: drawsError.message }, { status: 500 });
    }

    return NextResponse.json(
      {
        site: "Takarakuji AI (宝くじAI)",
        description:
          "Unofficial Numbers4 (Japan) dashboard. Not affiliated with any lottery operator.",
        disclaimer:
          "Data is for research and entertainment only. Not financial or gambling advice. Verify with official sources.",
        origin,
        latest_draws: draws ?? [],
        links: {
          home: origin,
          results: `${origin}/numbers4/result`,
          predictions: `${origin}/numbers4`,
          stats: `${origin}/numbers4/stats`,
          trend: `${origin}/numbers4/trend`,
          llms_txt: `${origin}/llms.txt`,
          llms_full_txt: `${origin}/llms-full.txt`,
          feed: `${origin}/feed.xml`,
        },
      },
      {
        headers: {
          "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
  } catch (e) {
    return NextResponse.json(
      { error: "Internal error" },
      { status: 500 },
    );
  }
}

import { NextResponse } from "next/server";

import { getSiteOrigin } from "@/lib/site";

export const dynamic = "force-dynamic";

const DRAW_PATH = /^\/numbers4\/result\/(\d+)\/?$/;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const rawUrl = searchParams.get("url");
  const format = searchParams.get("format") ?? "json";

  if (format !== "json") {
    return NextResponse.json(
      { error: "Only format=json is supported" },
      { status: 400 },
    );
  }

  if (!rawUrl?.trim()) {
    return NextResponse.json({ error: "Missing url parameter" }, { status: 400 });
  }

  const origin = getSiteOrigin();
  let parsed: URL;
  try {
    parsed = new URL(rawUrl);
  } catch {
    return NextResponse.json({ error: "Invalid url" }, { status: 400 });
  }

  if (parsed.origin !== origin) {
    return NextResponse.json({ error: "URL host not allowed" }, { status: 403 });
  }

  const m = parsed.pathname.match(DRAW_PATH);
  if (!m) {
    return NextResponse.json(
      { error: "oEmbed is only available for /numbers4/result/{draw_number}" },
      { status: 404 },
    );
  }

  const draw = m[1];
  const title = `第${draw}回 ナンバーズ4 | 宝くじAI`;

  const body = {
    version: "1.0",
    type: "link" as const,
    provider_name: "Takarakuji AI",
    provider_url: origin,
    title,
    author_name: "Takarakuji AI",
    html: `<a href="${parsed.href}">${title}</a>`,
  };

  return NextResponse.json(body, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

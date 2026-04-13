import { NextResponse } from "next/server";

import { getSiteOrigin } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function GET() {
  const origin = getSiteOrigin();
  const spec = {
    openapi: "3.1.0",
    info: {
      title: "Takarakuji AI — public HTTP API",
      version: "1.0.0",
      description:
        "Unofficial Japan Numbers3 / Numbers4 / Loto6 dashboard. Not affiliated with any lottery operator. Intended for reference, transparency, and machine-readable integration.",
    },
    servers: [{ url: origin }],
    paths: {
      "/api/numbers3/latest": {
        get: {
          summary: "Latest Numbers3 draws snapshot",
          description:
            "Returns recent Numbers3 draw rows and navigation links when the live data backend is configured; useful for AI assistants and external tools that need a latest-results snapshot.",
          responses: {
            "200": {
              description: "JSON payload with latest_draws and navigation links",
              content: {
                "application/json": {
                  schema: { type: "object" },
                },
              },
            },
            "503": { description: "Live draw data not configured" },
          },
        },
      },
      "/api/numbers4/latest": {
        get: {
          summary: "Latest Numbers4 draws snapshot",
          description:
            "Returns recent Numbers4 draw rows and navigation links when the live data backend is configured; useful for AI assistants and external tools that need a latest-results snapshot.",
          responses: {
            "200": {
              description: "JSON payload with latest_draws and navigation links",
              content: {
                "application/json": {
                  schema: { type: "object" },
                },
              },
            },
            "503": { description: "Live draw data not configured" },
          },
        },
      },
      "/api/loto6/latest": {
        get: {
          summary: "Latest Loto6 draws snapshot",
          description:
            "Returns recent Loto6 draw rows and navigation links when the live data backend is configured; useful for AI assistants and external tools that need a latest-results snapshot.",
          responses: {
            "200": {
              description: "JSON payload with latest_draws and navigation links",
              content: {
                "application/json": {
                  schema: { type: "object" },
                },
              },
            },
            "503": { description: "Live draw data not configured" },
          },
        },
      },
      "/api/oembed": {
        get: {
          summary: "oEmbed discovery for draw pages",
          parameters: [
            {
              name: "url",
              in: "query",
              required: true,
              schema: { type: "string", format: "uri" },
              description: `Canonical draw URL under ${origin}`,
            },
            {
              name: "format",
              in: "query",
              schema: { type: "string", enum: ["json"] },
            },
          ],
          responses: {
            "200": {
              description: "oEmbed 1.0 link type",
              content: {
                "application/json": {
                  schema: { type: "object" },
                },
              },
            },
          },
        },
      },
    },
  };

  return NextResponse.json(spec, {
    headers: {
      "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
    },
  });
}

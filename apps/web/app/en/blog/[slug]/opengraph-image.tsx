import { ImageResponse } from "next/og";

import { getEnPostBySlug } from "@/lib/blog/posts-en";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export const dynamic = "force-dynamic";

type ImageProps = {
  params: Promise<{ slug: string }>;
};

function clampText(text: string, maxLength: number) {
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}…` : text;
}

export default async function Image({ params }: ImageProps) {
  const { slug } = await params;
  const post = getEnPostBySlug(slug);

  const title = clampText(post?.title ?? "English guide", 88);
  const description = clampText(
    post?.description ??
      "English guide for international readers using Takarakuji AI as a reference dashboard.",
    160,
  );

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          position: "relative",
          overflow: "hidden",
          background:
            "linear-gradient(135deg, #f6f2e8 0%, #efe5d2 56%, #e5dac3 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(circle at 14% 18%, rgba(182,145,75,0.16) 0%, transparent 24%), radial-gradient(circle at 82% 20%, rgba(29,59,47,0.16) 0%, transparent 26%), radial-gradient(circle at 50% 100%, rgba(182,145,75,0.1) 0%, transparent 36%)",
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 28,
            borderRadius: 36,
            border: "1px solid rgba(182,145,75,0.2)",
            background:
              "linear-gradient(145deg, rgba(255,255,255,0.5), rgba(255,255,255,0.18) 38%, rgba(255,255,255,0.24) 100%)",
            boxShadow: "0 24px 80px rgba(84,68,31,0.12)",
            display: "flex",
          }}
        />

        <div
          style={{
            position: "relative",
            display: "flex",
            width: "100%",
            padding: "56px 64px",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "10px 18px",
                borderRadius: 999,
                border: "1px solid rgba(182,145,75,0.24)",
                background: "rgba(255,250,240,0.68)",
              }}
            >
              <span
                style={{
                  fontSize: 20,
                  letterSpacing: "0.22em",
                  textTransform: "uppercase",
                  color: "#8a6b2f",
                  fontWeight: 700,
                }}
              >
                English Guide
              </span>
            </div>
            <span
              style={{
                fontSize: 18,
                letterSpacing: "0.22em",
                textTransform: "uppercase",
                color: "rgba(75,61,39,0.7)",
              }}
            >
              Takarakuji AI
            </span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 18,
              maxWidth: 960,
            }}
          >
            <span
              style={{
                fontSize: 58,
                lineHeight: 1.08,
                letterSpacing: "-0.04em",
                color: "#21190f",
                fontWeight: 800,
              }}
            >
              {title}
            </span>
            <span
              style={{
                fontSize: 26,
                lineHeight: 1.4,
                color: "#5a4528",
                maxWidth: 860,
              }}
            >
              {description}
            </span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                gap: 12,
              }}
            >
              {["Official verification", "Reference dashboard", "English guide"].map(
                (item) => (
                  <div
                    key={item}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      padding: "10px 16px",
                      borderRadius: 999,
                      border: "1px solid rgba(33,25,15,0.08)",
                      background: "rgba(255,255,255,0.45)",
                      color: "#4d3d27",
                      fontSize: 20,
                    }}
                  >
                    {item}
                  </div>
                ),
              )}
            </div>
            <span
              style={{
                fontSize: 20,
                color: "rgba(75,61,39,0.54)",
                letterSpacing: "0.08em",
              }}
            >
              takarakuji-ai.space/en/blog/{slug}
            </span>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}

import { ImageResponse } from "next/og";

export const alt = "宝くじAI — ナンバーズ4 抽選結果・予測";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0f0b1a 0%, #1a1030 40%, #0c1929 100%)",
          fontFamily: "sans-serif",
        }}
      >
        {/* Decorative circles */}
        <div
          style={{
            position: "absolute",
            top: -80,
            right: -60,
            width: 400,
            height: 400,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%)",
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -100,
            left: -80,
            width: 500,
            height: 500,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%)",
            display: "flex",
          }}
        />

        {/* Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "linear-gradient(90deg, #7c3aed, #06b6d4)",
            borderRadius: 24,
            padding: "8px 24px",
            marginBottom: 24,
          }}
        >
          <span style={{ color: "#fff", fontSize: 22, fontWeight: 700 }}>
            Takarakuji AI
          </span>
        </div>

        {/* Title */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span
            style={{
              fontSize: 64,
              fontWeight: 800,
              color: "#fff",
              letterSpacing: "-0.02em",
              textAlign: "center",
              lineHeight: 1.15,
            }}
          >
            ナンバーズ4
          </span>
          <span
            style={{
              fontSize: 32,
              fontWeight: 500,
              background: "linear-gradient(90deg, #c4b5fd, #67e8f9)",
              backgroundClip: "text",
              color: "transparent",
              textAlign: "center",
            }}
          >
            抽選結果 · AI予測 · 統計
          </span>
        </div>

        {/* URL */}
        <div
          style={{
            position: "absolute",
            bottom: 36,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span
            style={{
              fontSize: 20,
              color: "rgba(255,255,255,0.5)",
              letterSpacing: "0.05em",
            }}
          >
            takarakuji-ai.space
          </span>
        </div>
      </div>
    ),
    { ...size },
  );
}

import { ImageResponse } from "next/og";

export const alt = "宝くじAI — ナンバーズ4 ハブ";
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
          background: "linear-gradient(135deg, #0f0b1a 0%, #1a1030 45%, #0c1929 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "linear-gradient(90deg, #7c3aed, #06b6d4)",
            borderRadius: 24,
            padding: "8px 24px",
            marginBottom: 20,
          }}
        >
          <span style={{ color: "#fff", fontSize: 22, fontWeight: 700 }}>
            宝くじAI · Numbers4 Hub
          </span>
        </div>
        <span
          style={{
            fontSize: 56,
            fontWeight: 800,
            color: "#fff",
            textAlign: "center",
          }}
        >
          ナンバーズ4
        </span>
        <span
          style={{
            marginTop: 12,
            fontSize: 28,
            color: "rgba(196,181,253,0.95)",
            textAlign: "center",
          }}
        >
          予測 · 統計 · トレンド
        </span>
        <span
          style={{
            position: "absolute",
            bottom: 36,
            fontSize: 20,
            color: "rgba(255,255,255,0.45)",
          }}
        >
          takarakuji-ai.space
        </span>
      </div>
    ),
    { ...size },
  );
}

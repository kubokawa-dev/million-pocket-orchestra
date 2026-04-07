import { ImageResponse } from "next/og";

export const alt = "宝くじAI — ナンバーズ4 当選番号一覧";
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
          background: "linear-gradient(135deg, #0c1929 0%, #1e1b4b 50%, #0f172a 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <span
          style={{
            fontSize: 52,
            fontWeight: 800,
            color: "#fff",
            textAlign: "center",
          }}
        >
          当選番号一覧
        </span>
        <span
          style={{
            marginTop: 16,
            fontSize: 30,
            color: "#67e8f9",
            textAlign: "center",
          }}
        >
          Numbers4 · 過去結果
        </span>
        <span
          style={{
            position: "absolute",
            bottom: 36,
            fontSize: 20,
            color: "rgba(255,255,255,0.45)",
          }}
        >
          宝くじAI · takarakuji-ai.space
        </span>
      </div>
    ),
    { ...size },
  );
}

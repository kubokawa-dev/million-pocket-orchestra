import { ImageResponse } from "next/og";

export const alt = "Takarakuji AI — Investor Brief";
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
          position: "relative",
          overflow: "hidden",
          background:
            "linear-gradient(135deg, #090b08 0%, #0d120e 48%, #171d15 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(circle at 18% 18%, rgba(196,153,67,0.28) 0%, transparent 26%), radial-gradient(circle at 82% 22%, rgba(27,92,68,0.32) 0%, transparent 28%), radial-gradient(circle at 50% 100%, rgba(196,153,67,0.14) 0%, transparent 38%)",
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 28,
            borderRadius: 36,
            border: "1px solid rgba(215,181,108,0.24)",
            background:
              "linear-gradient(145deg, rgba(215,181,108,0.08), rgba(255,255,255,0.01) 34%, rgba(255,255,255,0.02) 100%)",
            boxShadow: "0 24px 80px rgba(0,0,0,0.35)",
            display: "flex",
          }}
        />

        <div
          style={{
            position: "relative",
            zIndex: 1,
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
                border: "1px solid rgba(215,181,108,0.28)",
                background: "rgba(255,248,231,0.05)",
              }}
            >
              <span
                style={{
                  fontSize: 20,
                  letterSpacing: "0.22em",
                  textTransform: "uppercase",
                  color: "#d7b56c",
                  fontWeight: 700,
                }}
              >
                Investor Brief
              </span>
            </div>
            <span
              style={{
                fontSize: 18,
                letterSpacing: "0.22em",
                textTransform: "uppercase",
                color: "rgba(231,220,193,0.72)",
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
              maxWidth: 880,
            }}
          >
            <span
              style={{
                fontSize: 72,
                lineHeight: 1.02,
                letterSpacing: "-0.04em",
                color: "#fff8e7",
                fontWeight: 800,
              }}
            >
              Japan-born predictive
              <br />
              entertainment intelligence
            </span>
            <span
              style={{
                fontSize: 28,
                lineHeight: 1.35,
                color: "#d7ccb3",
                maxWidth: 760,
              }}
            >
              Premium narrative for strategic partners, multilingual expansion,
              and data-driven category growth.
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
              {["7 language entries", "3 live product hubs", "OpenAPI + APIs"].map(
                (item) => (
                  <div
                    key={item}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      padding: "10px 16px",
                      borderRadius: 999,
                      border: "1px solid rgba(255,255,255,0.1)",
                      background: "rgba(255,255,255,0.04)",
                      color: "#e7dcc1",
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
                color: "rgba(255,255,255,0.5)",
                letterSpacing: "0.08em",
              }}
            >
              takarakuji-ai.space/investors
            </span>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}

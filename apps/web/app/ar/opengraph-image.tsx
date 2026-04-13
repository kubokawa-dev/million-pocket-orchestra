import { ImageResponse } from "next/og";

export const alt = "Takarakuji AI — Arabic Entry";
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
            "linear-gradient(135deg, #fbf7ef 0%, #f3ead8 56%, #e9dec8 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(circle at 14% 18%, rgba(182,145,75,0.16) 0%, transparent 24%), radial-gradient(circle at 82% 18%, rgba(29,59,47,0.18) 0%, transparent 26%), radial-gradient(circle at 50% 100%, rgba(182,145,75,0.1) 0%, transparent 36%)",
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
              "linear-gradient(145deg, rgba(255,255,255,0.52), rgba(255,255,255,0.16) 38%, rgba(255,255,255,0.22) 100%)",
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
            direction: "rtl",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span
              style={{
                fontSize: 18,
                letterSpacing: "0.12em",
                color: "rgba(75,61,39,0.7)",
              }}
            >
              Takarakuji AI
            </span>
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
                    letterSpacing: "0.08em",
                    color: "#8a6b2f",
                    fontWeight: 700,
                  }}
                >
                  Arabic Entry
                </span>
            </div>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 18,
              maxWidth: 900,
              alignSelf: "flex-end",
            }}
          >
            <span
              style={{
                fontSize: 64,
                lineHeight: 1.08,
                letterSpacing: "-0.03em",
                color: "#21190f",
                fontWeight: 800,
                textAlign: "right",
              }}
            >
              Curated Arabic entry
              <br />
              for strategic visitors
            </span>
            <span
              style={{
                fontSize: 28,
                lineHeight: 1.45,
                color: "#5a4528",
                maxWidth: 760,
                textAlign: "right",
              }}
            >
              A Gulf-friendly narrative layer for international visitors, partner
              introductions, and premium-facing review.
            </span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "space-between",
            }}
          >
            <span
              style={{
                fontSize: 20,
                color: "rgba(75,61,39,0.54)",
                letterSpacing: "0.08em",
                direction: "ltr",
              }}
            >
              takarakuji-ai.space/ar
            </span>
            <div
              style={{
                display: "flex",
                gap: 12,
              }}
            >
              {["Arabic layer", "7 language entries", "Calm tone"].map((item) => (
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
              ))}
            </div>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}

import { ImageResponse } from "next/og";

export const alt = "Takarakuji AI — English Entry";
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
                English Entry
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
              maxWidth: 880,
            }}
          >
            <span
              style={{
                fontSize: 72,
                lineHeight: 1.02,
                letterSpacing: "-0.04em",
                color: "#21190f",
                fontWeight: 800,
              }}
            >
              A multilingual data
              <br />
              and intelligence brand
            </span>
            <span
              style={{
                fontSize: 28,
                lineHeight: 1.35,
                color: "#5a4528",
                maxWidth: 760,
              }}
            >
              International overview for global visitors, launch traffic, and
              strategic introductions.
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
              {["Japan-first", "7 language entries", "Premium-facing"].map((item) => (
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
            <span
              style={{
                fontSize: 20,
                color: "rgba(75,61,39,0.54)",
                letterSpacing: "0.08em",
              }}
            >
              takarakuji-ai.space/en
            </span>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}

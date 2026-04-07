import { ImageResponse } from "next/og";

import { getCachedNumbers4DrawFullRow } from "@/lib/numbers4-predictions/load-6949";

export const alt = "ナンバーズ4 回別ダッシュボード";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export const dynamic = "force-dynamic";

type ImageProps = {
  params: Promise<{ draw_number: string }>;
};

export default async function Image({ params }: ImageProps) {
  const { draw_number: raw } = await params;
  const n = parseInt(raw, 10);
  const row =
    Number.isFinite(n) && n > 0 ? await getCachedNumbers4DrawFullRow(n) : null;
  const nums =
    row?.numbers != null && String(row.numbers).trim() !== ""
      ? String(row.numbers).trim()
      : "当選番号は取り込み後に表示";
  const dateLine =
    row?.draw_date != null && String(row.draw_date).trim() !== ""
      ? `抽選日 ${String(row.draw_date).trim()}`
      : "";

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
          background: "linear-gradient(135deg, #1a1030 0%, #312e81 45%, #0f172a 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <span
          style={{
            fontSize: 36,
            fontWeight: 600,
            color: "rgba(196,181,253,0.9)",
            marginBottom: 8,
          }}
        >
          ナンバーズ4（非公式ダッシュボード）
        </span>
        <span
          style={{
            fontSize: 64,
            fontWeight: 800,
            color: "#fff",
            letterSpacing: "0.02em",
          }}
        >
          第 {Number.isFinite(n) ? n : "—"} 回
        </span>
        <span
          style={{
            marginTop: 24,
            fontSize: 56,
            fontWeight: 700,
            fontFamily: "monospace",
            letterSpacing: "0.35em",
            color: "#fef08a",
          }}
        >
          {nums}
        </span>
        {dateLine ? (
          <span
            style={{
              marginTop: 20,
              fontSize: 26,
              color: "rgba(255,255,255,0.65)",
            }}
          >
            {dateLine}
          </span>
        ) : null}
        <span
          style={{
            position: "absolute",
            bottom: 32,
            fontSize: 20,
            color: "rgba(255,255,255,0.4)",
          }}
        >
          宝くじAI · 公式サイトで必ず照合を
        </span>
      </div>
    ),
    { ...size },
  );
}

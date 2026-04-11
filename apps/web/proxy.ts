import { type NextRequest, NextResponse } from "next/server";

import { updateSession } from "@/lib/supabase/session";

/** 同一 IP あたりのウィンドウ（ミリ秒） */
const WINDOW_MS = 60_000;
/** ウィンドウ内の最大リクエスト数（公開 /api の荒らし対策・ベストエフォート） */
const MAX_REQUESTS = 180;

type Bucket = { resetAt: number; count: number };

const buckets = new Map<string, Bucket>();

function checkRateLimit(key: string): boolean {
  const now = Date.now();
  const b = buckets.get(key);
  if (!b || now >= b.resetAt) {
    buckets.set(key, { resetAt: now + WINDOW_MS, count: 1 });
    return true;
  }
  b.count += 1;
  return b.count <= MAX_REQUESTS;
}

function pruneBuckets(): void {
  if (buckets.size <= 5000) {
    return;
  }
  const now = Date.now();
  for (const [k, b] of buckets) {
    if (now >= b.resetAt) {
      buckets.delete(k);
    }
  }
}

function clientIp(request: NextRequest): string {
  const fwd = request.headers.get("x-forwarded-for");
  if (fwd) {
    const first = fwd.split(",")[0]?.trim();
    if (first) {
      return first;
    }
  }
  return request.headers.get("x-real-ip")?.trim() || "unknown";
}

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  if (path.startsWith("/api/")) {
    pruneBuckets();
    const ip = clientIp(request);
    if (!checkRateLimit(ip)) {
      return NextResponse.json(
        { error: "Too many requests" },
        {
          status: 429,
          headers: { "Retry-After": "60" },
        },
      );
    }
  }
  return await updateSession(request);
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};

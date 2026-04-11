"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

/** v1 キーは年齢のみ。v2 から倫理ページ確認チェックを必須化 */
const STORAGE_KEY = "takarakuji-ai-service-ack-v2";
const LEGACY_STORAGE_KEY = "takarakuji-ai-age-ack-v1";

export function AgeAcknowledgmentBar() {
  const [visible, setVisible] = useState(false);
  const [ethicsChecked, setEthicsChecked] = useState(false);

  useEffect(() => {
    let alive = true;
    void Promise.resolve().then(() => {
      if (!alive || typeof window === "undefined") return;
      try {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        if (stored === "1") {
          setVisible(false);
          return;
        }
        // 以前に年齢のみ同意済み（v1）の端末も、v2 では倫理確認を改めてお願いする
        setVisible(true);
      } catch {
        setVisible(true);
      }
    });
    return () => {
      alive = false;
    };
  }, []);

  if (!visible) return null;

  const acknowledge = () => {
    if (!ethicsChecked) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, "1");
      window.localStorage.removeItem(LEGACY_STORAGE_KEY);
    } catch {
      // ignore quota / private mode
    }
    setVisible(false);
  };

  return (
    <div
      role="dialog"
      aria-labelledby="age-ack-title"
      aria-describedby="age-ack-desc"
      className="border-border/80 bg-background/95 supports-[backdrop-filter]:bg-background/80 fixed inset-x-0 bottom-0 z-[60] border-t shadow-[0_-8px_30px_rgba(0,0,0,0.12)] backdrop-blur-md dark:shadow-[0_-8px_30px_rgba(0,0,0,0.35)]"
    >
      <div className="mx-auto flex max-w-[1600px] flex-col gap-4 px-4 py-4 sm:px-6 sm:py-4">
        <div className="text-muted-foreground space-y-2 text-xs leading-relaxed sm:text-sm">
          <p id="age-ack-title" className="text-foreground text-base font-semibold">
            利用前の確認（倫理的配慮・年齢）
          </p>
          <p id="age-ack-desc">
            本サイトは
            <strong className="text-foreground">日本の宝くじに関する情報の閲覧・整理</strong>
            を目的とした非公式サービスです。表示される試算・統計は
            <strong className="text-foreground">当せんの保証や購入の推奨ではありません。</strong>
            <strong className="text-foreground">18歳未満の方はご利用にならないでください。</strong>
          </p>
        </div>

        <label className="text-foreground flex cursor-pointer items-start gap-3 rounded-lg border border-border/70 bg-muted/25 px-3 py-2.5 text-sm leading-snug">
          <input
            type="checkbox"
            checked={ethicsChecked}
            onChange={(e) => setEthicsChecked(e.target.checked)}
            className="border-border text-foreground mt-0.5 size-4 shrink-0 rounded"
          />
          <span>
            <Link
              href="/responsible-use#ethical"
              className="font-medium underline-offset-4 hover:underline"
            >
              倫理的配慮・健全な利用について
            </Link>
            の要点を読み、18歳以上であり、当サイトの性質（参考情報・自己責任）に同意します。
          </span>
        </label>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <Link
            href="/responsible-use#ethical"
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "w-full justify-center sm:w-auto",
            )}
          >
            ページを開いて読む
          </Link>
          <Button
            type="button"
            size="sm"
            className="w-full sm:w-auto"
            disabled={!ethicsChecked}
            onClick={acknowledge}
          >
            確認のうえ利用を開始する
          </Button>
        </div>
      </div>
    </div>
  );
}

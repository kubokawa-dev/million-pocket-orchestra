"use client";

import { HelpTooltip } from "@/components/ui/help-tooltip";
import { formatContributorSlugLine } from "@/lib/numbers4-predictions/ensemble-contributors";
import { cn } from "@/lib/utils";

const TOOLTIP_CONTENT_BOX =
  "max-w-[min(22rem,calc(100vw-2rem))] [&_.contributor-scroll]:max-h-[min(65vh,18rem)] [&_.contributor-scroll]:overflow-y-auto [&_.contributor-scroll]:overscroll-contain [&_.contributor-scroll]:pr-1";

const triggerClass = cn(
  "text-foreground font-medium tabular-nums underline decoration-dotted decoration-muted-foreground/60 underline-offset-[3px]",
  "hover:text-foreground focus-visible:ring-ring focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none",
);

function ExactContributorTooltip({ exactSlugs }: { exactSlugs: string[] }) {
  const nExact = exactSlugs.length;
  return (
    <HelpTooltip
      side="top"
      align="start"
      delay={50}
      closeDelay={80}
      content={
        <>
          <p className="text-muted-foreground mb-2 text-[0.65rem] leading-snug">
            この4桁の並びと一致したモデル:
          </p>
          <div className="contributor-scroll">
            <ul className="space-y-1.5">
              {exactSlugs.map((slug) => (
                <li
                  key={slug}
                  className="text-foreground leading-snug break-words"
                >
                  {formatContributorSlugLine(slug)}
                </li>
              ))}
            </ul>
          </div>
        </>
      }
      className={cn(triggerClass, "text-muted-foreground hover:text-foreground p-0")}
      contentClassName={TOOLTIP_CONTENT_BOX}
    >
      一致 {nExact}
    </HelpTooltip>
  );
}

function BoxContributorTooltip({ boxOnlySlugs }: { boxOnlySlugs: string[] }) {
  const nBox = boxOnlySlugs.length;
  return (
    <HelpTooltip
      side="top"
      align="start"
      delay={50}
      closeDelay={80}
      content={
        <>
          <p className="text-muted-foreground mb-2 text-[0.65rem] leading-snug">
            桁の並びは異なるが、ボックス（数字の組み合わせ）は同一の候補:
          </p>
          <div className="contributor-scroll">
            <ul className="space-y-1.5">
              {boxOnlySlugs.map((slug) => (
                <li
                  key={slug}
                  className="text-foreground leading-snug break-words"
                >
                  {formatContributorSlugLine(slug)}
                </li>
              ))}
            </ul>
          </div>
        </>
      }
      className={cn(triggerClass, "text-muted-foreground hover:text-foreground p-0")}
      contentClassName={TOOLTIP_CONTENT_BOX}
    >
      ボックス {nBox}
    </HelpTooltip>
  );
}

/**
 * 寄与モデル列: クリック展開なし（テーブル行高の崩れ防止）。ホバー／フォーカスでツールチップのみ。
 */
export function EnsembleContributorCell({
  exactSlugs,
  boxOnlySlugs,
}: {
  exactSlugs: string[];
  boxOnlySlugs: string[];
}) {
  const nExact = exactSlugs.length;
  const nBox = boxOnlySlugs.length;
  if (nExact === 0 && nBox === 0) {
    return (
      <span
        className="text-muted-foreground text-xs tabular-nums"
        title="各モデル直近ラン上位96件に一致する候補がありません（より下位のみの可能性あり）"
      >
        —
      </span>
    );
  }

  return (
    <div className="flex max-w-[13rem] flex-wrap items-baseline gap-x-1 gap-y-0.5 text-xs leading-tight whitespace-nowrap">
      {nExact > 0 ? (
        <ExactContributorTooltip exactSlugs={exactSlugs} />
      ) : null}
      {nExact > 0 && nBox > 0 ? (
        <span className="text-muted-foreground/80 select-none" aria-hidden>
          ·
        </span>
      ) : null}
      {nBox > 0 ? (
        <BoxContributorTooltip boxOnlySlugs={boxOnlySlugs} />
      ) : null}
    </div>
  );
}

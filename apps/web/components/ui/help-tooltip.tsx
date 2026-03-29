"use client";

import type { ReactNode } from "react";
import { Tooltip } from "@base-ui/react/tooltip";
import { cn } from "@/lib/utils";

export function HelpTooltipProvider({
  children,
  delay = 280,
  closeDelay = 80,
}: {
  children: ReactNode;
  delay?: number;
  closeDelay?: number;
}) {
  return (
    <Tooltip.Provider delay={delay} closeDelay={closeDelay}>
      {children}
    </Tooltip.Provider>
  );
}

type HelpTooltipProps = {
  children: ReactNode;
  content: ReactNode;
  side?: "top" | "bottom" | "left" | "right";
  align?: "start" | "center" | "end";
  className?: string;
  /** ポップアップの Tailwind max-width クラス */
  contentClassName?: string;
  delay?: number;
  /** 閉じるまでの待ち（ms）。長い一覧を読むとき少し長めにすると扱いやすいです */
  closeDelay?: number;
};

export function HelpTooltip({
  children,
  content,
  side = "top",
  align = "center",
  className,
  contentClassName = "max-w-[min(22rem,calc(100vw-2rem))]",
  delay,
  closeDelay,
}: HelpTooltipProps) {
  return (
    <Tooltip.Root>
      <Tooltip.Trigger
        type="button"
        delay={delay}
        closeDelay={closeDelay}
        className={cn(
          "text-muted-foreground hover:text-foreground inline-flex cursor-help items-center gap-1 rounded-sm border-0 bg-transparent p-0 font-sans text-inherit underline decoration-dotted decoration-muted-foreground/55 underline-offset-[3px] transition-colors",
          className,
        )}
      >
        {children}
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Positioner
          side={side}
          align={align}
          sideOffset={6}
          className="z-50"
        >
          <Tooltip.Popup
            className={cn(
              "border-border/80 bg-popover text-popover-foreground shadow-lg",
              "rounded-lg border px-3 py-2.5 text-xs leading-relaxed",
              "[&_strong]:text-foreground [&_ul]:mt-1.5 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-4",
              contentClassName,
            )}
          >
            {content}
          </Tooltip.Popup>
        </Tooltip.Positioner>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

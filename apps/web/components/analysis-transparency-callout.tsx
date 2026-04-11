import Link from "next/link";
import { InfoIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type AnalysisTransparencyCalloutProps = {
  title?: string;
  basis: readonly string[];
  limitations: readonly string[];
  sourcesHref?: string;
  sourcesLabel?: string;
  ethicsHref?: string;
  className?: string;
};

/**
 * 分析・試算ブロック付近で「根拠」と「限界」を並べて示すための補助 UI。
 */
export function AnalysisTransparencyCallout({
  title = "この表示の根拠と限界",
  basis,
  limitations,
  sourcesHref = "/data-sources",
  sourcesLabel = "データの出所",
  ethicsHref = "/responsible-use#ethical",
  className,
}: AnalysisTransparencyCalloutProps) {
  return (
    <aside
      className={cn(
        "border-border/70 bg-muted/30 text-muted-foreground rounded-xl border px-4 py-3 text-sm leading-relaxed",
        className,
      )}
    >
      <div className="text-foreground mb-2 flex items-start gap-2 font-medium">
        <InfoIcon className="mt-0.5 size-4 shrink-0 opacity-80" aria-hidden />
        <span>{title}</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 sm:gap-4">
        <div>
          <p className="text-foreground mb-1 text-xs font-semibold tracking-wide">
            根拠（何を見ているか）
          </p>
          <ul className="list-inside list-disc space-y-1 text-xs sm:text-sm">
            {basis.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-foreground mb-1 text-xs font-semibold tracking-wide">
            限界（誤解しやすい点）
          </p>
          <ul className="list-inside list-disc space-y-1 text-xs sm:text-sm">
            {limitations.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      </div>
      <p className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-border/60 pt-3 text-xs">
        <Link
          href={sourcesHref}
          className="text-foreground font-medium underline-offset-4 hover:underline"
        >
          {sourcesLabel}
        </Link>
        <span className="text-border hidden sm:inline" aria-hidden>
          |
        </span>
        <Link
          href={ethicsHref}
          className="text-foreground font-medium underline-offset-4 hover:underline"
        >
          倫理的配慮・健全な利用
        </Link>
      </p>
    </aside>
  );
}

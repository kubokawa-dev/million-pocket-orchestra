import { MarkdownBody } from "@/components/markdown-body";

type Numbers4ReportMarkdownProps = {
  markdown: string;
};

export function Numbers4ReportMarkdown({ markdown }: Numbers4ReportMarkdownProps) {
  return <MarkdownBody markdown={markdown} />;
}

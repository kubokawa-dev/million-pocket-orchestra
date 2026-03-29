import fs from "node:fs/promises";
import path from "node:path";

/**
 * `apps/web` から実行される想定で、リポジトリ直下の `reports/` を解決する。
 * （`npm run dev` の cwd がリポジトリルートの場合も考慮）
 */
function reportsDirectoryCandidates(): string[] {
  return [
    path.join(process.cwd(), "reports"),
    path.join(process.cwd(), "..", "..", "reports"),
  ];
}

function reportFilenames(drawNumber: number): string[] {
  return [`analytics_${drawNumber}.md`, `analysis_${drawNumber}.md`];
}

/**
 * 第 N 回の分析レポート Markdown を読み込む。
 * `reports/analytics_{N}.md` を優先し、無ければ `reports/analysis_{N}.md`。
 */
export async function loadNumbers4ReportMarkdown(
  drawNumber: number,
): Promise<string | null> {
  for (const dir of reportsDirectoryCandidates()) {
    for (const name of reportFilenames(drawNumber)) {
      const full = path.join(dir, name);
      try {
        const stat = await fs.stat(full);
        if (stat.isFile()) {
          return await fs.readFile(full, "utf8");
        }
      } catch {
        /* try next */
      }
    }
  }
  return null;
}

import { redirect } from "next/navigation";

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

/**
 * 旧 URL `/numbers4/{回号}` から新パスへ誘導します。
 */
export default async function LegacyNumbers4DrawRedirect({ params }: PageProps) {
  const { draw_number } = await params;
  redirect(`/numbers4/result/${draw_number}`);
}

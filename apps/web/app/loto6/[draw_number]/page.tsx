import { redirect } from "next/navigation";

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

/** 旧 URL `/loto6/{回号}` から当選結果ページへ誘導します。 */
export default async function LegacyLoto6DrawRedirect({ params }: PageProps) {
  const { draw_number } = await params;
  redirect(`/loto6/result/${draw_number}`);
}

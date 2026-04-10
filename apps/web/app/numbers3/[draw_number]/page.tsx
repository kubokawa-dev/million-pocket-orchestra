import { redirect } from "next/navigation";

type PageProps = {
  params: Promise<{ draw_number: string }>;
};

export default async function LegacyNumbers3DrawRedirect({ params }: PageProps) {
  const { draw_number } = await params;
  redirect(`/numbers3/result/${draw_number}`);
}

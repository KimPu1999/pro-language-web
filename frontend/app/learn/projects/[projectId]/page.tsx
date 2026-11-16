import { redirect } from "next/navigation";

export default async function LearnProjectPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  redirect(`/my-projects/${projectId}`);
}

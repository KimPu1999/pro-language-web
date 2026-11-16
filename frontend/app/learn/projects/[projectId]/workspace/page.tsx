import { redirect } from "next/navigation";

export default async function LearnProjectWorkspacePage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  redirect(`/my-projects/${projectId}`);
}

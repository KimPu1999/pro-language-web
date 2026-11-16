import { redirect } from "next/navigation";

export default async function ProjectSubmissionPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  redirect(`/learn/projects/${projectId}/workspace#submission`);
}

import { notFound } from "next/navigation";
import ProjectDetail from "@/components/project-detail";

const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

async function projectExists(slug: string) {
  const response = await fetch(`${apiBase}/api/v1/projects/${encodeURIComponent(slug)}`, { cache: "no-store" });
  if (response.status === 404) return false;
  if (!response.ok) throw new Error(`Project lookup failed (${response.status}).`);
  return true;
}

export default async function ProjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!await projectExists(slug)) notFound();
  return <ProjectDetail slug={slug} />;
}

import { notFound } from "next/navigation";
import { projectApi } from "@/lib/project-api";
import { ProjectStepReader } from "@/components/project-step-reader";
export default async function ProjectStepPage({ params }: { params: Promise<{ slug: string; stepSlug: string }> }) {
  const { slug, stepSlug } = await params;
  try { const project = await projectApi.detail(slug); const step = project.milestones.find(m => m.slug === stepSlug || `step-${m.position}` === stepSlug); if (!step) notFound(); return <section className="mx-auto max-w-5xl px-5 py-12 lg:px-8"><ProjectStepReader project={project} step={step} /></section>; } catch { notFound(); }
}

import { notFound } from "next/navigation";
import LessonPage from "@/components/lesson-page";

const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

async function lessonExists(slug: string, lessonSlug: string) {
  const response = await fetch(`${apiBase}/api/v1/courses/${encodeURIComponent(slug)}/lessons/${encodeURIComponent(lessonSlug)}`, { cache: "no-store" });
  if (response.status === 404) return false;
  if (!response.ok) throw new Error(`Lesson lookup failed (${response.status}).`);
  return true;
}

export default async function LessonRoute({ params }: { params: Promise<{ slug: string; lessonSlug: string }> }) {
  const { slug, lessonSlug } = await params;
  if (!await lessonExists(slug, lessonSlug)) notFound();
  return <LessonPage slug={slug} lessonSlug={lessonSlug} />;
}

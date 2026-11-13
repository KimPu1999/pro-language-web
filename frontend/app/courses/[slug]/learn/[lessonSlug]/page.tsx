import { redirect } from "next/navigation";

export default async function CourseLessonPage({ params }: { params: Promise<{ slug: string; lessonSlug: string }> }) {
  const { slug, lessonSlug } = await params;
  redirect(`/learn/${slug}/${lessonSlug}`);
}

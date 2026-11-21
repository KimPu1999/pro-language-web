import type { Metadata } from "next";
import CourseDetail from "@/components/course-detail";

type CoursePreview = { title: string; slug: string; description?: string; short_description?: string; seo_title?: string; seo_description?: string; thumbnail?: string | null };
const apiBase = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

async function getCourse(slug: string): Promise<CoursePreview | null> {
  try {
    const response = await fetch(`${apiBase}/api/v1/courses/${encodeURIComponent(slug)}`, { next: { revalidate: 60 } });
    return response.ok ? response.json() : null;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const course = await getCourse(slug);
  if (!course) return { title: "Course not found | Learn-Coding", robots: { index: false, follow: false } };
  const description = course.seo_description || course.short_description || course.description || "Learn with Learn-Coding.";
  return { title: `${course.seo_title || course.title} | Learn-Coding`, description, alternates: { canonical: `/courses/${course.slug}` }, openGraph: { title: course.seo_title || course.title, description, type: "website", images: course.thumbnail ? [{ url: course.thumbnail }] : undefined } };
}

export default async function CoursePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <CourseDetail slug={slug} />;
}

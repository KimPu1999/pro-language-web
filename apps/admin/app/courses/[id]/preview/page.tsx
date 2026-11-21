import { CoursePreview } from "@/components/course-preview";

export default async function AdminCoursePreviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CoursePreview courseId={id} />;
}

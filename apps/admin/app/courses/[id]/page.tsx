import { CourseEditor } from "@/components/course-builder";

export default async function EditCoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CourseEditor courseId={id} />;
}

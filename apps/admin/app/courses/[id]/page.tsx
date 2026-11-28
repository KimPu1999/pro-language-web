import { CourseEditor } from "@/components/course-builder";
import { InlineCurriculumBuilderV2 } from "@/components/inline-curriculum-builder-v2";

export default async function EditCoursePage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams?: Promise<{ section?: string }> }) {
  const { id } = await params;
  const query = searchParams ? await searchParams : {};
  return query.section === "curriculum" ? <InlineCurriculumBuilderV2 courseId={id} /> : <CourseEditor courseId={id} />;
}

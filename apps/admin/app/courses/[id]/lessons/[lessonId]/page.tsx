import { LessonEditor } from "@/components/lesson-editor";

export default async function AdminLessonEditorPage({ params }: { params: Promise<{ id: string; lessonId: string }> }) {
  const { id, lessonId } = await params;
  return <LessonEditor courseId={id} lessonId={lessonId} />;
}

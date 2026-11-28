import { InlineCurriculumBuilderV2 } from "@/components/inline-curriculum-builder-v2";

export default async function CurriculumPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <InlineCurriculumBuilderV2 courseId={id} />;
}

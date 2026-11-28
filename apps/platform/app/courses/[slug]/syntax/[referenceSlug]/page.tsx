import { SyntaxReferenceDetail } from "@/components/syntax-reference-library";

export default async function SyntaxReferencePage({ params }: { params: Promise<{ slug: string; referenceSlug: string }> }) {
  const { slug, referenceSlug } = await params;
  return <SyntaxReferenceDetail courseSlug={slug} referenceSlug={referenceSlug} />;
}

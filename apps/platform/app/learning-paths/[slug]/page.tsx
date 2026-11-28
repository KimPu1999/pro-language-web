import { redirect } from "next/navigation";

// Existing links and bookmarks may still use /learning-paths/:slug.
export default async function LearningPathAlias({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  redirect(`/careers/paths/${encodeURIComponent(slug)}`);
}

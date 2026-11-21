import { ToolDetail } from "@/components/tools-catalog";

export default async function ToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <ToolDetail slug={slug} />;
}

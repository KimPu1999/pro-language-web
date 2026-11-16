import { ToolPage } from "@/components/careers-tools-hub";

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  return <ToolPage slug={(await params).slug} />;
}

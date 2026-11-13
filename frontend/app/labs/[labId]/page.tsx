import { LabDetail } from "@/components/lab-pages";

export default async function Page({ params }: { params: Promise<{ labId: string }> }) {
  const { labId } = await params;
  return <LabDetail id={labId} />;
}

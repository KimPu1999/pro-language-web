import { CloudLabDetail } from "@/components/cloud-lab-pages";
export default async function Page({ params }: { params: Promise<{ labId: string }> }) { return <CloudLabDetail id={(await params).labId} />; }

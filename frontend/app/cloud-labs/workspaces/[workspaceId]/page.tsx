import { CloudWorkspace } from "@/components/cloud-lab-pages";
export default async function Page({ params }: { params: Promise<{ workspaceId: string }> }) { return <CloudWorkspace id={(await params).workspaceId} />; }

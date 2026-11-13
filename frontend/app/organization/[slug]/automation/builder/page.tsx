import { WorkflowBuilder } from "@/components/automation-pages";
export default async function Page({ params }: { params: Promise<{ slug: string }> }) { return <WorkflowBuilder slug={(await params).slug} />; }

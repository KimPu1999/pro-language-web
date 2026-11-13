import { AutomationList } from "@/components/automation-pages";
export default async function Page({ params }: { params: Promise<{ slug: string }> }) { return <AutomationList slug={(await params).slug} kind="usage" />; }

import { AutomationDashboard } from "@/components/automation-pages";
export default async function Page({ params }: { params: Promise<{ slug: string }> }) { return <AutomationDashboard slug={(await params).slug} />; }

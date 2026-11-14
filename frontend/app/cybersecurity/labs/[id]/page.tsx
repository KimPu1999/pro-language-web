import { SecurityLabDetail } from "@/components/cybersecurity-pages";
export default async function Page({ params }: { params: Promise<{ id: string }> }) { return <SecurityLabDetail id={(await params).id} />; }

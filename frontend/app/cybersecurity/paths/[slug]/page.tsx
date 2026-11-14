import { SecurityPathDetail } from "@/components/cybersecurity-pages";
export default async function Page({ params }: { params: Promise<{ slug: string }> }) { return <SecurityPathDetail slug={(await params).slug} />; }

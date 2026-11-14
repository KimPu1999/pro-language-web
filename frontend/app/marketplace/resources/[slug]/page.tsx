import { ResourceDetail } from "@/components/marketplace-pages";
export default async function Page({ params }: { params: Promise<{ slug: string }> }) { return <ResourceDetail slug={(await params).slug}/>; }

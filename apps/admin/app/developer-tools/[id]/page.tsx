import { DeveloperToolEditor } from "@/components/developer-tools-management";

export default async function EditDeveloperToolPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <DeveloperToolEditor id={id} />; }

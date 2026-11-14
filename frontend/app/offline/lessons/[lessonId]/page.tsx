import { OfflineReader } from "@/components/mobile-pages";
export default async function Page({ params }: { params: Promise<{ lessonId: string }> }) { return <section className="mx-auto max-w-7xl px-5 py-10 lg:px-8"><OfflineReader manifestId={(await params).lessonId} /></section>; }

"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { studentSuccessApi } from "@/lib/api";
import { Card, Skeleton } from "@/components/ui";
export default function Page() { const params = useParams<{ ticketId: string }>(); const [data, setData] = useState<any>(null); const [error, setError] = useState(""); useEffect(() => { if (params.ticketId) studentSuccessApi.ticket(params.ticketId).then(setData).catch((e: Error) => setError(e.message)); }, [params.ticketId]); return <section className="mx-auto max-w-4xl space-y-6 px-5 py-12"><p className="text-sm uppercase tracking-[0.18em] text-indigo-300">Student Success</p><h1 className="text-4xl font-bold">Support ticket</h1>{error ? <Card className="p-6 text-rose-300">{error}</Card> : !data ? <Skeleton className="h-48"/> : <Card className="p-6"><pre className="overflow-auto text-sm text-slate-300">{JSON.stringify(data, null, 2)}</pre></Card>}</section>; }

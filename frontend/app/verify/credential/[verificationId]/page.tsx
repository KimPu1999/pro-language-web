"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { assessmentApi } from "@/lib/api";
import { Card, Skeleton } from "@/components/ui";
export default function Page() { const { verificationId } = useParams<{ verificationId: string }>(); const [data, setData] = useState<any>(null); useEffect(() => { if (verificationId) assessmentApi.verify(verificationId).then(setData); }, [verificationId]); return <section className="mx-auto max-w-2xl px-5 py-16"><Card className="p-8 text-center">{!data ? <Skeleton className="h-32"/> : <><p className={data.status === "active" ? "text-emerald-300" : "text-amber-300"}>{data.status}</p><h1 className="mt-4 text-3xl font-bold">Credential verification</h1>{data.status !== "not_found" && <><p className="mt-5 text-xl">{data.title}</p><p className="mt-2 text-slate-400">{data.issuer} · {data.verification_id}</p></>}</>}</Card></section>; }

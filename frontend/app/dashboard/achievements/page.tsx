"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { EyeOff, Sparkles } from "lucide-react";
import { Card, Skeleton } from "@/components/ui";
import { gamificationApi } from "@/lib/ai-api";

type Achievement = { id: string; slug: string; title: string; description: string; threshold: number; earned: boolean; awarded_at?: string | null };

export default function Achievements() {
  const [items, setItems] = useState<Achievement[] | null>(null); const [error, setError] = useState("");
  useEffect(() => { gamificationApi.achievements().then(value => setItems(value.items as Achievement[])).catch(reason => setError(reason instanceof Error ? reason.message : "Unable to load achievements")); }, []);
  return <section className="mx-auto max-w-6xl space-y-6 px-5 py-10"><div><p className="text-sm text-primary">Verified learning rewards</p><h1 className="mt-1 text-3xl font-bold">Achievements</h1><p className="mt-2 text-sm text-slate-400">Badges are awarded from verified platform records, not client-side claims.</p></div>{error && <div role="alert"><Card className="p-5 text-red-300">Unable to load achievements. {error}</Card></div>}{!items && !error && <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><Skeleton className="h-36"/><Skeleton className="h-36"/><Skeleton className="h-36"/></div>}{items && <>{!items.length ? <Card className="p-8 text-center"><Sparkles className="mx-auto text-slate-500"/><h2 className="mt-3 font-semibold">No achievement definitions are published yet</h2><p className="mt-2 text-sm text-slate-400">Verified rewards will appear here when the academy publishes them.</p><Link href="/courses" className="mt-4 inline-block text-sm text-primary">Continue learning →</Link></Card> : <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{items.map(item => <Card className={`p-5 ${item.earned ? "border-emerald-400/30" : "opacity-75"}`} key={item.id}><div className="flex items-start justify-between"><span className={`grid h-11 w-11 place-items-center rounded-xl ${item.earned ? "bg-emerald-500/15 text-emerald-300" : "bg-slate-500/15 text-slate-500"}`}>{item.earned ? <Sparkles size={21}/> : <EyeOff size={19}/>}</span><span className={`text-xs ${item.earned ? "text-emerald-300" : "text-slate-500"}`}>{item.earned ? "Earned" : "Locked"}</span></div><h2 className="mt-5 font-semibold">{item.title}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{item.description}</p>{item.earned && item.awarded_at && <p className="mt-4 text-xs text-slate-500">Awarded {new Date(item.awarded_at).toLocaleDateString()}</p>}</Card>)}</div>}</>}</section>;
}

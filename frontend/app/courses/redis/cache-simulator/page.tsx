"use client";

import Link from "next/link";
import { RefreshCw } from "lucide-react";
import { useState } from "react";

export default function RedisCacheSimulatorPage() {
  const [cache, setCache] = useState<Record<string, string>>({});
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const read = (key: string) => { if (cache[key]) setHits(value => value + 1); else { setMisses(value => value + 1); setCache(value => ({ ...value, [key]: "Course payload from PostgreSQL" })); } };
  const reset = () => { setCache({}); setHits(0); setMisses(0); };
  const total = hits + misses;
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/redis" className="text-sm text-slate-300 hover:text-white">← Back to Redis</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">Cache simulator</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">See cache-aside behavior</h1><p className="mt-4 text-lg leading-8 text-slate-400">Trigger deterministic hits, misses, database fallbacks, and invalidation in an in-memory simulation.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[1fr_320px]"><div className="rounded-2xl border border-line bg-surface p-6"><div className="flex items-center justify-between"><h2 className="font-semibold">Course detail request</h2><button onClick={reset} className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div><p className="mt-3 text-sm text-slate-400">Read `course:42` from Redis. A miss loads the synthetic authoritative database response and populates cache.</p><button onClick={() => read("course:42")} className="mt-6 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500">Request course 42</button><div className="mt-6 rounded-xl bg-ink p-4"><p className="text-xs uppercase tracking-wider text-slate-500">Cache state</p>{Object.entries(cache).map(([key, value]) => <p key={key} className="mt-2 text-sm text-emerald-300">{key}: {value}</p>)}{!Object.keys(cache).length && <p className="mt-2 text-sm text-slate-500">Empty — the next request is a miss.</p>}</div></div><aside className="rounded-2xl border border-red-400/20 bg-red-500/10 p-6"><p className="text-xs uppercase tracking-wider text-red-300">Metrics</p><p className="mt-4 text-3xl font-bold">{total ? Math.round((hits / total) * 100) : 0}%</p><p className="text-sm text-slate-400">hit rate</p><div className="mt-5 space-y-2 text-sm"><p className="text-emerald-300">Hits: {hits}</p><p className="text-amber-300">Misses: {misses}</p></div><p className="mt-6 text-xs leading-5 text-slate-400">This is not a real Redis benchmark. Production metrics need instrumented infrastructure and controlled load tests.</p></aside></div></section>;
}

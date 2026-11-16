"use client";

import Link from "next/link";
import { RefreshCw } from "lucide-react";
import { useState } from "react";

export default function RedisStreamsLabPage() {
  const [events, setEvents] = useState<string[]>([]);
  const [pending, setPending] = useState<string[]>([]);
  const add = () => setEvents(current => [...current, `event-${current.length + 1} · lesson.completed`]);
  const read = () => setPending(events.filter(event => !pending.includes(event)));
  const ack = () => setPending([]);
  const reset = () => { setEvents([]); setPending([]); };
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/redis" className="text-sm text-slate-300 hover:text-white">← Back to Redis</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">Streams lab</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Explore consumer groups</h1><p className="mt-4 text-lg leading-8 text-slate-400">Simulate XADD, XREADGROUP, pending messages, and acknowledgement without a real Redis connection.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-2"><div className="rounded-2xl border border-line bg-surface p-6"><div className="flex justify-between"><h2 className="font-semibold">Stream: academy-events</h2><button onClick={reset} className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div><div className="mt-5 space-y-2">{events.map(event => <p key={event} className="rounded-lg bg-ink p-3 font-mono text-sm text-red-200">{event}</p>)}{!events.length && <p className="text-sm text-slate-500">No stream entries.</p>}</div><div className="mt-6 flex flex-wrap gap-2"><button onClick={add} className="rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white">XADD event</button><button onClick={read} disabled={!events.length} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-300 disabled:opacity-50">XREADGROUP</button><button onClick={ack} disabled={!pending.length} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-300 disabled:opacity-50">XACK pending</button></div></div><aside className="rounded-2xl border border-red-400/20 bg-red-500/10 p-6"><p className="text-xs uppercase tracking-wider text-red-300">Consumer: worker-1</p><p className="mt-4 text-3xl font-bold">{pending.length}</p><p className="text-sm text-slate-400">pending messages</p><div className="mt-5 space-y-2">{pending.map(event => <p key={event} className="rounded-lg bg-ink/70 p-3 text-sm text-amber-200">{event}</p>)}{!pending.length && <p className="text-sm text-slate-500">Nothing pending.</p>}</div><p className="mt-6 text-xs leading-5 text-slate-300">Streams provide a durable event-log model, but delivery, retries, idempotency, and recovery still need explicit application design.</p></aside></div></section>;
}

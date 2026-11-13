"use client";

import { useEffect, useState } from "react";

type Check = { name: string; status: string; detail: string };

export default function OperationsPage() {
  const [checks, setChecks] = useState<Check[]>([]);
  const [message, setMessage] = useState("Loading observed service status…");
  const load = () => { setMessage("Loading observed service status…"); fetch("/api/v1/platform/quality", { credentials: "include" }).then(async (response) => { if (!response.ok) throw new Error(`Operations status unavailable (${response.status})`); return response.json(); }).then((data) => { setChecks(data.checks ?? []); setMessage(""); }).catch((error: Error) => setMessage(error.message)); };
  useEffect(load, []);
  return <section className="space-y-8"><div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Operations</p><h1 className="mt-2 text-3xl font-bold">Service status</h1><p className="mt-2 text-slate-400">Only observed checks are shown. Missing provider integrations remain clearly marked.</p></div><button type="button" onClick={load} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white">Refresh status</button>{message && <p role="status" className="text-sm text-slate-400">{message}</p>}<div className="grid gap-4 md:grid-cols-2">{checks.map((check) => <article className="rounded-2xl border border-line bg-surface p-5" key={check.name}><div className="flex items-center justify-between gap-3"><h2 className="font-semibold capitalize">{check.name.replaceAll("_", " ")}</h2><span className="rounded-full bg-elevated px-3 py-1 text-xs uppercase text-slate-300">{check.status.replaceAll("_", " ")}</span></div><p className="mt-3 text-sm leading-6 text-slate-400">{check.detail}</p></article>)}</div></section>;
}

"use client";

import { useEffect, useState } from "react";

type Check = { name: string; status: string; detail: string };

export default function QualityPage() {
  const [checks, setChecks] = useState<Check[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("/api/v1/platform/quality", { credentials: "include" })
      .then(async (response) => { if (!response.ok) throw new Error("Quality status is unavailable."); return response.json(); })
      .then((data) => setChecks(data.checks ?? []))
      .catch((reason: Error) => setError(reason.message));
  }, []);
  return <section className="space-y-8">
    <div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Operations</p><h1 className="mt-2 text-3xl font-bold">Platform quality</h1><p className="mt-2 max-w-2xl text-slate-400">Observed dependency and configuration status. Unconfigured services are shown explicitly and are never presented as healthy.</p></div>
    {error ? <div role="alert" className="rounded-xl border border-red-400/20 bg-red-400/10 p-5 text-red-200">{error}</div> : <div className="grid gap-4 md:grid-cols-2">{checks.map((check) => <article className="rounded-2xl border border-line bg-surface p-5" key={check.name}><div className="flex items-center justify-between gap-3"><h2 className="font-semibold capitalize">{check.name.replaceAll("_", " ")}</h2><span className="rounded-full bg-elevated px-3 py-1 text-xs uppercase tracking-wider text-slate-300">{check.status.replaceAll("_", " ")}</span></div><p className="mt-3 text-sm leading-6 text-slate-400">{check.detail}</p></article>)}</div>}
    {!checks.length && !error && <div className="rounded-xl border border-line bg-surface p-6 text-slate-400">Loading quality status…</div>}
  </section>;
}

"use client";

import { useMemo, useState } from "react";

const LABS = [
  ["CIA triad risk review", "Beginner", "Synthetic service scenario", "30 min"],
  ["Password hashing and verification", "Beginner", "Local Python example", "45 min"],
  ["Security log redaction", "Beginner", "Synthetic log file", "45 min"],
  ["Network segmentation review", "Intermediate", "Owned diagram only", "60 min"],
  ["Secure API authorization review", "Intermediate", "Local sample API", "60 min"],
  ["SOC alert triage simulation", "Advanced", "Synthetic alerts", "75 min"],
];

export function CybersecurityLabCatalog() {
  const [query, setQuery] = useState("");
  const [difficulty, setDifficulty] = useState("All");
  const labs = useMemo(() => LABS.filter(([title, level, environment]) => (difficulty === "All" || level === difficulty) && `${title} ${environment}`.toLowerCase().includes(query.toLowerCase())), [difficulty, query]);
  return <main className="min-h-screen bg-[#0B1020] p-4 text-slate-100 sm:p-8"><div className="mx-auto max-w-6xl"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">Defensive security labs</p><h1 className="mt-2 text-3xl font-bold">Practice only in authorized environments</h1><p className="mt-3 max-w-3xl text-slate-400">Labs use synthetic data, local owned systems, or explicit simulations. Do not scan public systems, collect real credentials, execute malware, or run untrusted code on the application host.</p><div className="mt-6 flex flex-col gap-3 sm:flex-row"><input aria-label="Search cybersecurity labs" className="flex-1 rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" placeholder="Search defensive labs" value={query} onChange={event => setQuery(event.target.value)} /><select aria-label="Filter lab difficulty" className="rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" value={difficulty} onChange={event => setDifficulty(event.target.value)}><option>All</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div><div className="mt-6 grid gap-4 md:grid-cols-2">{labs.map(([title, level, environment, duration]) => <article key={title} className="rounded-2xl border border-emerald-400/20 bg-[#131F36] p-5"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold">{title}</h2><span className="rounded-full bg-emerald-400/10 px-2 py-1 text-xs text-emerald-200">{level}</span></div><p className="mt-4 text-sm text-slate-300">Environment: {environment} · {duration}</p><ol className="mt-4 list-decimal space-y-1 pl-5 text-sm text-slate-400"><li>Confirm ownership or written authorization.</li><li>Use synthetic data and follow the documented steps.</li><li>Verify the defensive result, redact evidence, and clean up.</li></ol><div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-100">Ethical boundary: stop if scope is unclear. Never paste credentials or target systems you do not own.</div></article>)}{labs.length === 0 && <p className="rounded-xl border border-white/10 p-6 text-slate-400">No labs match those filters.</p>}</div></div></main>;
}

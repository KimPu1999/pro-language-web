"use client";

import { useMemo, useState } from "react";

const LABS = [
  ["First CI workflow review", "Beginner", "GitHub Actions", "30 min", "Read-only YAML"],
  ["Git branching and protected releases", "Beginner", "Git, GitHub", "45 min", "Local repository"],
  ["Docker build and image scan", "Intermediate", "Docker, registry", "60 min", "Local container review"],
  ["Multi-environment promotion", "Intermediate", "CI/CD, approvals", "60 min", "Pipeline simulation"],
  ["Terraform plan gate", "Advanced", "Terraform, IaC", "75 min", "Plan-only example"],
  ["Kubernetes rollback drill", "Advanced", "Kubernetes, Helm", "75 min", "Manifest simulation"],
];

export function CICDLabCatalog() {
  const [query, setQuery] = useState("");
  const [difficulty, setDifficulty] = useState("All");
  const labs = useMemo(() => LABS.filter(([title, level, tools]) => (difficulty === "All" || level === difficulty) && `${title} ${tools}`.toLowerCase().includes(query.toLowerCase())), [difficulty, query]);
  return <main className="min-h-screen bg-[#0B1020] p-4 text-slate-100 sm:p-8"><div className="mx-auto max-w-6xl"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">CI/CD labs</p><h1 className="mt-2 text-3xl font-bold">Practice delivery safely</h1><p className="mt-3 max-w-3xl text-slate-400">Labs are local, simulated, or read-only. The platform never runs learner scripts, accesses cloud accounts, stores CI secrets, or creates external resources.</p><div className="mt-6 flex flex-col gap-3 sm:flex-row"><input aria-label="Search CI/CD labs" className="flex-1 rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" placeholder="Search labs" value={query} onChange={event => setQuery(event.target.value)} /><select aria-label="Filter lab difficulty" className="rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" value={difficulty} onChange={event => setDifficulty(event.target.value)}><option>All</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div><div className="mt-6 grid gap-4 md:grid-cols-2">{labs.map(([title, level, tools, duration, mode]) => <article key={title} className="rounded-2xl border border-blue-400/20 bg-[#131F36] p-5"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold">{title}</h2><span className="rounded-full bg-blue-400/10 px-2 py-1 text-xs text-blue-200">{level}</span></div><p className="mt-4 text-sm text-slate-300">Tools: {tools} · {duration} · {mode}</p><ol className="mt-4 list-decimal space-y-1 pl-5 text-sm text-slate-400"><li>Read the objective and inspect the example configuration.</li><li>Trace a success and failure path without executing it here.</li><li>Record verification, security, rollback, and cleanup steps.</li></ol><div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-100">Do not paste credentials into the platform. Hosted runners, registries, and cloud services may incur costs.</div></article>)}{labs.length === 0 && <p className="rounded-xl border border-white/10 p-6 text-slate-400">No labs match those filters.</p>}</div></div></main>;
}

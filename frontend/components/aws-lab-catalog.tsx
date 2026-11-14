"use client";

import { useMemo, useState } from "react";

const LABS = [
  ["Billing budget and cost guardrails", "Beginner", "Budgets, billing", "30 min", "Simulated checklist"],
  ["IAM least-privilege review", "Beginner", "IAM", "45 min", "Read-only policy review"],
  ["S3 static website design", "Beginner", "S3, CloudFront", "60 min", "Diagram and local files"],
  ["VPC route inspection", "Intermediate", "VPC", "60 min", "Read-only route exercise"],
  ["CloudWatch observability plan", "Intermediate", "CloudWatch", "45 min", "Dashboard design"],
  ["Infrastructure change-set review", "Advanced", "CloudFormation", "75 min", "Template review; no deploy"],
];

export function AWSLabCatalog() {
  const [query, setQuery] = useState("");
  const [difficulty, setDifficulty] = useState("All");
  const labs = useMemo(() => LABS.filter(([title, level, services]) => (difficulty === "All" || level === difficulty) && `${title} ${services}`.toLowerCase().includes(query.toLowerCase())), [difficulty, query]);
  return <main className="min-h-screen bg-[#0B1020] p-4 text-slate-100 sm:p-8"><div className="mx-auto max-w-6xl"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-orange-300">AWS hands-on labs</p><h1 className="mt-2 text-3xl font-bold">Practice without provisioning cloud resources</h1><p className="mt-3 max-w-3xl text-slate-400">These labs use simulations, diagrams, and local review. Never paste AWS access keys into the platform. If you independently run a command in your account, verify pricing, permissions, and cleanup first.</p><div className="mt-6 flex flex-col gap-3 sm:flex-row"><label className="flex-1"><span className="sr-only">Search labs</span><input className="w-full rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" placeholder="Search labs" value={query} onChange={event => setQuery(event.target.value)} /></label><select className="rounded-lg border border-white/10 bg-[#131F36] px-3 py-2" value={difficulty} onChange={event => setDifficulty(event.target.value)}><option>All</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div><div className="mt-6 grid gap-4 md:grid-cols-2">{labs.map(([title, level, services, duration, mode]) => <article key={title} className="rounded-2xl border border-orange-400/20 bg-[#131F36] p-5"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold">{title}</h2><span className="rounded-full bg-orange-400/10 px-2 py-1 text-xs text-orange-200">{level}</span></div><dl className="mt-4 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-slate-500">Services</dt><dd className="mt-1 text-slate-300">{services}</dd></div><div><dt className="text-slate-500">Duration</dt><dd className="mt-1 text-slate-300">{duration}</dd></div></dl><p className="mt-4 text-sm text-slate-400">Mode: {mode}. Required access is limited to documentation or local simulation; no platform action is performed.</p><ol className="mt-4 list-decimal space-y-1 pl-5 text-sm text-slate-300"><li>Read the objective and cost warning.</li><li>Inspect the architecture or sample policy.</li><li>Record verification and cleanup steps.</li></ol><div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-100">AWS usage may incur charges. Check current regional pricing and never assume Free Tier means zero cost.</div></article>)}{labs.length === 0 && <p className="rounded-xl border border-white/10 p-6 text-slate-400">No labs match those filters.</p>}</div></div></main>;
}

"use client";
import { useEffect, useState } from "react";
import { aiApi } from "@/lib/ai-api";

const tabs = ["Overview", "Provider Settings", "Model Policies", "Usage Analytics", "Quotas", "Safety", "Audit Logs"];

export default function AdminAIPage() {
  const [tab, setTab] = useState("Overview");
  const [settings, setSettings] = useState<any>(null);
  const [usage, setUsage] = useState<any>(null);
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([aiApi.adminSettings(), aiApi.adminUsage()]).then(([a, b]) => { setSettings(a); setUsage(b); }).catch((e) => setError(e.message)); }, []);
  return <div className="space-y-6">
    <div><p className="text-sm text-primary">Operations</p><h1 className="mt-1 text-3xl font-bold">AI Control Center</h1><p className="mt-2 text-slate-400">Manage availability, policies and operational usage without exposing provider secrets.</p></div>
    <div className="flex flex-wrap gap-2 rounded-xl border border-line bg-surface p-2">{tabs.map((item) => <button key={item} onClick={() => setTab(item)} className={`rounded-lg px-3 py-2 text-sm ${tab === item ? "bg-primary text-white" : "text-slate-400 hover:bg-elevated hover:text-white"}`}>{item}</button>)}</div>
    {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>}
    <section className="grid gap-4 md:grid-cols-3"><div className="rounded-xl border border-line bg-surface p-5"><p className="text-sm text-slate-400">Provider</p><p className="mt-2 text-xl font-semibold">{settings?.provider ?? "Loading…"}</p></div><div className="rounded-xl border border-line bg-surface p-5"><p className="text-sm text-slate-400">Model</p><p className="mt-2 text-xl font-semibold">{settings?.model ?? "Loading…"}</p></div><div className="rounded-xl border border-line bg-surface p-5"><p className="text-sm text-slate-400">Requests recorded</p><p className="mt-2 text-xl font-semibold">{usage?.requests ?? "Loading…"}</p></div></section>
    <section className="rounded-xl border border-line bg-surface p-6"><h2 className="text-lg font-semibold">{tab}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{settings?.enabled ? "The configured provider is enabled for server-side requests." : "AI is currently disabled. No live provider requests are made and no fabricated responses are shown."}</p><p className="mt-4 text-sm text-slate-500">Provider credentials remain server-side and are never returned by this control center.</p></section>
  </div>;
}

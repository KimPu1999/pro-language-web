"use client";
import { useEffect, useState } from "react";
import { Card, EmptyState, Skeleton } from "@/components/ui";

type Check = { name: string; status: string; detail: string };
async function readJson(path: string) { const response = await fetch(path, { credentials: "include" }); if (!response.ok) throw new Error(`Request failed (${response.status})`); return response.json(); }
export function SystemHealthPage() {
  const [checks, setChecks] = useState<Check[]>([]), [error, setError] = useState(""), [loading, setLoading] = useState(true);
  const load = () => { setLoading(true); setError(""); Promise.all([readJson("/api/v1/health"), readJson("/api/v1/ready"), readJson("/api/v1/platform/quality")]).then(([health, ready, quality]) => setChecks([{name:"FastAPI",status:health.status,detail:"Liveness endpoint responded successfully."},{name:"PostgreSQL",status:ready.database,detail:"Readiness endpoint verified database connectivity."},...(quality.checks??[])] as Check[])).catch((e:Error)=>setError(e.message)).finally(()=>setLoading(false)); };
  useEffect(load, []);
  return <section className="space-y-7"><div><p className="text-sm text-indigo-300">Operations</p><h1 className="mt-2 text-3xl font-bold">System health</h1><p className="mt-2 text-sm text-slate-400">Only live liveness, readiness, and configured dependency checks are shown.</p></div><button onClick={load} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold">Refresh checks</button>{error&&<Card className="p-5 text-red-300">{error}</Card>}{loading?<div className="grid gap-4 md:grid-cols-2">{[1,2,3,4].map(x=><Skeleton key={x} className="h-32"/>)}</div>:<div className="grid gap-4 md:grid-cols-2">{checks.map(check=><Card className="p-5" key={check.name}><div className="flex items-center justify-between gap-3"><h2 className="font-semibold capitalize">{check.name.replaceAll("_"," ")}</h2><span className="rounded-full bg-elevated px-3 py-1 text-xs uppercase text-slate-300">{check.status.replaceAll("_"," ")}</span></div><p className="mt-3 text-sm leading-6 text-slate-400">{check.detail}</p></Card>)}</div>}</section>;
}
export function AdminPlaceholder({ title, eyebrow, description, detail }: { title: string; eyebrow: string; description: string; detail: string }) {
  return <section className="space-y-7"><div><p className="text-sm text-indigo-300">{eyebrow}</p><h1 className="mt-2 text-3xl font-bold">{title}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{description}</p></div><Card className="p-7"><EmptyState title="Not configured in this repository" description={detail}/></Card></section>;
}
export function PlatformSecurityPage(){return <AdminPlaceholder eyebrow="Security" title="Security center" description="Role and access controls remain server-authorized. This surface does not expose credentials or secrets." detail="Platform role assignments, audit history, and security events require the dedicated platform security data source; no fake status is shown."/>;}
export function PlatformNotificationsPage(){return <AdminPlaceholder eyebrow="Communications" title="Notifications" description="Review announcements, templates, delivery evidence, and failed delivery retries." detail="No platform notification-delivery tables or provider endpoint are currently connected, so delivery is not claimed."/>;}
export function PlatformMediaPage(){return <AdminPlaceholder eyebrow="Assets" title="Media library" description="Manage validated platform assets and resource links." detail="No safe upload storage provider is configured in this repository. Upload controls remain unavailable."/>;}
export function PlatformSettingsPage(){return <AdminPlaceholder eyebrow="Configuration" title="Platform settings" description="Manage branding, languages, SEO defaults, registration, and security preferences." detail="Settings persistence is not implemented in the current schema. Secret values are not exposed."/>;}


"use client";

import { useEffect, useState } from "react";
import { operationsApi } from "@/lib/api";
import { Button, Card, EmptyState, Skeleton } from "@/components/ui";

function useLoad<T>(loader: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null); const [error, setError] = useState("");
  useEffect(() => { loader().then(setData).catch((e: Error) => setError(e.message)); }, [loader]);
  return { data, error };
}

function ConsoleList({ title, description, loader, fields = ["title", "status"] }: { title: string; description: string; loader: () => Promise<any>; fields?: string[] }) {
  const { data, error } = useLoad(loader); const rows = Array.isArray(data) ? data : data?.items ?? data?.checks ?? [];
  return <section className="space-y-6"><div><p className="text-sm uppercase tracking-[0.2em] text-indigo-300">Platform operations</p><h1 className="mt-2 text-3xl font-bold">{title}</h1><p className="mt-2 text-slate-400">{description}</p></div>{error ? <Card className="p-5 text-rose-300">{error}</Card> : !data ? <Skeleton className="h-48" /> : rows.length ? <div className="grid gap-4 md:grid-cols-2">{rows.map((row: any, index: number) => <Card className="p-5" key={row.id ?? row.name ?? index}>{fields.map((field) => <p className="mt-1 text-sm text-slate-300 first:mt-0" key={field}><span className="text-slate-500">{field.replaceAll("_", " ")}: </span>{String(row[field] ?? "—")}</p>)}</Card>)}</div> : <EmptyState title="No recorded data" description="This view does not fabricate operational history. It will populate when an authenticated producer records evidence." />}</section>;
}

export function OperationsDashboard() { return <ConsoleList title="Operations dashboard" description="Observed service and incident data only; missing telemetry is shown as unavailable." loader={operationsApi.monitoring} fields={["service", "status", "latency_ms", "detail"]} />; }
export function MonitoringPage() { return <ConsoleList title="Service monitoring" description="Persisted health checks from authenticated probes. External telemetry is not inferred." loader={operationsApi.monitoring} fields={["service", "status", "latency_ms", "detail"]} />; }
export function IncidentsPage() { return <ConsoleList title="Incident management" description="Incident lifecycle and timeline records from platform operations." loader={operationsApi.incidents} fields={["title", "severity", "status", "created_at"]} />; }
export function ImprovementsPage() { return <ConsoleList title="Product improvements" description="Human-owned backlog items linked to operational evidence." loader={operationsApi.improvements} fields={["title", "priority", "status", "target_release"]} />; }
export function ReleasesPage() { return <ConsoleList title="Release management" description="Release records and approval state. Deployment success is never inferred." loader={operationsApi.releases} fields={["version", "environment", "status", "created_at"]} />; }
export function FlagsPage() { return <ConsoleList title="Feature flags" description="Server-controlled flags with explicit rollout state." loader={operationsApi.flags} fields={["key", "enabled", "rollout_percent", "description"]} />; }
export function MaintenancePage() { return <ConsoleList title="Maintenance" description="Scheduled notices and service windows." loader={operationsApi.maintenance} fields={["title", "starts_at", "ends_at", "status"]} />; }
export function BackupsPage() { return <ConsoleList title="Backup monitoring" description="Backup records are separate from restore-drill evidence." loader={operationsApi.backups} fields={["readiness"]} />; }
export function PerformancePage() { return <ConsoleList title="Performance monitoring" description="Performance metrics require an OpenTelemetry or Prometheus producer; no values are invented here." loader={operationsApi.monitoring} fields={["telemetry", "source"]} />; }

export function FeedbackForm({ bug = false }: { bug?: boolean }) {
  const [body, setBody] = useState({ title: "", body: "", category: "general", description: "", affected_page: "", reproduction_steps: "", expected_result: "", actual_result: "" }); const [message, setMessage] = useState("");
  const submit = async (event: React.FormEvent) => { event.preventDefault(); const csrf = document.cookie.split(";").find((x) => x.trim().startsWith("cm_csrf="))?.split("=")[1] ?? ""; try { await (bug ? operationsApi.bugs(body, csrf) : operationsApi.feedback(body, csrf)); setMessage("Submitted successfully."); } catch (e) { setMessage((e as Error).message); } };
  return <section className="mx-auto max-w-2xl space-y-6"><div><p className="text-sm uppercase tracking-[0.2em] text-indigo-300">Student support</p><h1 className="mt-2 text-3xl font-bold">{bug ? "Report a bug" : "Share feedback"}</h1><p className="mt-2 text-slate-400">Please do not include passwords, access tokens, private code, or sensitive personal data.</p></div><form onSubmit={submit} className="space-y-4"><input required aria-label="Title" value={body.title} onChange={(e) => setBody({ ...body, title: e.target.value })} placeholder="Title" className="w-full rounded-xl border border-line bg-surface px-4 py-3" /><textarea required aria-label={bug ? "Description" : "Feedback"} value={bug ? body.description : body.body} onChange={(e) => setBody({ ...body, ...(bug ? { description: e.target.value } : { body: e.target.value }) })} placeholder={bug ? "What happened?" : "What should we improve?"} className="min-h-40 w-full rounded-xl border border-line bg-surface px-4 py-3" />{bug && <><input aria-label="Affected page" value={body.affected_page} onChange={(e) => setBody({ ...body, affected_page: e.target.value })} placeholder="Affected page" className="w-full rounded-xl border border-line bg-surface px-4 py-3" /><textarea aria-label="Reproduction steps" value={body.reproduction_steps} onChange={(e) => setBody({ ...body, reproduction_steps: e.target.value })} placeholder="Reproduction steps" className="min-h-24 w-full rounded-xl border border-line bg-surface px-4 py-3" /></>}<Button type="submit">Submit</Button>{message && <p role="status" className="text-sm text-slate-300">{message}</p>}</form></section>;
}

export function MyFeedback() { return <ConsoleList title="My feedback" description="Only your own feedback records are shown." loader={operationsApi.myFeedback} fields={["title", "category", "status", "created_at"]} />; }
export function PublicStatus() { return <ConsoleList title="CodeMaster Academy status" description="Public service status without internal infrastructure details." loader={operationsApi.status} fields={["name", "status"]} />; }

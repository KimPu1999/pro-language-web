"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import Editor from "@monaco-editor/react";
import { cloudLabsApi } from "@/lib/api";
import { Badge, Button, Card, EmptyState, Skeleton } from "@/components/ui";

function csrf() {
  return typeof document === "undefined" ? "" : document.cookie.split("; ").find((item) => item.startsWith("cm_csrf="))?.slice(8) ?? "";
}

function ErrorState({ message }: { message: string }) {
  return <Card><p className="text-rose-300">{message}</p></Card>;
}

export function CloudLabCatalog() {
  const [data, setData] = useState<any>();
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  useEffect(() => { cloudLabsApi.catalog(search ? `?search=${encodeURIComponent(search)}` : "").then(setData).catch((e) => setError(e.message)); }, [search]);
  if (error) return <ErrorState message={error} />;
  return <div className="space-y-6"><div><p className="text-sm text-indigo-300">Phase 26 · free developer environments</p><h1 className="mt-2 text-3xl font-semibold">Cloud development labs</h1><p className="mt-3 max-w-2xl text-slate-400">Practice Git, Docker, CI/CD, Kubernetes, and deployment workflows in owned workspaces. Execution status is always shown honestly.</p></div><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search labs" className="w-full rounded-xl border border-line bg-surface px-4 py-3 text-sm outline-none" />{!data ? <Skeleton /> : data.items?.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{data.items.map((lab: any) => <Card key={lab.id} className="flex flex-col p-5"><div className="flex items-center justify-between gap-3"><Badge>{lab.category}</Badge><span className="text-xs text-slate-500">{lab.estimated_minutes} min</span></div><h2 className="mt-4 text-lg font-semibold">{lab.title}</h2><p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-400">{lab.description_en}</p><div className="mt-auto flex items-center justify-between gap-3 pt-5"><span className="text-xs text-slate-500">{lab.difficulty} · {lab.technology}</span><Link href={`/cloud-labs/${lab.id}`} className="text-sm font-semibold text-indigo-300">Open lab →</Link></div></Card>)}</div> : <EmptyState title="No published cloud labs" description="Published labs will appear here when an instructor releases a version." />}</div>;
}

export function CloudLabDashboard() {
  const [data, setData] = useState<any>(); const [error, setError] = useState("");
  useEffect(() => { cloudLabsApi.dashboard().then(setData).catch((e) => setError(e.message)); }, []);
  if (error) return <ErrorState message={error} />; if (!data) return <Skeleton />;
  return <div className="space-y-6"><div><p className="text-sm text-indigo-300">Your environments</p><h1 className="mt-2 text-3xl font-semibold">Cloud lab dashboard</h1></div><div className="grid gap-4 sm:grid-cols-3">{[["Active workspaces", data.active_workspaces?.length ?? 0], ["Started labs", data.progress?.started ?? 0], ["Completed labs", data.completed_labs ?? 0]].map(([label, value]) => <Card className="p-5" key={String(label)}><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-3xl font-semibold">{String(value)}</p></Card>)}</div><Card className="p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold">Recent workspaces</h2><p className="mt-1 text-sm text-slate-500">Resource usage is based on persisted workspace files.</p></div><Link href="/cloud-labs" className="text-sm text-indigo-300">Browse labs →</Link></div>{data.recent_workspaces?.length ? <div className="mt-5 space-y-2">{data.recent_workspaces.map((workspace: any) => <Link href={`/cloud-labs/workspaces/${workspace.id}`} className="flex items-center justify-between rounded-xl bg-ink p-4" key={workspace.id}><span className="font-mono text-sm">{String(workspace.id).slice(0, 8)}…</span><Badge>{workspace.status}</Badge></Link>)}</div> : <EmptyState title="No workspaces yet" description="Choose a published lab to create your first isolated workspace." />}</Card></div>;
}

export function CloudLabDetail({ id }: { id: string }) {
  const [data, setData] = useState<any>(); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { cloudLabsApi.detail(id).then(setData).catch((e) => setError(e.message)); }, [id]);
  async function create() { setBusy(true); try { const workspace = await cloudLabsApi.createWorkspace(id, csrf()); window.location.href = `/cloud-labs/workspaces/${workspace.id}`; } catch (e) { setError(e instanceof Error ? e.message : "Unable to create workspace"); } finally { setBusy(false); } }
  if (error) return <ErrorState message={error} />; if (!data) return <Skeleton />;
  return <div className="max-w-3xl space-y-6"><div><p className="text-sm text-indigo-300">Cloud lab</p><h1 className="mt-2 text-3xl font-semibold">{data.title}</h1><div className="mt-4 flex flex-wrap gap-2"><Badge>{data.category}</Badge><Badge>{data.difficulty}</Badge><Badge>{data.technology}</Badge><Badge>{data.estimated_minutes} min</Badge></div></div><Card className="space-y-5 p-6"><p className="whitespace-pre-wrap leading-7 text-slate-300">{data.description_en}</p><div><h2 className="font-semibold">Objectives</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-400">{data.objectives?.map((item: string) => <li key={item}>{item}</li>)}</ul></div><p className="rounded-xl bg-amber-500/10 p-4 text-sm text-amber-200">Mode: {data.execution_mode}. Student commands are not executed by the FastAPI application server.</p><Button onClick={create} disabled={busy}>{busy ? "Creating…" : "Create workspace"}</Button></Card></div>;
}

export function CloudWorkspace({ id }: { id: string }) {
  const [data, setData] = useState<any>(); const [source, setSource] = useState(""); const [path, setPath] = useState("main.py"); const [message, setMessage] = useState("");
  const load = useCallback(() => cloudLabsApi.workspace(id).then((next) => { setData(next); const file = next.files?.[0]; if (file) { setPath(file.path); setSource(file.source_code); } }).catch((e) => setMessage(e.message)), [id]);
  useEffect(() => { load(); }, [load]);
  async function save() { try { await cloudLabsApi.saveFile(id, { path, source_code: source, language: path.endsWith(".js") ? "javascript" : "python" }, csrf()); setMessage("Saved"); } catch (e) { setMessage(e instanceof Error ? e.message : "Save failed"); } }
  async function action(actionName: string) { try { const result = await cloudLabsApi.lifecycle(id, actionName, csrf()); setMessage(`Workspace ${result.status}`); load(); } catch (e) { setMessage(e instanceof Error ? e.message : "Lifecycle action failed"); } }
  async function snapshot() { try { const result = await cloudLabsApi.snapshot(id, csrf()); setMessage(`Snapshot saved: ${String(result.id).slice(0, 8)}…`); } catch (e) { setMessage(e instanceof Error ? e.message : "Snapshot failed"); } }
  const language = useMemo(() => path.endsWith(".js") ? "javascript" : path.endsWith(".ts") ? "typescript" : "python", [path]);
  if (!data) return <Card><p className="text-slate-400">{message || "Loading workspace…"}</p></Card>;
  return <div className="space-y-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm text-indigo-300">Browser cloud IDE</p><h1 className="mt-1 font-semibold">Workspace {String(data.id).slice(0, 8)}…</h1></div><div className="flex flex-wrap gap-2"><Badge>{data.status}</Badge><Badge>{data.execution?.mode}</Badge><Button onClick={save}>Save</Button><Button onClick={snapshot} className="bg-elevated">Snapshot</Button></div></div><div className="grid gap-4 xl:grid-cols-[220px_1fr_300px]"><Card className="p-4"><h2 className="font-semibold">Files</h2>{data.files?.map((file: any) => <button className={`mt-2 block w-full rounded-lg px-3 py-2 text-left text-sm ${file.path === path ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:bg-surface"}`} key={file.path} onClick={() => { setPath(file.path); setSource(file.source_code); }}>{file.path}</button>)}<div className="mt-6 space-y-2"><Button onClick={() => action("start")} className="w-full">Start</Button><Button onClick={() => action("suspend")} className="w-full bg-elevated">Suspend</Button><Button onClick={() => action("stop")} className="w-full bg-elevated">Stop</Button></div></Card><Card className="overflow-hidden"><div className="border-b border-line px-4 py-3 text-sm text-slate-400">{path}</div><Editor height="560px" language={language} theme="vs-dark" value={source} onChange={(value) => setSource(value ?? "")} options={{ fontSize: 14, minimap: { enabled: false }, automaticLayout: true, padding: { top: 16 } }} /></Card><Card className="p-5"><h2 className="font-semibold">Terminal / output</h2><p className="mt-3 text-sm leading-6 text-amber-200">{data.execution?.detail}</p><p className="mt-5 text-xs text-slate-500">{message || "No command has been executed."}</p><div className="mt-6 border-t border-line pt-4"><p className="text-sm text-slate-400">Storage</p><p className="mt-1 font-mono text-sm">{data.quota.storage_bytes} / {data.quota.storage_limit_bytes} bytes</p></div></Card></div></div>;
}

export function CloudPracticeMode({ mode }: { mode: string }) {
  const [data, setData] = useState<any>(); useEffect(() => { cloudLabsApi.modes().then(setData); }, []); const item = data?.[mode];
  return <div className="max-w-3xl space-y-6"><div><p className="text-sm text-indigo-300">DevOps learning lab</p><h1 className="mt-2 text-3xl font-semibold capitalize">{mode} practice</h1></div><Card className="p-6"><Badge>{item?.mode ?? "Loading"}</Badge><h2 className="mt-5 text-xl font-semibold">Safe, guided practice</h2><p className="mt-3 leading-7 text-slate-400">This module presents concepts and deterministic exercises. It does not execute untrusted infrastructure commands on the application host.</p><p className="mt-5 rounded-xl bg-amber-500/10 p-4 text-sm text-amber-200">{item?.available ? `Mode: ${item.mode}.` : "This integration is not configured in the current environment."}</p><Link href="/cloud-labs" className="mt-5 inline-block text-sm text-indigo-300">Browse available labs →</Link></Card></div>;
}

export function CloudInstructorLabs() { return <Card><h1 className="text-3xl font-semibold">Cloud lab builder</h1><p className="mt-3 text-slate-400">Uses the existing instructor lab authoring and publishing workflow. Validation remains server-side and runner-dependent.</p><Link className="mt-5 inline-block text-indigo-300" href="/instructor/labs">Open existing lab authoring →</Link></Card>; }

export function CloudOperations() { const [data, setData] = useState<any>(); const [error, setError] = useState(""); useEffect(() => { cloudLabsApi.operations().then(setData).catch((e) => setError(e.message)); }, []); if (error) return <ErrorState message={error} />; if (!data) return <Skeleton />; return <div className="space-y-6"><h1 className="text-3xl font-semibold">Cloud lab operations</h1><div className="grid gap-4 sm:grid-cols-2"><Card className="p-5"><p className="text-sm text-slate-400">Workspaces</p><p className="mt-2 text-3xl">{data.workspace_count}</p></Card><Card className="p-5"><p className="text-sm text-slate-400">Failed runs</p><p className="mt-2 text-3xl">{data.failed_runs}</p></Card></div><Card className="p-5"><p>Runner: <span className="text-amber-200">{data.runner.status}</span></p><p className="mt-2 text-sm text-slate-400">Docker socket exposed: {String(data.runner.host_socket_exposed)} · Kubernetes mode: {data.security.kubernetes_mode} · Public previews: {String(data.security.public_previews)}</p></Card></div>; }

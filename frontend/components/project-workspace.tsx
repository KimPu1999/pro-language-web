"use client";

import { useState } from "react";
import { csrf } from "@/components/auth-form";
import { projectApi } from "@/lib/project-api";
import { Card, Skeleton } from "@/components/ui";
import { ProjectSubmissionPanel } from "@/components/project-submission-panel";

type WorkspaceData = {
  id: string;
  status: string;
  project: { title: string; description_en: string; milestones: { id: string; title: string; code?: string; filename?: string | null; expected_output?: string }[] };
  progress: { percent: number; completed: number; total: number };
  milestones: { id: string; completed: boolean; notes?: string }[];
  submissions: { id: string; status: string; repository_url: string; branch_or_sha: string; submitted_at: string; review?: { decision: string; comments: string; total_score?: number | null } | null }[];
};

export function ProjectWorkspace({ id, initialData }: { id: string; initialData?: WorkspaceData | null }) {
  const [data, setData] = useState<WorkspaceData | null>(initialData ?? null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState<string | null>(null);
  const [activeFile, setActiveFile] = useState<string | null>(null);

  const refresh = async () => {
    setError("");
    try { setData(await projectApi.workspace(id) as WorkspaceData); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load workspace"); }
  };

  const toggleMilestone = async (milestoneId: string, completed: boolean, notes = "") => {
    setSaving(milestoneId); setMessage("");
    try { await projectApi.milestone(id, milestoneId, { completed, notes }, csrf()); await refresh(); setMessage("Progress saved."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to save progress"); }
    finally { setSaving(null); }
  };


  if (error && !data) return <section className="mx-auto max-w-6xl px-5 py-14"><Card className="p-7"><p className="text-red-300" role="alert">Unable to load this project workspace. {error}</p><button onClick={refresh} className="mt-5 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold">Retry</button></Card></section>;
  if (!data) return <section className="mx-auto max-w-6xl px-5 py-14"><Skeleton className="h-12 w-80"/><div className="mt-8 grid gap-5 lg:grid-cols-2"><Skeleton className="h-96"/><Skeleton className="h-96"/></div></section>;
  const currentFile = data.project.milestones.find(item => item.id === activeFile);
  return <section className="mx-auto max-w-6xl px-5 py-10 lg:px-8"><div className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-sm font-medium text-indigo-300">Authenticated project workspace</p><h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">{data.project.title}</h1><p className="mt-3 text-slate-400">{data.status.replaceAll("_", " ")} · {data.progress.completed} of {data.progress.total} milestones · {data.progress.percent}%</p></div><button onClick={refresh} className="rounded-lg border border-line px-4 py-2 text-sm text-slate-300 hover:border-indigo-400/60">Refresh</button></div>
    <div className="mt-7 h-2 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-400 transition-all" style={{ width: `${Math.min(100, Math.max(0, data.progress.percent))}%` }}/></div>
    {(error || message) && <p className={`mt-4 text-sm ${error ? "text-red-300" : "text-emerald-300"}`} role={error ? "alert" : "status"}>{error || message}</p>}
    <div className="mt-7 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.85fr)]"><Card className="p-6"><h2 className="text-xl font-bold">Project milestones</h2><p className="mt-2 text-sm leading-6 text-slate-400">Complete the guide in order. Progress is saved through the authenticated API, not only in the browser.</p><div className="mt-5 space-y-3">{data.project.milestones.map((milestone, index) => { const state = data.milestones.find(item => item.id === milestone.id); return <div key={milestone.id} className="flex items-start gap-3 rounded-xl bg-ink p-4"><input aria-label={`Complete ${milestone.title}`} type="checkbox" checked={!!state?.completed} disabled={saving === milestone.id} onChange={event => toggleMilestone(milestone.id, event.target.checked, state?.notes)} className="mt-1 h-4 w-4 accent-indigo-500"/><div className="min-w-0 flex-1"><p className="font-medium text-slate-100">{index + 1}. {milestone.title}</p>{milestone.expected_output && <p className="mt-1 text-xs leading-5 text-slate-500">Expected: {milestone.expected_output}</p>}</div>{milestone.code && <button onClick={() => setActiveFile(milestone.id)} className="rounded-lg border border-line px-2.5 py-1.5 text-xs text-indigo-200 hover:border-indigo-400/60">View code</button>}</div>; })}</div></Card>
      <div className="space-y-5"><Card className="p-6"><h2 className="text-xl font-bold">Code workspace</h2>{currentFile ? <><div className="mt-4 flex items-center justify-between text-xs text-slate-500"><span>{currentFile.filename || "source.txt"}</span><button onClick={() => navigator.clipboard.writeText(currentFile.code || "")} className="text-indigo-300">Copy code</button></div><pre className="mt-3 max-h-96 overflow-auto rounded-xl bg-[#080d1b] p-4 text-xs leading-6 text-indigo-100"><code>{currentFile.code}</code></pre><p className="mt-3 text-xs leading-5 text-amber-200/80">This workspace is a source preview. It does not claim to execute code unless a secure runner reports an actual result.</p></> : <p className="mt-4 rounded-xl bg-ink p-4 text-sm leading-6 text-slate-400">Select a milestone with source code to inspect its file. Draft editing and language-specific execution are enabled only where a protected backend workspace exists.</p>}</Card></div></div>
    <ProjectSubmissionPanel projectId={id} projectStatus={data.status} progress={data.progress} submissions={data.submissions} onRefresh={refresh} /></section>;
}

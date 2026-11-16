"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ProjectMilestone, ProjectTemplate } from "@/lib/types";
import { Card, Skeleton } from "@/components/ui";
import { csrf } from "@/components/auth-form";
import { projectApi } from "@/lib/project-api";

type StudentProject = { id: string; project_id: string; status: string; progress?: { percent: number; completed: number; total: number } };

function CodeBlock({ step }: { step: ProjectMilestone }) {
  const [copied, setCopied] = useState(false);
  if (!step.code) return <Card className="p-6 text-sm text-slate-400">No source snippet is published for this step. Follow the written instructions and use the project workspace for available files.</Card>;
  const copy = async () => { await navigator.clipboard.writeText(step.code || ""); setCopied(true); window.setTimeout(() => setCopied(false), 1200); };
  return <Card className="overflow-hidden p-0"><div className="flex items-center justify-between border-b border-line px-4 py-3 text-xs text-slate-500"><span>{step.filename || "source.txt"}</span><button onClick={copy} className="text-indigo-300 hover:text-white">{copied ? "Copied" : "Copy code"}</button></div><pre className="max-h-[620px] overflow-auto p-5 text-sm leading-7 text-indigo-100"><code>{step.code}</code></pre></Card>;
}

export function ProjectStepReader({ project, step }: { project: ProjectTemplate; step: ProjectMilestone }) {
  const [studentProject, setStudentProject] = useState<StudentProject | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(true);
  const [progressError, setProgressError] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const index = project.milestones.findIndex(item => item.id === step.id);
  const previous = project.milestones[index - 1];
  const next = project.milestones[index + 1];
  const progressPercent = studentProject?.progress?.percent ?? 0;
  const completed = useMemo(() => studentProject?.progress?.completed ?? 0, [studentProject]);

  const loadProgress = useCallback(async () => {
    setLoadingProgress(true); setProgressError("");
    try {
      const rows = await projectApi.mine() as StudentProject[];
      setStudentProject(rows.find(row => row.project_id === project.id) ?? null);
    } catch (reason) { setProgressError(reason instanceof Error ? reason.message : "Progress is unavailable"); }
    finally { setLoadingProgress(false); }
  }, [project.id]);
  useEffect(() => { loadProgress(); }, [loadProgress]);

  const start = async () => {
    setSaving(true); setMessage("");
    try { const result = await projectApi.start(project.slug, csrf()); await loadProgress(); setMessage("Project started. This step can now be marked complete."); if (!studentProject) setStudentProject({ id: result.id, project_id: project.id, status: result.status, progress: { percent: 0, completed: 0, total: project.milestones.length } }); }
    catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to start project"); }
    finally { setSaving(false); }
  };

  const complete = async () => {
    if (!studentProject) return;
    setSaving(true); setMessage("");
    try { await projectApi.milestone(studentProject.id, step.id, { completed: true, notes: "" }, csrf()); await loadProgress(); setMessage("Step marked complete."); }
    catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to save step progress"); }
    finally { setSaving(false); }
  };

  return <article className="space-y-6"><div className="flex flex-wrap items-center gap-2 text-sm text-slate-400"><Link href={`/projects/${project.slug}`} className="hover:text-white">{project.title}</Link><span>/</span><span className="text-slate-200">Step {step.position}</span></div><div className="grid gap-6 xl:grid-cols-[220px_minmax(0,1fr)_220px]"><aside className="order-2 h-fit xl:order-1 xl:sticky xl:top-24"><Card className="p-4"><div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Tutorial steps</p><span className="text-xs text-indigo-300">{index + 1}/{project.milestones.length}</span></div><div className="mt-4 h-2 rounded-full bg-slate-800"><div className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-400" style={{ width: `${Math.round(((index + 1) / Math.max(1, project.milestones.length)) * 100)}%` }}/></div><nav className="mt-4 max-h-[55vh] space-y-1 overflow-y-auto" aria-label="Tutorial steps">{project.milestones.map((item, itemIndex) => <Link key={item.id} href={`/projects/${project.slug}/learn/${item.slug || `step-${item.position}`}`} className={`block rounded-lg px-3 py-2 text-xs transition ${item.id === step.id ? "bg-indigo-500/20 text-indigo-100" : "text-slate-400 hover:bg-white/5 hover:text-white"}`} aria-current={item.id === step.id ? "step" : undefined}>{itemIndex + 1}. {item.title}</Link>)}</nav></Card></aside>
      <main className="order-1 min-w-0 space-y-6 xl:order-2"><header><p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-300">Step {step.position} · {project.title}</p><h1 className="mt-3 text-3xl font-extrabold tracking-tight sm:text-5xl">{step.title}</h1><p className="mt-4 text-lg leading-8 text-slate-400">{step.description_en}</p></header><Card className="p-6 sm:p-8"><h2 className="text-xl font-bold">Instructions</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-8 text-slate-300">{step.content_en || step.description_en}</p></Card><section><h2 className="mb-3 text-xl font-bold">Relevant source code</h2><CodeBlock step={step}/></section>{step.line_explanation && <Card className="p-6 sm:p-8"><h2 className="text-xl font-bold">Code explanation</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-8 text-slate-300">{step.line_explanation}</p></Card>}{step.expected_output && <Card className="p-6 sm:p-8"><h2 className="text-xl font-bold">Expected result</h2><p className="mt-2 text-xs text-slate-500">Illustrative output unless a secure runner has verified it.</p><pre className="mt-4 overflow-x-auto whitespace-pre-wrap rounded-xl bg-ink p-4 text-sm leading-7 text-emerald-200"><code>{step.expected_output}</code></pre></Card>}<Card className="p-6 sm:p-8"><h2 className="text-xl font-bold">Verification checklist</h2><ul className="mt-4 space-y-3 text-sm leading-7 text-slate-300"><li>✓ Follow the file path and instructions for this step.</li><li>✓ Run the project-specific command locally in the documented environment.</li><li>✓ Compare the actual result with the expected result above.</li><li>✓ Record failures and fix them before continuing.</li></ul><p className="mt-4 text-xs text-slate-500">This checklist is manual. It is not reported as an automated test.</p></Card><Card className="border-amber-400/20 bg-amber-400/5 p-6"><h2 className="text-xl font-bold">Hints and common mistakes</h2><p className="mt-4 text-sm leading-7 text-slate-300">No progressive hint or mistake list has been published for this step yet. Use the code explanation and project requirements, and ask an instructor when the local verification result differs.</p></Card><div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-6">{previous ? <Link href={`/projects/${project.slug}/learn/${previous.slug || `step-${previous.position}`}`} className="rounded-lg border border-line px-4 py-2 text-sm text-slate-300 hover:border-indigo-400/60">← Previous</Link> : <span/>}{next ? <Link href={`/projects/${project.slug}/learn/${next.slug || `step-${next.position}`}`} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400">Next step →</Link> : <Link href={`/projects/${project.slug}`} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400">Back to project</Link>}</div></main>
      <aside className="order-3 h-fit space-y-4 xl:sticky xl:top-24"><Card className="p-5"><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Your progress</p>{loadingProgress ? <Skeleton className="mt-4 h-8"/> : <><p className="mt-3 text-3xl font-bold text-white">{progressPercent}%</p><p className="mt-1 text-xs text-slate-500">{completed} completed steps</p><div className="mt-3 h-2 rounded-full bg-slate-800"><div className="h-2 rounded-full bg-emerald-500" style={{ width: `${progressPercent}%` }}/></div></>}{progressError && <p className="mt-3 text-xs text-amber-200">Sign in to save tutorial progress.</p>}{message && <p className="mt-3 text-xs text-emerald-300" role="status">{message}</p>}</Card><Card className="p-5">{studentProject ? <button disabled={saving} onClick={complete} className="w-full rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-60">{saving ? "Saving…" : "Mark step complete"}</button> : <button disabled={saving || loadingProgress} onClick={start} className="w-full rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-60">{saving ? "Starting…" : "Start project"}</button>}<p className="mt-3 text-xs leading-5 text-slate-500">Progress is scoped to your authenticated project workspace.</p></Card></aside></div></article>;
}

"use client";

import Editor from "@monaco-editor/react";
import { useEffect, useMemo, useState } from "react";
import { csrf } from "@/components/auth-form";
import { api } from "@/lib/api";
import type { RunnerJob, RunnerLanguage } from "@/lib/types";
import type { ProjectSourceFile } from "@/components/project-source-viewer";

const monacoLanguage: Record<string, string> = { c: "c", cpp: "cpp", python: "python", javascript: "javascript", typescript: "typescript", java: "java", php: "php", sql: "sql", html: "html", css: "css", rust: "rust", text: "plaintext" };

export function ProjectCodeWorkspace({ files }: { files: ProjectSourceFile[] }) {
  const [drafts, setDrafts] = useState(files);
  const [activeId, setActiveId] = useState(files[0]?.id ?? "");
  const [job, setJob] = useState<RunnerJob | null>(null);
  const [languages, setLanguages] = useState<RunnerLanguage[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const active = drafts.find(file => file.id === activeId) ?? drafts[0];
  const language = active?.language ?? "text";
  const runnerAvailable = useMemo(() => languages.some(item => item.identifier === language), [languages, language]);

  useEffect(() => { api.runnerLanguages().then(setLanguages).catch(() => setLanguages([])); }, []);
  const updateCode = (code: string | undefined) => { if (!active) return; setDrafts(current => current.map(file => file.id === active.id ? { ...file, code: code ?? "" } : file)); setNotice("Unsaved browser draft"); };
  const reset = () => { if (!active) return; setDrafts(current => current.map(file => file.id === active.id ? { ...file, code: files.find(original => original.id === active.id)?.code ?? "" } : file)); setNotice("File reset to the published starter code."); setJob(null); };
  const run = async () => {
    if (!active || !runnerAvailable) { setNotice("A validated secure runner is not available for this language."); return; }
    setBusy(true); setError(""); setNotice(""); setJob(null);
    try { const created = await api.execute({ language, source_code: active.code }, csrf()); setJob(created); if (created.status === "queued" || created.status === "running") window.setTimeout(async () => { try { setJob(await api.runnerJob(created.id)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to read execution status"); } }, 800); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to submit code"); }
    finally { setBusy(false); }
  };
  if (!files.length) return <p className="rounded-xl bg-ink/60 p-5 text-sm text-slate-400">No starter files are published for this project yet.</p>;
  const result = job?.result;
  return <section className="overflow-hidden rounded-2xl border border-line bg-surface" aria-label="Interactive project code workspace"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3"><div><p className="font-semibold text-white">Project code workspace</p><p className="text-xs text-slate-500">{language} · {active?.path}</p></div><div className="flex flex-wrap gap-2"><button onClick={reset} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300 hover:border-indigo-400/60">Reset file</button><button onClick={run} disabled={busy || !runnerAvailable} className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">{busy ? "Submitting…" : runnerAvailable ? "Run code" : "Runner unavailable"}</button></div></div><div className="flex overflow-x-auto border-b border-line">{drafts.map(file => <button key={file.id} onClick={() => setActiveId(file.id)} className={`whitespace-nowrap px-4 py-2 text-xs ${file.id === active?.id ? "border-b-2 border-indigo-400 text-white" : "text-slate-500 hover:text-slate-200"}`}>{file.path}</button>)}</div><Editor height="390px" language={monacoLanguage[language] ?? "plaintext"} theme="vs-dark" value={active?.code ?? ""} onChange={updateCode} options={{ fontSize: 14, minimap: { enabled: false }, wordWrap: "on", automaticLayout: true, padding: { top: 16 }, readOnly: false }} /><div className="border-t border-line bg-ink p-4"><div className="flex flex-wrap items-center justify-between gap-2"><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Execution output</p><span className="text-xs text-slate-600">{job?.status ?? "Not run"}</span></div>{notice && <p className="mt-3 text-xs text-amber-200">{notice}. Draft persistence is not enabled for project workspaces yet.</p>}{error && <p className="mt-3 text-sm text-red-300" role="alert">{error}</p>}{job?.status === "runner_unavailable" && <p className="mt-3 rounded-lg bg-amber-500/10 p-3 text-sm text-amber-200">Secure runner unavailable. No code was executed.</p>}<pre className="mt-3 min-h-16 whitespace-pre-wrap text-sm text-slate-300">{result ? `stdout:\n${result.stdout || "(empty)"}\n\nstderr:\n${result.stderr || "(empty)"}\n\nexit code: ${result.exit_code ?? "not available"}\nexecution time: ${result.execution_time_ms ?? "not available"} ms` : "Run the active file to display real runner output."}</pre></div></section>;
}

"use client";

import Editor from "@monaco-editor/react";
import { useState } from "react";
import { api } from "@/lib/api";
import type { RunnerJob } from "@/lib/types";
import { csrf } from "@/components/auth-form";

const monacoLanguage: Record<string, string> = { python: "python", javascript: "javascript", typescript: "typescript", java: "java", cpp: "cpp", php: "php" };

export function InteractiveClassroom({ language, initialCode, lessonId }: { language: string; initialCode: string; lessonId: string }) {
  const [code, setCode] = useState(initialCode);
  const [job, setJob] = useState<RunnerJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"editor" | "output">("editor");
  const run = async () => {
    setBusy(true); setError(""); setTab("output");
    try {
      const created = await api.execute({ language, source_code: code }, csrf());
      setJob(created);
      if (created.status === "queued" || created.status === "running") {
        window.setTimeout(async () => { try { setJob(await api.runnerJob(created.id)); } catch (err) { setError(err instanceof Error ? err.message : "Unable to read execution status"); } }, 700);
      }
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to submit code"); }
    finally { setBusy(false); }
  };
  const result = job?.result;
  return <section className="overflow-hidden rounded-2xl border border-line bg-surface" aria-label="Interactive coding classroom">
    <div className="flex items-center justify-between border-b border-line px-4 py-3"><div><p className="text-sm font-semibold text-white">Try it yourself</p><p className="text-xs text-slate-500">{language} · {lessonId.slice(0, 8)}</p></div><button onClick={run} disabled={busy} className="rounded-lg bg-indigo-500 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-60">{busy ? "Submitting…" : "Run code"}</button></div>
    <div className="flex border-b border-line lg:hidden">{(["editor", "output"] as const).map(value => <button key={value} onClick={() => setTab(value)} className={`flex-1 px-3 py-2 text-sm capitalize ${tab === value ? "border-b-2 border-indigo-400 text-white" : "text-slate-500"}`}>{value}</button>)}</div>
    <div className={`${tab === "output" ? "hidden lg:block" : ""}`}><Editor height="360px" language={monacoLanguage[language] ?? "plaintext"} theme="vs-dark" value={code} onChange={value => setCode(value ?? "")} options={{ fontSize: 14, minimap: { enabled: false }, wordWrap: "on", tabSize: 2, padding: { top: 16 } }} /></div>
    <div className={`border-t border-line bg-ink p-4 ${tab === "editor" ? "hidden lg:block" : ""}`}><div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Output</p><span className="text-xs text-slate-600">{job?.status ?? "Ready"}</span></div>{job?.status === "runner_unavailable" ? <p className="mt-3 rounded-lg bg-amber-500/10 p-3 text-sm text-amber-200">The secure runner is unavailable in this environment. Your code was not executed.</p> : error ? <p role="alert" className="mt-3 text-sm text-red-300">{error}</p> : <pre className="mt-3 min-h-16 whitespace-pre-wrap text-sm text-slate-300">{result?.stdout || result?.stderr || (job ? "Execution queued. Refresh status to see results." : "Run the example to see output here.")}</pre>}</div>
  </section>;
}

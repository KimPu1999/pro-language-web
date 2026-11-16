"use client";

import { useMemo, useState } from "react";

export type ProjectSourceFile = { id: string; path: string; language: string; code: string; description?: string; expectedOutput?: string };

function languageFor(path: string) {
  const extension = path.split(".").pop()?.toLowerCase();
  return ({ c: "c", cpp: "cpp", h: "c", py: "python", js: "javascript", ts: "typescript", tsx: "typescript", java: "java", php: "php", sql: "sql", html: "html", css: "css", json: "json", sh: "bash", yml: "yaml", yaml: "yaml" } as Record<string, string>)[extension ?? ""] ?? "text";
}

export function ProjectFileTree({ files, activeId, onSelect }: { files: ProjectSourceFile[]; activeId: string | null; onSelect: (id: string) => void }) {
  const folders = useMemo(() => files.map(file => file.path.split("/").slice(0, -1).join("/")).filter(Boolean).filter((value, index, values) => values.indexOf(value) === index), [files]);
  return <div className="rounded-xl border border-line bg-ink/60 p-3" aria-label="Project files"><p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Files</p>{folders.map(folder => <p key={folder} className="px-2 py-1 text-xs text-slate-500">▾ {folder}/</p>)}{files.map(file => <button key={file.id} onClick={() => onSelect(file.id)} className={`flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition ${activeId === file.id ? "bg-indigo-500/20 text-indigo-100" : "text-slate-400 hover:bg-white/5 hover:text-white"}`} aria-current={activeId === file.id ? "true" : undefined}><span className="text-xs text-slate-600">{file.path.endsWith("/") ? "▾" : "□"}</span><span className="truncate">{file.path.split("/").pop()}</span><span className="ml-auto text-[10px] uppercase text-slate-600">{file.language}</span></button>)}</div>;
}

export function ProjectSourceViewer({ files }: { files: ProjectSourceFile[] }) {
  const [activeId, setActiveId] = useState(files[0]?.id ?? null);
  const [copied, setCopied] = useState(false);
  const active = files.find(file => file.id === activeId) ?? files[0];
  if (!files.length) return <div className="rounded-xl bg-ink/60 p-5 text-sm leading-6 text-slate-400">No published starter files are available for this project yet. Check the project guide for local implementation instructions.</div>;
  const copy = async () => { if (!active) return; await navigator.clipboard.writeText(active.code); setCopied(true); window.setTimeout(() => setCopied(false), 1200); };
  return <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]"><ProjectFileTree files={files} activeId={active?.id ?? null} onSelect={setActiveId}/><div className="min-w-0 overflow-hidden rounded-xl border border-line bg-[#080d1b]"><div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-4 py-3 text-xs"><span className="text-slate-400">{active?.path}</span><button onClick={copy} className="text-indigo-300 hover:text-white">{copied ? "Copied" : "Copy code"}</button></div><pre className="max-h-[560px] overflow-auto p-5 text-sm leading-7 text-indigo-100"><code>{active?.code}</code></pre>{active?.description && <p className="border-t border-line px-4 py-3 text-xs leading-5 text-slate-500">{active.description}</p>}{active?.expectedOutput && <div className="border-t border-line px-4 py-3"><p className="text-xs font-semibold uppercase tracking-wider text-slate-600">Illustrative expected result</p><p className="mt-2 whitespace-pre-wrap text-xs leading-5 text-slate-400">{active.expectedOutput}</p></div>}</div></div>;
}

export { languageFor };

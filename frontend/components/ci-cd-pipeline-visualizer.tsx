"use client";

import { useEffect, useMemo, useState } from "react";

type Stage = { id: string; name: string; detail: string };
const STAGES: Stage[] = [
  { id: "source", name: "Source", detail: "A reviewed commit starts the workflow." },
  { id: "lint", name: "Lint", detail: "Style and configuration checks run." },
  { id: "test", name: "Test", detail: "Automated tests produce evidence." },
  { id: "build", name: "Build", detail: "A reproducible artifact is created." },
  { id: "scan", name: "Security scan", detail: "Dependencies, secrets, and images are checked." },
  { id: "publish", name: "Publish", detail: "The immutable artifact is retained." },
  { id: "staging", name: "Deploy staging", detail: "The candidate reaches a test environment." },
  { id: "approval", name: "Approval", detail: "A protected environment requires review." },
  { id: "production", name: "Deploy production", detail: "The approved artifact is released." },
  { id: "verify", name: "Verify", detail: "Health checks confirm the release." },
  { id: "rollback", name: "Rollback", detail: "The prior version is restored only when needed." },
];
const TEMPLATES = { standard: "Standard delivery", secure: "Security-first delivery", gitops: "GitOps delivery" } as const;

export function CICDPipelineVisualizer({ compact = false }: { compact?: boolean }) {
  const [template, setTemplate] = useState<keyof typeof TEMPLATES>("standard");
  const [position, setPosition] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(900);
  const [failed, setFailed] = useState(false);
  const [logs, setLogs] = useState<string[]>(["Simulation ready. No external pipeline was started."]);
  const stage = STAGES[position];
  const status = failed ? "failed" : position === STAGES.length - 1 ? "rollback available" : position === 0 ? "ready" : "running";
  const templateNote = useMemo(() => template === "secure" ? "Protected environments, pinned dependencies, and short-lived identity are explicit." : template === "gitops" ? "The deployment controller reconciles approved desired state." : "A straightforward artifact promotion flow with an approval gate.", [template]);

  useEffect(() => {
    if (!playing || failed) return;
    const timer = window.setInterval(() => {
      setPosition(current => {
        if (current >= STAGES.length - 1) { setPlaying(false); return current; }
        return current + 1;
      });
    }, speed);
    return () => window.clearInterval(timer);
  }, [failed, playing, speed]);

  const move = (next: number) => {
    const clamped = Math.max(0, Math.min(STAGES.length - 1, next));
    setPosition(clamped);
    setLogs(current => [...current.slice(-3), `${STAGES[clamped].name}: ${STAGES[clamped].detail}`]);
  };
  const reset = () => { setPlaying(false); setFailed(false); setPosition(0); setLogs(["Simulation reset. No external pipeline was started."]); };
  return <section className={compact ? "p-4" : "min-h-screen bg-[#0B1020] p-4 text-slate-100 sm:p-8"} aria-labelledby="cicd-visualizer-title"><div className="mx-auto max-w-6xl"><div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">CI/CD simulator</p><h1 id="cicd-visualizer-title" className="mt-2 text-2xl font-bold">Trace a release pipeline</h1><p className="mt-2 max-w-2xl text-sm text-slate-400">This deterministic simulator models pipeline state transitions. It is not a GitHub Actions, GitLab, Jenkins, or production run.</p></div><label className="text-sm text-slate-300">Template<select className="mt-2 block w-full rounded-lg border border-white/10 bg-[#131F36] px-3 py-2 sm:w-56" value={template} onChange={event => { setTemplate(event.target.value as keyof typeof TEMPLATES); reset(); }}>{Object.entries(TEMPLATES).map(([id, name]) => <option key={id} value={id}>{name}</option>)}</select></label></div><p className="mt-4 rounded-lg border border-blue-400/20 bg-blue-400/5 p-3 text-sm text-blue-100">{templateNote}</p><div className="mt-6 rounded-2xl border border-blue-400/20 bg-[#131F36] p-4 sm:p-6"><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{STAGES.map((item, index) => <button key={item.id} className={`rounded-xl border p-4 text-left transition ${index === position ? "border-blue-300 bg-blue-400/15" : index < position && !failed ? "border-emerald-400/30 bg-emerald-400/5" : "border-white/10 bg-[#0B1020]"}`} onClick={() => move(index)}><span className="text-[10px] uppercase tracking-wider text-slate-500">Stage {index + 1}</span><h2 className="mt-2 font-semibold">{item.name}</h2><p className="mt-2 text-xs leading-5 text-slate-400">{item.detail}</p></button>)}</div><div className="mt-6 flex flex-wrap items-center gap-2"><button className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold" onClick={() => setPlaying(value => !value)}>{playing ? "Pause" : "Play"}</button><button className="rounded-lg border border-white/10 px-3 py-2 text-sm" onClick={() => move(position - 1)} disabled={position === 0}>Back</button><button className="rounded-lg border border-white/10 px-3 py-2 text-sm" onClick={() => move(position + 1)} disabled={position >= STAGES.length - 1 || failed}>Step forward</button><button className="rounded-lg border border-amber-300/20 px-3 py-2 text-sm text-amber-100" onClick={() => { setPlaying(false); setFailed(true); setLogs(current => [...current.slice(-3), `${stage.name}: simulated failure; inspect logs before retry.`]); }}>Simulate failure</button><button className="rounded-lg border border-white/10 px-3 py-2 text-sm" onClick={() => { setFailed(false); setLogs(current => [...current.slice(-3), `${stage.name}: retry requested; idempotency must be checked.`]); }}>Retry</button><button className="rounded-lg border border-white/10 px-3 py-2 text-sm" onClick={reset}>Reset</button><label className="ml-auto text-xs text-slate-400">Speed<select className="ml-2 rounded border border-white/10 bg-[#0B1020] px-2 py-1" value={speed} onChange={event => setSpeed(Number(event.target.value))}><option value={1400}>Slow</option><option value={900}>Normal</option><option value={450}>Fast</option></select></label></div></div><div className="mt-6 grid gap-4 lg:grid-cols-2"><div className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Current state</p><h2 className="mt-2 text-xl font-semibold">{stage.name}</h2><p className="mt-2 text-sm text-slate-400">{stage.detail}</p><p className={`mt-4 text-sm ${failed ? "text-amber-200" : "text-emerald-300"}`}>Status: {failed ? "failure simulated — rollback or retry requires review" : status}</p></div><div className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Simulated logs</p><div className="mt-3 space-y-2 font-mono text-xs text-slate-300">{logs.map((log, index) => <p key={`${log}-${index}`}>{log}</p>)}</div></div></div></div></section>;
}

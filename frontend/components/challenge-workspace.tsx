"use client";

import Editor from "@monaco-editor/react";
import { useEffect, useMemo, useState } from "react";
import type { Challenge, RunnerJob } from "@/lib/types";
import { api } from "@/lib/api";
import { csrf } from "@/components/auth-form";
import { Badge, Card } from "@/components/ui";

type ChallengeResult = { status: string; score: number | null; job_id?: string; result?: RunnerJob["result"] };

export function ChallengeWorkspace({ challenge }: { challenge: Challenge }) {
  const first = challenge.languages[0];
  const [language, setLanguage] = useState(first?.language ?? "python");
  const [drafts, setDrafts] = useState<Record<string, string>>(() => Object.fromEntries(challenge.languages.map(item => [item.language, item.starter_code])));
  const [mode, setMode] = useState<"learn" | "practice">("learn");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ChallengeResult | null>(null);
  const code = drafts[language] ?? "";
  const selected = useMemo(() => challenge.languages.find(item => item.language === language) ?? first, [challenge.languages, first, language]);

  useEffect(() => {
    if (!result?.job_id || !["queued", "running"].includes(result.status)) return;
    let cancelled = false;
    let attempts = 0;
    const poll = async () => {
      try {
        const job = await api.runnerJob(result.job_id!);
        if (cancelled) return;
        setResult(current => current ? { ...current, status: job.status, result: job.result ?? undefined } : current);
        attempts += 1;
        if (["queued", "running"].includes(job.status) && attempts < 20) window.setTimeout(poll, 700);
      } catch (error) {
        if (!cancelled) setResult(current => current ? { ...current, status: error instanceof Error ? error.message : "Unable to read execution status" } : current);
      }
    };
    const timer = window.setTimeout(poll, 500);
    return () => { cancelled = true; window.clearTimeout(timer); };
  }, [result?.job_id, result?.status]);

  const run = async (submit: boolean) => {
    setBusy(true);
    try {
      const next = submit ? await api.challengeSubmit(challenge.id, { language, source_code: code }, csrf()) : await api.challengeRun(challenge.id, { language, source_code: code }, csrf());
      setResult(next);
    } catch (error) {
      setResult({ status: error instanceof Error ? error.message : "Unable to submit", score: null });
    } finally { setBusy(false); }
  };

  return <div className="space-y-6">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><Badge>{challenge.difficulty}</Badge><p className="mt-3 text-xs font-semibold uppercase tracking-widest text-indigo-300">{challenge.category?.name ?? "Practice challenge"}</p><h1 className="mt-2 text-3xl font-bold text-white">{challenge.title}</h1></div></div>
    <div className="flex gap-2 border-b border-line"><button type="button" onClick={() => setMode("learn")} className={`border-b-2 px-4 py-3 text-sm font-semibold ${mode === "learn" ? "border-indigo-400 text-white" : "border-transparent text-slate-500"}`}>Read and understand</button><button type="button" onClick={() => setMode("practice")} className={`border-b-2 px-4 py-3 text-sm font-semibold ${mode === "practice" ? "border-indigo-400 text-white" : "border-transparent text-slate-500"}`}>Optional practice</button></div>
    {mode === "learn" ? <div className="grid gap-6 lg:grid-cols-[1.15fr_.85fr]"><Card className="p-6"><h2 className="text-lg font-semibold text-white">Problem statement</h2><p className="mt-4 whitespace-pre-wrap leading-8 text-slate-300">{challenge.description_en}</p><h2 className="mt-8 text-lg font-semibold text-white">Learning approach</h2><p className="mt-3 leading-7 text-slate-400">Break the input into clear steps, identify the invariant that should remain true while processing it, and verify the result against the examples before submitting.</p><h2 className="mt-8 text-lg font-semibold text-white">Constraints and edge cases</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-400">{challenge.constraints.length ? challenge.constraints.map(value => <li key={value}>{value}</li>) : <li>Review the input limits before choosing an approach.</li>}</ul><h2 className="mt-8 text-lg font-semibold text-white">Common mistakes</h2><p className="mt-3 leading-7 text-slate-400">Check empty input, boundary values, output formatting, and whether your loop or index includes the final item.</p></Card><Card className="p-6"><h2 className="text-lg font-semibold text-white">Worked examples</h2>{challenge.examples.length ? challenge.examples.map((example, index) => <div className="mt-4 rounded-xl bg-ink p-4" key={`${example.input}-${index}`}><p className="text-xs uppercase tracking-widest text-slate-500">Example {index + 1}</p><pre className="mt-3 whitespace-pre-wrap font-mono text-sm text-slate-300">Input: {example.input || "∅"}{"\n"}Output: {example.output || "∅"}</pre>{example.explanation && <p className="mt-3 text-sm leading-6 text-slate-400">{example.explanation}</p>}</div>) : <p className="mt-4 text-sm text-slate-500">No public examples have been added yet.</p>}<h2 className="mt-8 text-lg font-semibold text-white">Hints</h2>{challenge.hints?.length ? challenge.hints.map((hint, index) => <details className="mt-3 rounded-lg border border-line p-3" key={index}><summary className="cursor-pointer text-sm text-indigo-300">Reveal hint {index + 1}</summary><p className="mt-3 text-sm leading-6 text-slate-400">{hint.body_en}</p></details>) : <p className="mt-3 text-sm text-slate-500">Hints are not available for this challenge.</p>}</Card></div> : <div className="grid gap-6 xl:grid-cols-[1fr_1fr]"><Card className="overflow-hidden"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4"><div><p className="text-xs uppercase tracking-widest text-slate-500">Optional execution</p><p className="mt-1 text-sm text-slate-400">Your code is sent to the configured isolated runner.</p></div><select aria-label="Programming language" value={language} onChange={event => setLanguage(event.target.value)} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm">{challenge.languages.map(value => <option key={value.language} value={value.language}>{value.language}</option>)}</select></div><Editor height="480px" language={language} theme="vs-dark" value={code} onChange={value => setDrafts(current => ({ ...current, [language]: value ?? "" }))} options={{ fontSize: 14, minimap: { enabled: false }, wordWrap: "on", padding: { top: 16 } }} /><div className="flex flex-wrap gap-2 border-t border-line bg-ink p-4"><button type="button" onClick={() => run(false)} disabled={busy || !selected} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-200">{busy ? "Working…" : "Run samples"}</button><button type="button" onClick={() => run(true)} disabled={busy || !selected} className="rounded-lg bg-indigo-500 px-3 py-2 text-sm font-semibold text-white">Submit solution</button></div></Card><Card className="p-6"><h2 className="text-lg font-semibold text-white">Public tests and expected output</h2>{challenge.public_tests?.length ? challenge.public_tests.map((test, index) => <div className="mt-4 rounded-xl bg-ink p-4 font-mono text-xs text-slate-300" key={index}>Input: {test.input || "∅"}<br/>Expected: {test.expected_output}</div>) : <p className="mt-4 text-sm text-slate-500">Public tests are not available. Hidden tests remain private.</p>}<div className="mt-8 border-t border-line pt-5"><p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Execution result</p>{result?.status === "runner_unavailable" ? <p className="mt-3 text-sm text-amber-200">Secure execution is unavailable in this environment. Your source was not executed.</p> : result ? <div className="mt-3 space-y-3"><p className="text-sm text-slate-300">{result.status}{result.score === null ? "" : ` · ${result.score}%`}</p>{result.result && <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-ink p-3 font-mono text-xs text-slate-300">{result.result.stdout || result.result.stderr || "No output."}</pre>}{result.result?.exit_code !== null && result.result?.exit_code !== undefined && <p className="text-xs text-slate-500">Exit code: {result.result.exit_code}{result.result.execution_time_ms !== null && result.result.execution_time_ms !== undefined ? ` · ${result.result.execution_time_ms} ms` : ""}</p>}{result.result?.error_code && <p className="text-xs text-amber-200">{result.result.error_code}</p>}</div> : <p className="mt-3 text-sm text-slate-300">Run samples or submit to see the verified result.</p>}</div></Card></div>}
  </div>;
}

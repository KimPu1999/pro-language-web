"use client";

import { useEffect, useMemo, useState } from "react";

type Kind = "array" | "stack";
type Snapshot = { values: number[]; operation: string };

const INITIAL: Record<Kind, number[]> = { array: [8, 3, 5], stack: [4, 7] };

export function DataStructuresVisualizer() {
  const [kind, setKind] = useState<Kind>("array");
  const [history, setHistory] = useState<Snapshot[]>([{ values: INITIAL.array, operation: "Initial state" }]);
  const [cursor, setCursor] = useState(0);
  const [input, setInput] = useState("9");
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState("700");

  const current = history[cursor];
  const complexity = kind === "array" ? "Index lookup O(1); middle insert/delete O(n)" : "Push/pop at top O(1)";
  const pseudocode = kind === "array" ? ["append(value)", "  place value at size", "  increase size"] : ["push(value)", "  add value to top", "pop()", "  remove top value"];

  function reset(nextKind = kind) {
    setPlaying(false);
    setHistory([{ values: INITIAL[nextKind], operation: "Initial state" }]);
    setCursor(0);
  }

  function selectKind(nextKind: Kind) {
    setKind(nextKind);
    reset(nextKind);
  }

  function commit(values: number[], operation: string) {
    const next = [...history.slice(0, cursor + 1), { values, operation }];
    setHistory(next);
    setCursor(next.length - 1);
  }

  function addValue() {
    const value = Number(input);
    if (!Number.isFinite(value)) return;
    commit([...current.values, value], kind === "array" ? `append(${value})` : `push(${value})`);
  }

  function removeValue() {
    if (current.values.length === 0) return;
    const values = kind === "array" ? current.values.slice(0, -1) : current.values.slice(0, -1);
    commit(values, kind === "array" ? "delete(last index)" : `pop() -> ${current.values[current.values.length - 1]}`);
  }

  function searchValue() {
    const value = Number(input);
    if (!Number.isFinite(value)) return;
    const index = current.values.indexOf(value);
    commit([...current.values], `search(${value}) -> ${index >= 0 ? `index ${index}` : "not found"}`);
  }

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setCursor((value) => value < history.length - 1 ? value + 1 : (setPlaying(false), value)), Number(speed));
    return () => window.clearInterval(timer);
  }, [playing, speed, history.length]);

  const slots = useMemo(() => current.values.map((value, index) => ({ value, index })), [current.values]);

  return (
    <main className="mx-auto min-h-screen max-w-6xl bg-[#0B1020] px-4 py-8 text-slate-100 sm:px-6 lg:px-8" aria-labelledby="visualizer-title">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-violet-300">Data Structures</p><h1 id="visualizer-title" className="mt-2 text-3xl font-bold">Interactive Visualizer</h1><p className="mt-2 max-w-2xl text-slate-400">Every operation creates a real deterministic state snapshot. Step backward and forward to inspect the trace.</p></div>
        <button type="button" onClick={() => reset()} className="rounded-lg border border-white/10 px-3 py-2 text-sm hover:bg-white/5">Reset</button>
      </div>
      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_300px]">
        <section className="rounded-2xl border border-white/10 bg-[#131F36] p-5">
          <div className="flex flex-wrap gap-2"><button type="button" onClick={() => selectKind("array")} className={`rounded-lg px-3 py-2 text-sm ${kind === "array" ? "bg-violet-600 text-white" : "border border-white/10 text-slate-300"}`}>Array</button><button type="button" onClick={() => selectKind("stack")} className={`rounded-lg px-3 py-2 text-sm ${kind === "stack" ? "bg-violet-600 text-white" : "border border-white/10 text-slate-300"}`}>Stack</button></div>
          <div className="mt-6 flex min-h-44 items-end gap-3 overflow-x-auto rounded-xl border border-white/10 bg-[#0B1020] p-5">{slots.length ? slots.map(({ value, index }) => <div key={`${cursor}-${index}`} className="min-w-16 text-center"><div className="rounded-lg border border-violet-400/50 bg-violet-500/20 px-4 py-4 text-lg font-semibold">{value}</div><p className="mt-2 text-xs text-slate-500">{kind === "stack" && index === slots.length - 1 ? "top" : `[${index}]`}</p></div>) : <p className="text-sm text-slate-500">Empty structure</p>}</div>
          <div className="mt-4 flex flex-wrap items-end gap-3"><label className="text-sm text-slate-300">Value<input value={input} onChange={(event) => setInput(event.target.value)} inputMode="numeric" className="mt-1 block w-24 rounded-lg border border-white/10 bg-[#0B1020] px-3 py-2 text-white" /></label><button type="button" onClick={addValue} className="rounded-lg bg-violet-600 px-3 py-2 text-sm font-medium">{kind === "array" ? "Insert" : "Push"}</button><button type="button" onClick={removeValue} className="rounded-lg border border-white/10 px-3 py-2 text-sm">{kind === "array" ? "Delete last" : "Pop"}</button><button type="button" onClick={searchValue} className="rounded-lg border border-white/10 px-3 py-2 text-sm">Search</button></div>
          <div className="mt-5 flex flex-wrap items-center gap-3"><button type="button" onClick={() => setCursor((value) => Math.max(0, value - 1))} disabled={cursor === 0} className="rounded-lg border border-white/10 px-3 py-2 text-sm disabled:opacity-40">Step back</button><button type="button" onClick={() => setCursor((value) => Math.min(history.length - 1, value + 1))} disabled={cursor === history.length - 1} className="rounded-lg border border-white/10 px-3 py-2 text-sm disabled:opacity-40">Step forward</button><button type="button" onClick={() => setPlaying((value) => !value)} className="rounded-lg border border-white/10 px-3 py-2 text-sm">{playing ? "Pause" : "Play"}</button><label className="text-sm text-slate-400">Speed<select value={speed} onChange={(event) => setSpeed(event.target.value)} className="ml-2 rounded-lg border border-white/10 bg-[#0B1020] px-2 py-2 text-white"><option value="1000">Slow</option><option value="700">Normal</option><option value="350">Fast</option></select></label><span className="text-sm text-slate-500">State {cursor + 1}/{history.length}</span></div>
          <p className="mt-4 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-sm text-slate-300" aria-live="polite">{current.operation}</p>
        </section>
        <aside className="space-y-5"><div className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><h2 className="font-semibold">Complexity</h2><p className="mt-2 text-sm leading-6 text-slate-400">{complexity}</p></div><div className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><h2 className="font-semibold">Pseudocode</h2><pre className="mt-3 text-xs leading-6 text-slate-400"><code>{pseudocode.join("\n")}</code></pre></div><div className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><h2 className="font-semibold">History</h2><ol className="mt-3 max-h-48 space-y-2 overflow-auto text-xs text-slate-400">{history.map((item, index) => <li key={`${item.operation}-${index}`} className={index === cursor ? "text-violet-300" : ""}>{index + 1}. {item.operation}</li>)}</ol></div></aside>
      </div>
    </main>
  );
}

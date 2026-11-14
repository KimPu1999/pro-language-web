"use client";

import { useMemo, useState } from "react";

const PROBLEMS = [
  { title: "Linear Search", difficulty: "Easy", category: "Search", statement: "Return the first index containing a target value.", complexity: "O(n) time, O(1) space" },
  { title: "Binary Search", difficulty: "Easy", category: "Search", statement: "Find a target in a sorted array without scanning every value.", complexity: "O(log n) time, O(1) space" },
  { title: "Two Sum", difficulty: "Medium", category: "Arrays", statement: "Find two indexes whose values add to a target.", complexity: "O(n) expected time with a hash map" },
  { title: "Shortest Path", difficulty: "Hard", category: "Graphs", statement: "Compute a shortest route when edge weights are nonnegative.", complexity: "O((V + E) log V) with a heap" },
  { title: "Longest Common Subsequence", difficulty: "Hard", category: "Dynamic Programming", statement: "Find the length of a sequence shared by two strings.", complexity: "O(nm) time, O(nm) space" },
];

export function AlgorithmProblems() {
  const [query, setQuery] = useState("");
  const [difficulty, setDifficulty] = useState("All");
  const items = useMemo(() => PROBLEMS.filter((problem) => (difficulty === "All" || problem.difficulty === difficulty) && `${problem.title} ${problem.category}`.toLowerCase().includes(query.toLowerCase())), [difficulty, query]);
  return <main className="mx-auto min-h-screen max-w-6xl bg-[#0B1020] px-4 py-8 text-slate-100 sm:px-6 lg:px-8" aria-labelledby="problems-title"><p className="text-xs font-semibold uppercase tracking-[0.18em] text-orange-300">Practice</p><h1 id="problems-title" className="mt-2 text-3xl font-bold">Algorithm Problems</h1><p className="mt-2 max-w-2xl text-slate-400">A public practice catalog with visible problem contracts. Hidden tests and submissions require the secure judge and are not exposed here.</p><div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto]"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search problems or categories" className="rounded-lg border border-white/10 bg-[#131F36] px-3 py-2 text-white" aria-label="Search problems" /><select value={difficulty} onChange={(event) => setDifficulty(event.target.value)} className="rounded-lg border border-white/10 bg-[#131F36] px-3 py-2 text-white" aria-label="Filter difficulty"><option>All</option><option>Easy</option><option>Medium</option><option>Hard</option></select></div><div className="mt-6 grid gap-4 md:grid-cols-2">{items.map((problem) => <article key={problem.title} className="rounded-2xl border border-white/10 bg-[#131F36] p-5"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold">{problem.title}</h2><span className="rounded-full bg-orange-500/15 px-2.5 py-1 text-xs text-orange-200">{problem.difficulty}</span></div><p className="mt-2 text-xs uppercase tracking-wide text-slate-500">{problem.category}</p><p className="mt-4 text-sm leading-6 text-slate-300">{problem.statement}</p><p className="mt-4 text-xs text-slate-400">Expected complexity: {problem.complexity}</p><p className="mt-4 text-xs text-slate-500">Solutions and hidden tests are deliberately not included in the client bundle.</p></article>)}{items.length === 0 && <p className="rounded-xl border border-dashed border-white/15 p-6 text-slate-400">No matching problems.</p>}</div></main>;
}

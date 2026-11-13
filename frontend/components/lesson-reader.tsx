"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Lesson } from "@/lib/types";
import { csrf } from "@/components/auth-form";
import { LessonTranslationToggle } from "@/components/translation";

export function LessonReader({ lesson }: { lesson: Lesson }) {
  const [showMyanmar, setShowMyanmar] = useState(false);
  const [exampleIndex, setExampleIndex] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [message, setMessage] = useState("");
  const example = lesson.code_examples[exampleIndex];

  async function complete() {
    setMessage("");
    try { await api.progress(lesson.id, true, csrf()); setCompleted(true); setMessage("Lesson marked complete."); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Sign in and enroll to save progress."); }
  }
  async function toggleBookmark() {
    setMessage("");
    try { const result = await api.bookmark(lesson.id, csrf()); setBookmarked(result.bookmarked); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Sign in to bookmark this lesson."); }
  }

  return <div>
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3"><LessonTranslationToggle onChange={setShowMyanmar}/><div className="flex gap-2"><button onClick={toggleBookmark} className={`rounded-lg border px-3 py-2 text-sm ${bookmarked ? "border-indigo-400 bg-indigo-500/15 text-indigo-200" : "border-line text-slate-300"}`} aria-pressed={bookmarked}>{bookmarked ? "Bookmarked" : "Bookmark"}</button><button onClick={complete} disabled={completed} className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold disabled:opacity-60">{completed ? "Completed" : "Mark complete"}</button></div></div>
    {message && <p className="mb-5 rounded-lg border border-line bg-surface px-4 py-3 text-sm text-slate-300" role="status">{message}</p>}
    <div className="prose prose-invert max-w-none whitespace-pre-line text-slate-300">{lesson.content_en}</div>
    {showMyanmar && <div className="mt-7 rounded-xl border border-indigo-400/20 bg-indigo-500/5 p-5 leading-8 text-slate-300">{lesson.content_mm ?? "Myanmar explanation is not available for this lesson yet."}</div>}
    {lesson.code_examples.length > 0 && <section className="mt-10" aria-label="Read-only code examples"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-bold">Explained examples</h2><p className="mt-1 text-sm text-slate-500">Read the code and expected behavior before trying it yourself.</p></div><div className="flex gap-2" role="tablist" aria-label="Code examples">{lesson.code_examples.map((item, index) => <button key={item.id} role="tab" aria-selected={index === exampleIndex} onClick={() => setExampleIndex(index)} className={`rounded-lg px-3 py-2 text-xs ${index === exampleIndex ? "bg-indigo-500/20 text-indigo-200" : "bg-surface text-slate-400"}`}>{index + 1}</button>)}</div></div><div className="mt-4 overflow-hidden rounded-2xl border border-line bg-[#0d1528]"><div className="flex items-center justify-between border-b border-line px-4 py-3 text-xs text-slate-500"><span>{example?.filename ?? `${example?.language ?? "code"} example`}</span><button onClick={() => example && navigator.clipboard?.writeText(example.code)} className="text-indigo-300 hover:text-white">Copy code</button></div><pre className="overflow-x-auto p-5 text-sm leading-7 text-slate-200"><code>{example?.code}</code></pre>{example?.description && <div className="border-t border-line bg-surface/60 p-5 text-sm leading-7 text-slate-300">{example.description}</div>}</div></section>}
  </div>;
}

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, EmptyState, Skeleton } from "@/components/ui";
import { communityApi } from "@/lib/ai-api";

export default function Questions() {
  const params = useSearchParams();
  const [items, setItems] = useState<any[] | null>(null);
  const [unanswered, setUnanswered] = useState(false);
  const [error, setError] = useState("");
  const load = (onlyUnanswered = unanswered) => { setItems(null); setError(""); communityApi.feed("", "question", { ...(onlyUnanswered ? { status: "unanswered" } : {}), course_id: params.get("course_id") || undefined, lesson_id: params.get("lesson_id") || undefined }).then(response => setItems(response.items ?? [])).catch(cause => { setItems([]); setError(cause instanceof Error ? cause.message : "Unable to load questions."); }); };
  // The initial request intentionally uses the first filter state.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(false); }, []);
  return <section className="mx-auto max-w-5xl px-5 py-12 lg:px-8"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-indigo-300">Community Q&A</p><h1 className="mt-2 text-4xl font-bold">Questions</h1><p className="mt-3 text-slate-400">Find answers from developers building alongside you.</p></div><Link href="/community/questions/ask?type=question" className="rounded-xl bg-primary px-4 py-3 text-sm font-semibold">Ask a question</Link></div><div className="mt-8 flex gap-2"><button onClick={() => { setUnanswered(false); load(false); }} className={`rounded-full px-4 py-2 text-sm ${!unanswered ? "bg-primary" : "bg-surface text-slate-400"}`}>All questions</button><button onClick={() => { setUnanswered(true); load(true); }} className={`rounded-full px-4 py-2 text-sm ${unanswered ? "bg-primary" : "bg-surface text-slate-400"}`}>Unanswered</button></div>{error && <Card className="mt-5 border-red-400/30 p-5 text-red-200" role="alert"><p>{error}</p><button className="mt-3 underline" onClick={() => load()}>Retry</button></Card>}<div className="mt-5 space-y-3">{items === null ? [1, 2, 3].map(index => <Skeleton className="h-32" key={index} />) : items.map(item => <Link key={item.id} href={`/community/questions/${item.slug}`}><Card className="p-5 hover:bg-elevated"><div className="flex flex-wrap gap-2 text-xs text-slate-500">{item.tags?.map((tag: string) => <span key={tag}>#{tag}</span>)}</div><h2 className="mt-2 font-semibold">{item.title}</h2><p className="mt-2 line-clamp-2 text-sm text-slate-400">{item.body}</p><p className="mt-4 text-xs text-slate-500">{item.vote_count ?? 0} votes · {item.answer_count ?? 0} answers · {item.comment_count ?? 0} replies</p></Card></Link>)}{items !== null && !items.length && <EmptyState title={unanswered ? "Every question has a solution" : "No questions yet"} description={unanswered ? "Check back soon or start a new question." : "Ask the first question in this community."} />}</div></section>;
}

import Link from "next/link";
import { notFound } from "next/navigation";
import { Code2 } from "lucide-react";
import { syntaxApi } from "@/lib/api";
import { Badge, Card } from "@/components/ui";
import { SyntaxExample } from "@/components/syntax-reference-section";

export default async function SyntaxReferencePage({ params }: { params: Promise<{ slug: string; referenceSlug: string }> }) {
  const { slug, referenceSlug } = await params;
  let reference;
  try { reference = await syntaxApi.reference(slug, referenceSlug); } catch { notFound(); }
  return <section className="mx-auto max-w-5xl px-5 py-12 lg:px-8"><Link className="text-sm text-indigo-300 hover:text-white" href={`/courses/${slug}#syntax-reference`}>← All syntax references</Link><div className="mt-8"><p className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[.16em] text-indigo-300"><Code2 size={16}/> {reference.category}</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight">{reference.title}</h1><p className="mt-4 max-w-3xl text-lg leading-8 text-slate-400">{reference.description}</p></div><div className="mt-8 grid gap-4 md:grid-cols-3"><Card className="p-5 md:col-span-2"><p className="text-[10px] font-semibold uppercase tracking-[.16em] text-indigo-300">Basic syntax</p><pre className="mt-3 overflow-x-auto whitespace-pre-wrap font-mono text-sm leading-7 text-indigo-100"><code>{reference.basic_syntax}</code></pre></Card><Card className="p-5"><p className="text-[10px] font-semibold uppercase tracking-[.16em] text-slate-500">When to use it</p><p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-300">{reference.when_to_use}</p></Card></div><Card className="mt-4 border-amber-400/15 bg-amber-400/5 p-5"><p className="text-[10px] font-semibold uppercase tracking-[.16em] text-amber-200">Important notes</p><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-amber-100/80">{reference.important_notes}</p></Card><div className="mt-8 flex items-end justify-between gap-3"><div><p className="text-sm font-semibold uppercase tracking-[.16em] text-indigo-300">Examples 1–5</p><h2 className="mt-2 text-2xl font-bold">Syntax in context</h2></div><Badge>5 reviewed examples</Badge></div><div className="mt-5 space-y-4">{reference.examples.slice().sort((a, b) => a.example_number - b.example_number).map(example => <SyntaxExample key={example.id} example={example}/>)}</div></section>;
}

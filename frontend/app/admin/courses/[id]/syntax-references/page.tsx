"use client";

import Link from "next/link";
import { ArrowLeft, Archive, Check, Code2, Eye, EyeOff, Plus, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { csrf } from "@/components/auth-form";
import { Badge, Button, Card } from "@/components/ui";
import { syntaxApi } from "@/lib/api";
import type { SyntaxReference, SyntaxReferenceExample } from "@/lib/types";

const inputClass = "mt-1 w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm text-slate-200 outline-none focus:border-indigo-400";
const areaClass = `${inputClass} min-h-24 leading-6`;

type DraftExample = Omit<SyntaxReferenceExample, "id" | "reference_id"> & { id?: string };
type DraftReference = Omit<SyntaxReference, "id" | "course_id" | "examples" | "status"> & { id?: string; status?: string; examples: DraftExample[] };

function emptyExample(number: number): DraftExample {
  return { example_number: number, title: `Example ${number}`, code: "", language: "text", expected_output: "", explanation: "" };
}

function emptyReference(): DraftReference {
  return { title: "", slug: "", category: "Basics", description: "", basic_syntax: "", when_to_use: "", important_notes: "", display_order: 0, status: "draft", examples: [emptyExample(1)] };
}

function toDraft(item: SyntaxReference): DraftReference {
  return { ...item, examples: item.examples.slice().sort((a, b) => a.example_number - b.example_number) };
}

function payload(draft: DraftReference) {
  return { ...draft, title: draft.title.trim(), slug: draft.slug.trim(), category: draft.category.trim(), description: draft.description.trim(), basic_syntax: draft.basic_syntax.trim(), when_to_use: draft.when_to_use.trim(), important_notes: draft.important_notes.trim(), display_order: Number(draft.display_order), examples: draft.examples.map(example => ({ example_number: Number(example.example_number), title: example.title.trim(), code: example.code, language: example.language.trim() || "text", expected_output: example.expected_output, explanation: example.explanation.trim() })) };
}

export default function SyntaxReferencesAdmin({ params }: { params: Promise<{ id: string }> }) {
  const [courseId, setCourseId] = useState("");
  const [items, setItems] = useState<SyntaxReference[]>([]);
  const [draft, setDraft] = useState<DraftReference | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  async function load(id: string) {
    setLoading(true);
    try { setItems(await syntaxApi.adminList(id)); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to load syntax references."); } finally { setLoading(false); }
  }

  useEffect(() => { params.then(p => { setCourseId(p.id); void load(p.id); }); }, [params]);

  const sortedItems = useMemo(() => items.slice().sort((a, b) => a.display_order - b.display_order || a.title.localeCompare(b.title)), [items]);
  const updateDraft = (patch: Partial<DraftReference>) => setDraft(current => current ? { ...current, ...patch } : current);
  const updateExample = (index: number, patch: Partial<DraftExample>) => setDraft(current => current ? { ...current, examples: current.examples.map((example, itemIndex) => itemIndex === index ? { ...example, ...patch } : example) } : current);

  function startNew() { setMessage(""); setDraft(emptyReference()); }
  function edit(item: SyntaxReference) { setMessage(""); setDraft(toDraft(item)); }
  function addExample() { setDraft(current => current && current.examples.length < 5 ? { ...current, examples: [...current.examples, emptyExample(current.examples.length + 1)] } : current); }
  function removeExample(index: number) { setDraft(current => current && current.examples.length > 1 ? { ...current, examples: current.examples.filter((_, itemIndex) => itemIndex !== index).map((example, itemIndex) => ({ ...example, example_number: itemIndex + 1 })) } : current); }

  async function save() {
    if (!draft) return;
    const next = payload(draft);
    if (next.title.length < 3 || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(next.slug)) { setMessage("Add a title and a lowercase hyphenated slug before saving."); return; }
    if (next.examples.some(example => !example.title || !example.code.trim() || example.explanation.length < 10)) { setMessage("Each example needs a title, code, and an explanation of at least 10 characters."); return; }
    setBusy(true);
    try {
      const saved = draft.id ? await syntaxApi.adminUpdate(draft.id, next, csrf()) : await syntaxApi.adminCreate(courseId, next, csrf());
      setItems(current => current.some(item => item.id === saved.id) ? current.map(item => item.id === saved.id ? saved : item) : [...current, saved]);
      setDraft(toDraft(saved));
      setMessage("Syntax reference saved as a draft.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to save syntax reference."); } finally { setBusy(false); }
  }

  async function changeStatus(action: "publish" | "unpublish" | "archive") {
    if (!draft?.id) return;
    if (action === "publish" && draft.examples.length !== 5) { setMessage("Publishing requires exactly five examples numbered 1 through 5."); return; }
    setBusy(true);
    try {
      const saved = action === "publish" ? await syntaxApi.publish(draft.id, csrf()) : action === "unpublish" ? await syntaxApi.unpublish(draft.id, csrf()) : await syntaxApi.archive(draft.id, csrf());
      setItems(current => current.map(item => item.id === saved.id ? saved : item));
      setDraft(toDraft(saved));
      setMessage(action === "archive" ? "Syntax reference archived." : action === "publish" ? "Syntax reference published." : "Syntax reference returned to draft.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to change syntax reference status."); } finally { setBusy(false); }
  }

  return <div className="mx-auto max-w-[1400px]">
    <div className="flex flex-wrap items-center justify-between gap-4"><div><Link className="inline-flex items-center gap-2 text-sm text-indigo-300 hover:text-indigo-200" href={`/admin/courses/${courseId}/builder`}><ArrowLeft size={15}/>Back to course builder</Link><p className="mt-4 text-sm font-semibold uppercase tracking-[.16em] text-indigo-300">Course content</p><h1 className="mt-2 text-3xl font-bold">Syntax references</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Build compact, course-scoped references. Drafts may be incomplete; public entries must contain examples 1 through 5.</p></div><Button onClick={startNew} className="inline-flex items-center gap-2"><Plus size={16}/>New reference</Button></div>
    {message && <p className="mt-5 rounded-xl border border-indigo-400/20 bg-indigo-500/10 px-4 py-3 text-sm text-indigo-100" role="status">{message}</p>}
    <div className="mt-7 grid gap-5 xl:grid-cols-[290px_minmax(0,1fr)]"><Card className="h-fit overflow-hidden p-3"><div className="flex items-center justify-between border-b border-line/70 px-2 pb-3"><div><span className="block text-[10px] font-bold uppercase tracking-[.18em] text-slate-500">Reference library</span><span className="mt-1 block text-xs text-slate-600">Course scoped entries</span></div><span className="rounded-full bg-white/[.04] px-2 py-1 text-xs font-semibold text-slate-500">{items.length}</span></div>{loading ? <p className="p-3 text-sm text-slate-500">Loading…</p> : sortedItems.length ? <div className="space-y-1 pt-2">{sortedItems.map(item => <button key={item.id} type="button" onClick={() => edit(item)} className={`w-full rounded-xl px-3 py-3 text-left transition ${draft?.id === item.id ? "bg-indigo-500/15 text-indigo-100 shadow-[inset_2px_0_0_#818cf8]" : "text-slate-400 hover:bg-elevated hover:text-white"}`}><span className="flex items-center justify-between gap-2"><span className="truncate text-sm font-medium">{item.title}</span><Badge className={item.status === "published" ? "bg-emerald-400/10 text-emerald-300" : item.status === "archived" ? "bg-slate-500/20 text-slate-400" : "bg-amber-400/10 text-amber-200"}>{item.status}</Badge></span><span className="mt-1 block text-xs text-slate-600">{item.category} · {item.examples.length}/5 examples</span></button>)}</div> : <div className="p-3 pt-5"><div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/10 text-indigo-300"><Code2 size={18}/></div><p className="mt-3 text-sm font-semibold text-slate-300">Your library is empty</p><p className="mt-1 text-xs leading-5 text-slate-500">Create a reference to give learners a focused syntax guide.</p><button type="button" onClick={startNew} className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-300 hover:text-indigo-200"><Plus size={14}/>Create reference</button></div>}</Card>
      {draft ? <Card className="p-5 sm:p-7"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-semibold text-indigo-300">{draft.id ? "Edit reference" : "New reference"}</p><h2 className="mt-1 text-2xl font-bold">Reference details</h2></div>{draft.id && <Badge className={draft.status === "published" ? "bg-emerald-400/10 text-emerald-300" : draft.status === "archived" ? "bg-slate-500/20 text-slate-400" : "bg-amber-400/10 text-amber-200"}>{draft.status}</Badge>}</div><div className="mt-6 grid gap-4 md:grid-cols-2"><label className="text-sm text-slate-300">Title<input className={inputClass} value={draft.title} onChange={event => updateDraft({ title: event.target.value })}/></label><label className="text-sm text-slate-300">Slug<input className={inputClass} value={draft.slug} onChange={event => updateDraft({ slug: event.target.value })}/></label><label className="text-sm text-slate-300">Category<input className={inputClass} value={draft.category} onChange={event => updateDraft({ category: event.target.value })}/></label><label className="text-sm text-slate-300">Display order<input type="number" min="0" className={inputClass} value={draft.display_order} onChange={event => updateDraft({ display_order: Number(event.target.value) })}/></label></div><label className="mt-4 block text-sm text-slate-300">Description<textarea className={areaClass} value={draft.description} onChange={event => updateDraft({ description: event.target.value })}/></label><div className="mt-4 grid gap-4 md:grid-cols-3"><label className="text-sm text-slate-300">Basic syntax<textarea className={`${areaClass} font-mono`} value={draft.basic_syntax} onChange={event => updateDraft({ basic_syntax: event.target.value })}/></label><label className="text-sm text-slate-300">When to use<textarea className={areaClass} value={draft.when_to_use} onChange={event => updateDraft({ when_to_use: event.target.value })}/></label><label className="text-sm text-slate-300">Important notes<textarea className={areaClass} value={draft.important_notes} onChange={event => updateDraft({ important_notes: event.target.value })}/></label></div><div className="mt-8 flex flex-wrap items-center justify-between gap-3"><div><h3 className="text-lg font-semibold">Examples <span className="text-sm font-normal text-slate-500">{draft.examples.length}/5</span></h3><p className="mt-1 text-sm text-slate-500">The API keeps example numbers ordered. Publish is available only when all five are complete.</p></div>{draft.examples.length < 5 && <Button type="button" onClick={addExample} className="inline-flex items-center gap-2 bg-surface text-slate-200 hover:bg-elevated"><Plus size={15}/>Add example</Button>}</div><div className="mt-4 space-y-4">{draft.examples.map((example, index) => <div className="rounded-xl border border-line bg-ink/60 p-4" key={example.id ?? `new-${index}`}><div className="flex items-center justify-between gap-3"><span className="text-sm font-semibold text-indigo-200">Example {index + 1}</span>{draft.examples.length > 1 && <button type="button" onClick={() => removeExample(index)} className="inline-flex items-center gap-1 text-xs text-red-300 hover:text-red-200"><Trash2 size={13}/>Remove</button>}</div><div className="mt-3 grid gap-3 md:grid-cols-[1fr_160px]"><label className="text-sm text-slate-300">Title<input className={inputClass} value={example.title} onChange={event => updateExample(index, { title: event.target.value })}/></label><label className="text-sm text-slate-300">Language<input className={inputClass} value={example.language} onChange={event => updateExample(index, { language: event.target.value })}/></label></div><label className="mt-3 block text-sm text-slate-300">Code<textarea className={`${areaClass} min-h-40 font-mono`} value={example.code} onChange={event => updateExample(index, { code: event.target.value })}/></label><label className="mt-3 block text-sm text-slate-300">Expected output / preview<textarea className={areaClass} value={example.expected_output} onChange={event => updateExample(index, { expected_output: event.target.value })}/></label><label className="mt-3 block text-sm text-slate-300">Explanation<textarea className={areaClass} value={example.explanation} onChange={event => updateExample(index, { explanation: event.target.value })}/></label></div>)}</div><div className="mt-7 flex flex-wrap gap-2 border-t border-line pt-5"><Button disabled={busy} onClick={save} className="inline-flex items-center gap-2"><Save size={16}/>{busy ? "Saving…" : "Save draft"}</Button>{draft.id && draft.status !== "published" && <Button disabled={busy} onClick={() => void changeStatus("publish")} className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500"><Check size={16}/>Publish</Button>}{draft.id && draft.status === "published" && <Button disabled={busy} onClick={() => void changeStatus("unpublish")} className="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-500"><EyeOff size={16}/>Unpublish</Button>}{draft.id && draft.status !== "archived" && <Button disabled={busy} onClick={() => void changeStatus("archive")} className="inline-flex items-center gap-2 bg-slate-700 hover:bg-slate-600"><Archive size={16}/>Archive</Button>}<Link href={`/courses/${courseId}`} className="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-400 hover:bg-surface hover:text-white"><Eye size={16}/>View course</Link></div></Card> : <Card className="relative grid min-h-[420px] place-items-center overflow-hidden p-8 text-center"><div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(99,102,241,.14),transparent_16rem)]"/><div className="relative max-w-md"><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl border border-indigo-400/20 bg-indigo-500/10 text-indigo-300 shadow-[0_0_40px_rgba(99,102,241,.12)]"><Code2 size={24}/></div><p className="mt-5 text-[11px] font-bold uppercase tracking-[.2em] text-indigo-300">Reference workspace</p><h2 className="mt-2 text-2xl font-bold tracking-tight">Start your syntax library</h2><p className="mt-3 text-sm leading-6 text-slate-400">Create a focused reference with five progressive examples, expected output, and a clear explanation for learners.</p><div className="mt-6 grid gap-2 text-left sm:grid-cols-3"><div className="rounded-xl border border-line/70 bg-ink/40 p-3"><span className="text-xs font-semibold text-slate-200">01</span><p className="mt-1 text-[11px] leading-5 text-slate-500">Explain the syntax</p></div><div className="rounded-xl border border-line/70 bg-ink/40 p-3"><span className="text-xs font-semibold text-slate-200">02</span><p className="mt-1 text-[11px] leading-5 text-slate-500">Add five examples</p></div><div className="rounded-xl border border-line/70 bg-ink/40 p-3"><span className="text-xs font-semibold text-slate-200">03</span><p className="mt-1 text-[11px] leading-5 text-slate-500">Review and publish</p></div></div><Button onClick={startNew} className="mt-6 inline-flex items-center gap-2"><Plus size={16}/>Create first reference</Button></div></Card>}
    </div>
  </div>;
}

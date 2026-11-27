"use client";

import { ArrowDown, ArrowUp, Check, Eye, Plus, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { roadmapApi } from "@/lib/roadmap-api";
import type { Roadmap } from "@/lib/types";
import { csrf } from "@/components/auth-form";
import { Badge, Button, Card, Skeleton } from "@/components/ui";

type ContentItem = { id:string; title:string; slug?:string|null; published?:boolean|null };

export default function AdminRoadmaps() {
  const [paths, setPaths] = useState<Roadmap[]>([]);
  const [selected, setSelected] = useState<Roadmap | null>(null);
  const [courses, setCourses] = useState<ContentItem[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async (id?: string) => {
    setLoading(true); setError("");
    try {
      const result = await roadmapApi.adminList("?page_size=100");
      setPaths(result.items);
      const next = id ? await roadmapApi.adminDetail(id) : selected ? await roadmapApi.adminDetail(selected.id) : result.items[0] ? await roadmapApi.adminDetail(result.items[0].id) : null;
      setSelected(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load the path builder"); }
    finally { setLoading(false); }
  };
  // Load the selected draft once on mount; subsequent refreshes are explicit.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { void load(); roadmapApi.adminContent("course", "&limit=100").then(setCourses).catch(() => setCourses([])); }, []);

  const create = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setMessage("");
    const data = Object.fromEntries(new FormData(event.currentTarget));
    try { const created = await roadmapApi.adminCreate({ ...data, estimated_hours: Number(data.estimated_hours || 0), goals: [], skills: [], completion_rules: {} }, csrf()) as { id:string }; event.currentTarget.reset(); await load(created.id); setMessage("Draft created."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to create draft"); }
  };
  const update = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (!selected) return; const data = Object.fromEntries(new FormData(event.currentTarget));
    try { await roadmapApi.adminUpdate(selected.id, { ...data, estimated_hours: Number(data.estimated_hours || 0) }, csrf()); await load(selected.id); setMessage("Draft saved."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to save draft"); }
  };
  const addStage = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (!selected) return; const data = Object.fromEntries(new FormData(event.currentTarget));
    try { await roadmapApi.adminStage(selected.id, { ...data, position: selected.stages?.length ?? 0, objectives: [], skills: [], completion_rules: {} }, csrf()); event.currentTarget.reset(); await load(selected.id); setMessage("Stage added."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to add stage"); }
  };
  const addStep = async (event: React.FormEvent<HTMLFormElement>, stageId: string, position: number) => {
    event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget));
    try { await roadmapApi.adminStep(stageId, { ...data, position }, csrf()); event.currentTarget.reset(); await load(selected?.id); setMessage("Step added."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to add step"); }
  };
  const linkCourse = async (stepId: string, courseId: string) => {
    if (!courseId) return;
    try { await roadmapApi.adminResource(stepId, { resource_type: "course", resource_id: courseId }, csrf()); await load(selected?.id); setMessage("Existing course linked."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to link course"); }
  };
  const moveStage = async (index: number, direction: number) => {
    if (!selected?.stages) return; const next = [...selected.stages]; const target = index + direction; if (target < 0 || target >= next.length) return; [next[index], next[target]] = [next[target], next[index]];
    try { await roadmapApi.adminReorderStages(selected.id, next.map(stage => stage.id), csrf()); await load(selected.id); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to reorder stages"); }
  };
  const transition = async (action: "review" | "approve" | "publish") => {
    if (!selected) return;
    try { if (action === "review") await roadmapApi.adminSubmitReview(selected.id, csrf()); if (action === "approve") await roadmapApi.adminApprove(selected.id, csrf()); if (action === "publish") await roadmapApi.adminPublish(selected.id, csrf()); await load(selected.id); setMessage(action === "review" ? "Submitted for review." : action === "approve" ? "Path approved." : "Path published."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to change publication state"); }
  };

  return <section className="mx-auto max-w-7xl"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Learning Paths</p><h1 className="mt-2 text-3xl font-bold">Path builder and publication</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">Create a persisted roadmap, link existing published courses, review its structure, and publish only after validation.</p></div><Button onClick={() => void load(selected?.id)}><Save size={16} /> Refresh</Button></div>
    {error && <Card className="mt-6 border-red-400/20 bg-red-500/[.06] p-4 text-sm text-red-200" role="alert">{error}</Card>}{message && <p className="mt-4 text-sm text-emerald-300" role="status">{message}</p>}
    <div className="mt-8 grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]"><Card className="p-4"><div className="flex items-center justify-between"><h2 className="font-semibold">Saved paths</h2><span className="text-xs text-slate-500">{paths.length}</span></div>{loading ? <div className="mt-4 space-y-2"><Skeleton className="h-10" /><Skeleton className="h-10" /></div> : <div className="mt-4 space-y-2">{paths.map(path => <button key={path.id} onClick={() => void load(path.id)} className={`w-full rounded-xl p-3 text-left transition ${selected?.id === path.id ? "bg-indigo-500/20 text-indigo-100" : "bg-elevated/60 text-slate-300 hover:bg-elevated"}`}><span className="block truncate text-sm font-semibold">{path.title}</span><span className="mt-1 flex items-center justify-between text-xs text-slate-500"><span>{path.slug}</span><Badge>{path.status}</Badge></span></button>)}</div>}
      <form onSubmit={create} className="mt-6 space-y-3 border-t border-line pt-5"><h3 className="text-sm font-semibold">Create draft</h3><input required name="title" placeholder="Path title" className="w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input required name="slug" pattern="[a-z0-9-]+" placeholder="stable-slug" className="w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input required name="career_category" placeholder="Category" className="w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input name="estimated_hours" type="number" min="0" placeholder="Estimated hours" className="w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><Button className="w-full"><Plus size={16} /> Create</Button></form></Card>
      <div className="min-w-0">{!selected ? <Card className="p-8 text-slate-400">Create or select a learning path to edit it.</Card> : <><Card className="p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-3"><Badge>{selected.status}</Badge><span className="text-xs text-slate-500">{selected.slug}</span></div><h2 className="mt-3 text-2xl font-bold">{selected.title}</h2><p className={`mt-2 text-xs ${selected.translation_available ? "text-emerald-300" : "text-amber-300"}`}>{selected.translation_available ? "Burmese translation complete" : `Burmese translation missing ${selected.translation_missing?.length ?? 0} sections`}</p></div><div className="flex flex-wrap gap-2"><Button onClick={() => void transition("review")} disabled={selected.status !== "draft"}><Check size={15} /> Submit review</Button><Button onClick={() => void transition("approve")} disabled={selected.status !== "in_review"}><Check size={15} /> Approve</Button><Button onClick={() => void transition("publish")} disabled={selected.status !== "approved"}><Eye size={15} /> Publish</Button></div></div><form onSubmit={update} className="mt-6 grid gap-3 md:grid-cols-2"><input required name="title" defaultValue={selected.title_en ?? selected.title} placeholder="English title" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input name="title_mm" defaultValue={selected.title_mm ?? ""} placeholder="မြန်မာခေါင်းစဉ်" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input required name="career_category" defaultValue={selected.career_category} placeholder="Category" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input name="estimated_hours" type="number" min="0" defaultValue={selected.estimated_hours} placeholder="Estimated hours" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><textarea required name="description_en" defaultValue={selected.description_en} placeholder="English description" rows={4} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm md:col-span-2" /><textarea name="description_mm" defaultValue={selected.description_mm ?? ""} placeholder="မြန်မာဖော်ပြချက်" rows={4} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm md:col-span-2" /><Button className="md:col-span-2"><Save size={16} /> Save draft</Button></form></Card>
        <Card className="mt-6 p-6"><div className="flex items-center justify-between gap-3"><div><h2 className="text-xl font-bold">Stages and linked courses</h2><p className="mt-1 text-sm text-slate-400">Keep ordering stable and link only real content records.</p></div><span className="text-sm text-slate-500">{selected.stages?.length ?? 0} stages</span></div><div className="mt-5 space-y-4">{selected.stages?.map((stage, index) => <Card className="p-4" key={stage.id}><div className="flex flex-wrap items-start justify-between gap-3"><div><Badge>{stage.level}</Badge><h3 className="mt-2 font-semibold">{stage.title}</h3><p className="mt-1 text-sm text-slate-400">{stage.description_en}</p></div><div className="flex gap-1"><button aria-label={`Move ${stage.title} up`} className="rounded-lg border border-line p-2 text-slate-400 disabled:opacity-30" disabled={index === 0} onClick={() => void moveStage(index, -1)}><ArrowUp size={15} /></button><button aria-label={`Move ${stage.title} down`} className="rounded-lg border border-line p-2 text-slate-400 disabled:opacity-30" disabled={index === (selected.stages?.length ?? 1) - 1} onClick={() => void moveStage(index, 1)}><ArrowDown size={15} /></button></div></div><div className="mt-4 space-y-3">{stage.steps.map(step => <div className="rounded-xl bg-ink p-3" key={step.id}><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="font-medium">{step.title}</p><p className="mt-1 text-xs text-slate-500">{step.instructions_en}</p></div><select aria-label={`Link a course to ${step.title}`} defaultValue="" onChange={event => void linkCourse(step.id, event.target.value)} className="max-w-full rounded-lg border border-line bg-surface px-2 py-2 text-xs"><option value="">Link existing course…</option>{courses.filter(course => course.published).map(course => <option key={course.id} value={course.id}>{course.title}</option>)}</select></div><div className="mt-3 flex flex-wrap gap-2">{step.resources.map(resource => <span className="rounded-lg bg-elevated px-2 py-1 text-xs text-slate-400" key={`${resource.resource_type}-${resource.resource_id}`}>{resource.title || resource.resource_type}</span>)}</div></div>)}<form onSubmit={event => void addStep(event, stage.id, stage.steps.length)} className="flex flex-wrap gap-2"><input required name="title" placeholder="New step title" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input name="instructions_en" placeholder="Instructions" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><Button><Plus size={15} /> Step</Button></form></div></Card>)}</div><form onSubmit={addStage} className="mt-5 grid gap-2 md:grid-cols-3"><input required name="title" placeholder="New stage title" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><input name="description_en" placeholder="Stage description" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm" /><select name="level" defaultValue="beginner" className="rounded-lg border border-line bg-ink px-3 py-2 text-sm"><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option><option value="professional">Professional</option></select><Button className="md:col-span-3"><Plus size={15} /> Add stage</Button></form></Card>
      </>}</div>
    </div>
  </section>;
}

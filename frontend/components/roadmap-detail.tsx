"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, Bookmark, CheckCircle2, Clock3, LockKeyhole, Play } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { LearningPathEnrollment, Roadmap, RoadmapResource } from "@/lib/types";
import { roadmapApi } from "@/lib/roadmap-api";
import { csrf } from "@/components/auth-form";
import { useI18n } from "@/lib/i18n";
import { Badge, Button, Card, EmptyState, Skeleton } from "@/components/ui";

function resourceHref(resource: RoadmapResource) {
  return resource.href || (resource.resource_type === "course" && resource.slug ? `/courses/${resource.slug}` : null);
}

export function RoadmapDetail({ roadmap }: { roadmap: Roadmap }) {
  const { locale } = useI18n();
  const my = locale === "my";
  const [enrollment, setEnrollment] = useState<LearningPathEnrollment | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [loadingAccount, setLoadingAccount] = useState(true);
  const [accountAvailable, setAccountAvailable] = useState(false);

  useEffect(() => {
    let active = true;
    roadmapApi.mine().then(items => {
      if (!active) return;
      const current = items.find(item => item.roadmap_id === roadmap.id) ?? null;
      setEnrollment(current);
      setSaved(Boolean(current?.bookmarked));
      setAccountAvailable(true);
    }).catch(() => {
      if (active) setAccountAvailable(false);
    }).finally(() => {
      if (active) setLoadingAccount(false);
    });
    return () => { active = false; };
  }, [roadmap.id]);

  const title = my && roadmap.title_mm ? roadmap.title_mm : roadmap.title;
  const description = my && roadmap.description_mm ? roadmap.description_mm : (roadmap.description ?? roadmap.description_en);
  const prerequisites = my && roadmap.prerequisites_mm ? roadmap.prerequisites_mm : roadmap.prerequisites_en;
  const outcomes = my && roadmap.outcomes_mm ? roadmap.outcomes_mm : (roadmap.outcomes ?? roadmap.outcomes_en);
  const firstResource = useMemo(() => roadmap.stages?.flatMap(stage => stage.steps).flatMap(step => step.resources).map(resourceHref).find(Boolean) ?? `/learning-paths/${roadmap.slug}`, [roadmap]);
  const resumeHref = enrollment?.progress.resume?.href || firstResource;
  const progress = enrollment?.progress;
  const hasTranslation = Boolean(roadmap.translation_available);
  const localize = (english: string | null | undefined, burmese: string | null | undefined) => my && burmese ? burmese : (english ?? "");

  const start = async () => {
    setBusy(true); setMessage("");
    try {
      const result = await roadmapApi.start(roadmap.slug, csrf());
      const items = await roadmapApi.mine();
      setEnrollment(items.find(item => item.id === result.id || item.roadmap_id === roadmap.id) ?? null);
      setAccountAvailable(true);
      setMessage(my ? "လေ့လာရေးလမ်းကြောင်းကို စတင်ပြီးပါပြီ။" : "Learning path added to your dashboard.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : (my ? "စတင်၍ မရသေးပါ။" : "Unable to start this path."));
    } finally { setBusy(false); }
  };

  const bookmarkPath = async () => {
    setBusy(true);
    try {
      const result = await roadmapApi.bookmark(roadmap.id, csrf());
      setSaved(result.bookmarked);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : (my ? "သိမ်း၍ မရသေးပါ။" : "Unable to save this path."));
    } finally { setBusy(false); }
  };

  return <div>
    {my && !hasTranslation && <div role="status" className="mb-6 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">မြန်မာဘာသာပြန် အပြည့်အစုံ မရရှိသေးပါ။ ရရှိထားသော မြန်မာစာကိုသာ ပြသပြီး ပျောက်ဆုံးသောအပိုင်းများအတွက် အင်္ဂလိပ်အကြောင်းအရာကို fallback အဖြစ် သီးခြားပြသထားပါသည်။</div>}
    <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_320px]">
      <div>
        <div className="max-w-4xl"><Badge>{roadmap.career_category}</Badge><h1 className="mt-4 text-4xl font-extrabold tracking-tight sm:text-6xl">{title}</h1><p className="mt-5 text-lg leading-8 text-slate-300">{description}</p></div>
        <div className="mt-8 grid gap-4 sm:grid-cols-3"><Card className="p-5"><Clock3 className="text-indigo-300" size={19} /><p className="mt-4 text-xs uppercase tracking-[.14em] text-slate-500">{my ? "လေ့လာချိန်" : "Study effort"}</p><p className="mt-1 text-2xl font-bold">{roadmap.estimated_hours ? `${roadmap.estimated_hours}h` : "—"}</p></Card><Card className="p-5"><BookOpen className="text-cyan-300" size={19} /><p className="mt-4 text-xs uppercase tracking-[.14em] text-slate-500">{my ? "သင်တန်းများ" : "Courses"}</p><p className="mt-1 text-2xl font-bold">{roadmap.course_count ?? 0}</p></Card><Card className="p-5"><CheckCircle2 className="text-emerald-300" size={19} /><p className="mt-4 text-xs uppercase tracking-[.14em] text-slate-500">{my ? "အဆင့်များ" : "Stages"}</p><p className="mt-1 text-2xl font-bold">{roadmap.stage_count ?? roadmap.stages?.length ?? 0}</p></Card></div>
        {outcomes && <Card className="mt-6 p-6"><h2 className="text-xl font-bold">{my ? "လေ့လာပြီးနောက် ရရှိမည့်အရာများ" : "Learning outcomes"}</h2><p className="mt-3 leading-7 text-slate-300">{outcomes}</p></Card>}
        {prerequisites && <Card className="mt-5 p-6"><div className="flex items-center gap-3"><LockKeyhole className="text-amber-300" size={19} /><h2 className="text-xl font-bold">{my ? "လိုအပ်ချက်များ" : "Prerequisites"}</h2></div><p className="mt-3 leading-7 text-slate-300">{prerequisites}</p></Card>}
        <div className="mt-12 flex items-end justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[.18em] text-indigo-300">{my ? "လေ့လာရေးမြေပုံ" : "Skill roadmap"}</p><h2 className="mt-2 text-2xl font-bold">{my ? "အဆင့်လိုက် လေ့လာပါ" : "Build skills in the right order"}</h2></div>{progress && <Badge className="bg-emerald-500/15 text-emerald-300">{Math.round(progress.progress_percent)}% complete</Badge>}</div>
        {!roadmap.stages?.length ? <div className="mt-5"><EmptyState title={my ? "အကြောင်းအရာ မပြည့်စုံသေးပါ" : "This path has no published curriculum"} description={my ? "စီမံခန့်ခွဲသူက လေ့လာရေးအဆင့်များကို ပြင်ဆင်နေပါသည်။" : "An administrator needs to add reviewed course content before this path can be used."} /></div> : <div className="mt-6 space-y-5">{roadmap.stages.map((stage, index) => <Card className="p-5 sm:p-7" key={stage.id}><div className="flex gap-4"><div className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-indigo-500/20 font-bold text-indigo-200">{index + 1}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-3"><Badge>{stage.level}</Badge><h3 className="text-xl font-bold">{localize(stage.title_en, stage.title_mm)}</h3></div><p className="mt-3 leading-7 text-slate-400">{localize(stage.description_en, stage.description_mm)}</p><div className="mt-5 space-y-3">{stage.steps.map(step => <div className="rounded-xl border border-line bg-ink/60 p-4" key={step.id}><div className="flex flex-wrap items-start justify-between gap-3"><div><h4 className="font-semibold">{localize(step.title_en, step.title_mm)}</h4><p className="mt-2 text-sm leading-6 text-slate-400">{localize(step.instructions_en, step.instructions_mm)}</p></div>{step.required && <span className="text-xs text-slate-500">{my ? "လိုအပ်သည်" : "Required"}</span>}</div>{step.resources.length > 0 && <div className="mt-4 flex flex-wrap gap-2">{step.resources.map(resource => { const href = resourceHref(resource); return href ? <Link className="inline-flex items-center gap-2 rounded-lg border border-indigo-400/25 bg-indigo-500/10 px-3 py-2 text-xs font-semibold text-indigo-200 hover:bg-indigo-500/20" href={href} key={`${resource.resource_type}-${resource.resource_id}`}><Play size={13} />{resource.title || resource.resource_type}</Link> : <span className="rounded-lg border border-line px-3 py-2 text-xs text-slate-500" key={`${resource.resource_type}-${resource.resource_id}`}>{resource.resource_type}</span>; })}</div>}</div>)}</div></div></div></Card>)}</div>}
      </div>
      <aside className="space-y-5 xl:sticky xl:top-24 xl:self-start"><Card className="p-5 sm:p-6"><p className="text-xs font-semibold uppercase tracking-[.18em] text-slate-500">{my ? "သင့်တိုးတက်မှု" : "Your progress"}</p>{loadingAccount ? <Skeleton className="mt-5 h-24" /> : progress ? <><p className="mt-4 text-4xl font-extrabold">{Math.round(progress.progress_percent)}%</p><div className="mt-4 h-2 rounded-full bg-elevated"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-400" style={{ width: `${Math.min(100, Math.max(0, progress.progress_percent))}%` }} /></div><p className="mt-3 text-sm text-slate-400">{progress.completed_steps}/{progress.total_steps} {my ? "အဆင့်ပြီးဆုံး" : "verified steps complete"}</p></> : <p className="mt-4 text-sm leading-6 text-slate-400">{accountAvailable ? (my ? "စတင်ရန် အောက်ပါခလုတ်ကို နှိပ်ပါ။" : "Start this path to save progress and resume where you left off.") : (my ? "တိုးတက်မှုသိမ်းရန် ဝင်ရောက်ပါ။" : "Sign in to save progress and resume learning.")}</p>}
          <div className="mt-5 grid gap-3">{progress ? <Link href={resumeHref} className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-500">{my ? "ဆက်လေ့လာရန်" : "Continue learning"}<ArrowRight size={16} /></Link> : <Button onClick={() => void start()} disabled={busy || !accountAvailable} className="w-full">{busy ? (my ? "စတင်နေသည်…" : "Starting…") : (my ? "လေ့လာမှု စတင်ရန်" : "Start learning")}</Button>}<Button onClick={() => void bookmarkPath()} disabled={busy || !accountAvailable} className="w-full border border-line bg-transparent text-slate-200 hover:bg-elevated"><Bookmark size={16} className={saved ? "fill-current" : ""} />{saved ? (my ? "သိမ်းထားပြီး" : "Saved") : (my ? "လမ်းကြောင်းသိမ်းရန်" : "Save path")}</Button></div>{message && <p className="mt-4 text-sm text-emerald-300" role="status">{message}</p>}</Card>
        <Card className="p-5"><h2 className="font-semibold">{my ? "ကျွမ်းကျင်မှုများ" : "Skills covered"}</h2><div className="mt-4 flex flex-wrap gap-2">{roadmap.skills?.length ? roadmap.skills.map(skill => <Badge className="bg-elevated text-slate-300" key={skill}>{skill}</Badge>) : <p className="text-sm text-slate-500">{my ? "မသတ်မှတ်ရသေးပါ။" : "Skills will be listed after editorial review."}</p>}</div></Card>
      </aside>
    </div>
  </div>;
}

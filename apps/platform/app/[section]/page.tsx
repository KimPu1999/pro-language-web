"use client";

import Link from "next/link";
import { ArrowLeft, ArrowRight, BookOpen, BriefcaseBusiness, Code2, Compass, FolderCode, Wrench } from "lucide-react";
import { use, useEffect, useState } from "react";

const descriptions: Record<string, string> = { courses: "Published courses and lessons.", projects: "Practical projects with milestones.", challenges: "Practice problems to sharpen your skills.", careers: "Career paths and interview preparation.", tools: "A directory of developer tools.", about: "Learn-Coding makes practical programming education easier to access.", contact: "Questions about a course or account? Contact the Learn-Coding team.", privacy: "Privacy policy.", terms: "Terms of service.", dashboard: "Your learning dashboard.", profile: "Your profile.", achievements: "Your achievements." };
const endpoints: Record<string, string> = { courses: "/api/v1/courses?page_size=12", projects: "/api/v1/projects?page_size=12", challenges: "/api/v1/challenges?page_size=12", careers: "/api/v1/roadmaps?page_size=12" };
const detailPaths: Record<string, string> = { courses: "/courses", projects: "/projects", challenges: "/challenges", careers: "/careers/paths" };
const sectionIcons = { courses: BookOpen, projects: FolderCode, challenges: Code2, careers: BriefcaseBusiness, tools: Wrench } as const;

export default function Section({ params }: { params: Promise<{ section: string }> }) {
  const { section } = use(params);
  const title = section.replaceAll("-", " ").replace(/\b\w/g, character => character.toUpperCase());
  const [data, setData] = useState<any>(null); const [pageData, setPageData] = useState<any>(null); const [pageState, setPageState] = useState<"idle" | "loading" | "not_found" | "error">("idle");
  const endpoint = endpoints[section];
  const Icon = sectionIcons[section as keyof typeof sectionIcons] ?? Compass;

  useEffect(() => {
    if (endpoint) fetch(endpoint).then(response => response.ok ? response.json() : null).then(setData).catch(() => setData(null));
    else if (!["tools", "dashboard", "profile", "achievements"].includes(section)) { setPageState("loading"); fetch(`/api/v1/site/pages/${section}`).then(async response => { if (response.status === 404) { setPageState("not_found"); return null; } if (!response.ok) throw new Error("page request failed"); setPageState("idle"); return response.json(); }).then(setPageData).catch(() => { setPageState("error"); setPageData(null); }); }
  }, [endpoint, section]);

  const items = data?.items ?? [];
  return <section className="mx-auto max-w-6xl px-6 py-16">
    <div className="flex items-center gap-2 text-sm uppercase tracking-[.2em] text-indigo-300"><Icon size={16} aria-hidden="true" /> Learn-Coding</div>
    <h1 className="mt-3 text-4xl font-bold capitalize">{title}</h1>
    <p className="mt-4 max-w-2xl text-slate-400">{descriptions[section] ?? "Explore Learn-Coding."}</p>
    {endpoint && data && <div className="mt-10 grid gap-4 md:grid-cols-3">{items.map((item: any) => <Link key={item.slug ?? item.id} href={`${detailPaths[section]}/${item.slug}`} className="group rounded-xl border border-line bg-surface p-5 hover:border-indigo-400"><div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-300"><Icon size={18} aria-hidden="true" /></div><h2 className="mt-4 font-semibold group-hover:text-indigo-200">{item.title}</h2><p className="mt-2 text-sm text-slate-400">{item.description ?? item.description_en ?? "Published Learn-Coding resource."}</p><span className="mt-4 inline-flex items-center gap-1 text-xs text-indigo-300">Open resource <ArrowRight size={14} aria-hidden="true" /></span></Link>)}</div>}
    {endpoint && data && items.length === 0 && <p className="mt-10 rounded-xl border border-line bg-surface p-5 text-slate-400">No published {title.toLowerCase()} are available yet.</p>}
    {!endpoint && pageData && <article className="prose prose-invert mt-10 max-w-3xl rounded-xl border border-line bg-surface p-6 whitespace-pre-wrap text-slate-300">{pageData.body}</article>}
    {!endpoint && !pageData && pageState === "loading" && <p className="mt-10 rounded-xl border border-line bg-surface p-5 text-slate-400">Loading page…</p>}
    {!endpoint && !pageData && pageState === "not_found" && <p className="mt-10 rounded-xl border border-line bg-surface p-5 text-slate-400">This page is not available.</p>}
    {!endpoint && !pageData && pageState === "error" && <p role="alert" className="mt-10 rounded-xl border border-red-400/20 bg-red-500/10 p-5 text-red-200">Unable to load this page. Please try again later.</p>}
    <Link href="/" className="mt-10 inline-flex items-center gap-2 text-indigo-300"><ArrowLeft size={16} aria-hidden="true" /> Back home</Link>
  </section>;
}

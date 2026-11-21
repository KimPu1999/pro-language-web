"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, FolderCode, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export default function Home() {
  const [branding, setBranding] = useState({ website_name: "Learn-Coding", tagline: "Learn to code. Build your future." }); const [homepage, setHomepage] = useState<any>();

  useEffect(() => {
    fetch("/api/v1/site/branding").then(response => response.ok ? response.json() : null).then(value => value && setBranding({ website_name: value.website_name || "Learn-Coding", tagline: value.tagline || "Learn to code. Build your future." })).catch(() => undefined);
    fetch("/api/v1/site/homepage").then(response => response.ok ? response.json() : null).then(setHomepage).catch(() => undefined);
  }, []);

  return <section className="mx-auto max-w-6xl px-6 py-20 sm:py-24">
    <div className="max-w-4xl">
      <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[.2em] text-indigo-300"><Sparkles size={16} aria-hidden="true" /> {branding.website_name}</div>
      <h1 className="mt-4 max-w-3xl text-5xl font-bold tracking-tight sm:text-7xl">{homepage?.hero_title || "Learn to code. Build real projects."}</h1>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">{homepage?.hero_description || branding.tagline}</p>
      {homepage?.announcement && <p className="mt-5 rounded-xl border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-indigo-100">{homepage.announcement}</p>}
      <div className="mt-8 flex flex-wrap gap-3">
        <Link href={homepage?.hero_cta_href || "/courses"} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 font-semibold transition hover:bg-primary-hover"><BookOpen size={18} aria-hidden="true" /> {homepage?.hero_cta_label || "Explore courses"} <ArrowRight size={16} aria-hidden="true" /></Link>
        <Link href="/projects" className="inline-flex items-center gap-2 rounded-lg border border-line px-5 py-3 font-semibold transition hover:bg-surface-hover"><FolderCode size={18} aria-hidden="true" /> View projects</Link>
      </div>
    </div>
    {homepage?.featured_courses?.length > 0 && homepage?.sections?.find((section: any) => section.key === "featured-courses" && section.visible) && <div className="mt-20"><h2 className="text-2xl font-semibold">Featured courses</h2><div className="mt-5 grid gap-4 md:grid-cols-3">{homepage.featured_courses.map((course: any) => <Link key={course.id} href={`/courses/${course.slug}`} className="rounded-2xl border border-line bg-surface p-5 transition hover:-translate-y-0.5 hover:border-primary"><p className="font-semibold">{course.title}</p><p className="mt-2 text-sm leading-6 text-slate-400">{course.short_description}</p></Link>)}</div></div>}
    {homepage?.featured_lessons?.length > 0 && homepage?.sections?.find((section: any) => section.key === "featured-lessons" && section.visible) && <div className="mt-12"><h2 className="text-2xl font-semibold">Featured lessons</h2><div className="mt-5 grid gap-4 md:grid-cols-3">{homepage.featured_lessons.map((lesson: any) => <Link key={lesson.id} href={`/courses/${lesson.course_slug}/learn/${lesson.slug}`} className="rounded-2xl border border-line bg-surface p-5 transition hover:-translate-y-0.5 hover:border-primary"><p className="font-semibold">{lesson.title}</p><p className="mt-2 text-sm text-slate-400">{lesson.course_title}</p></Link>)}</div></div>}
  </section>;
}

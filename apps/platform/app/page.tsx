"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, FolderCode, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export default function Home() {
  const [branding, setBranding] = useState({ website_name: "Learn-Coding", tagline: "Learn to code. Build your future." });

  useEffect(() => {
    fetch("/api/v1/site/branding").then(response => response.ok ? response.json() : null).then(value => value && setBranding({ website_name: value.website_name || "Learn-Coding", tagline: value.tagline || "Learn to code. Build your future." })).catch(() => undefined);
  }, []);

  return <section className="mx-auto max-w-6xl px-6 py-20 sm:py-24">
    <div className="max-w-4xl">
      <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[.2em] text-indigo-300"><Sparkles size={16} aria-hidden="true" /> {branding.website_name}</div>
      <h1 className="mt-4 max-w-3xl text-5xl font-bold tracking-tight sm:text-7xl">Learn to code. Build real projects.</h1>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">{branding.tagline}</p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link href="/courses" className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 font-semibold transition hover:bg-primary-hover"><BookOpen size={18} aria-hidden="true" /> Explore courses <ArrowRight size={16} aria-hidden="true" /></Link>
        <Link href="/projects" className="inline-flex items-center gap-2 rounded-lg border border-line px-5 py-3 font-semibold transition hover:bg-surface-hover"><FolderCode size={18} aria-hidden="true" /> View projects</Link>
      </div>
    </div>
  </section>;
}

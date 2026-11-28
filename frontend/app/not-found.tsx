import Link from "next/link";
import { ArrowRight, BookOpen, FolderKanban, LayoutDashboard } from "lucide-react";

export default function NotFound() {
  return (
    <main className="flex min-h-[calc(100dvh-8rem)] items-center justify-center px-5 py-16 sm:px-8" aria-labelledby="not-found-title">
      <div className="w-full max-w-2xl rounded-3xl border border-line bg-surface p-8 text-center shadow-xl shadow-black/10 sm:p-12">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border border-indigo-400/25 bg-indigo-500/10 text-indigo-300" aria-hidden="true">
          <LayoutDashboard size={28} strokeWidth={1.8} />
        </div>
        <p className="mt-7 text-sm font-bold uppercase tracking-[0.24em] text-primary">404</p>
        <h1 id="not-found-title" className="mt-3 text-3xl font-extrabold tracking-tight text-slate-100 sm:text-4xl">Page not found</h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-7 text-slate-400 sm:text-base">The page you requested does not exist or is no longer available. Try one of these destinations instead.</p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400" href="/">
            <LayoutDashboard size={16} aria-hidden="true" /> Return home <ArrowRight size={15} aria-hidden="true" />
          </Link>
          <Link className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-indigo-400/60 hover:bg-surface-hover hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400" href="/courses">
            <BookOpen size={16} aria-hidden="true" /> Explore courses
          </Link>
          <Link className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-indigo-400/60 hover:bg-surface-hover hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400" href="/projects">
            <FolderKanban size={16} aria-hidden="true" /> Explore projects
          </Link>
        </div>
      </div>
    </main>
  );
}

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function NotFound() {
  return <main className="flex min-h-[60vh] items-center justify-center px-5"><div className="max-w-md text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">404</p><h1 className="mt-3 text-3xl font-bold">Page not found</h1><p className="mt-3 text-slate-400">The page you requested does not exist or is no longer available.</p><div className="mt-6 flex flex-wrap justify-center gap-3"><Link className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white" href="/">Return home <ArrowRight size={15} /></Link><Link className="inline-flex rounded-lg border border-line px-4 py-2.5 text-sm font-semibold text-slate-300 hover:bg-surface" href="/courses">Explore courses</Link><Link className="inline-flex rounded-lg border border-line px-4 py-2.5 text-sm font-semibold text-slate-300 hover:bg-surface" href="/projects">Explore projects</Link></div></div></main>;
}

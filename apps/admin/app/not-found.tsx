import Link from "next/link";
import { ArrowRight, BookOpen, FolderCode, House } from "lucide-react";

export default function NotFound() {
  return (
    <main className="flex min-h-[calc(100dvh-8rem)] items-center justify-center px-5 py-16 text-center sm:px-8" aria-labelledby="admin-not-found-title">
      <div className="w-full max-w-2xl rounded-3xl border border-line bg-surface p-8 shadow-panel sm:p-12">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border border-primary/25 bg-primary/10 text-primary" aria-hidden="true">
          <House size={28} strokeWidth={1.8} />
        </div>
        <p className="mt-7 text-sm font-bold uppercase tracking-[0.24em] text-primary">404</p>
        <h1 id="admin-not-found-title" className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">Page Not Found</h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-7 text-muted">This Admin page does not exist or is no longer available.</p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/dashboard" className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60">
            <House size={16} aria-hidden="true" /> Dashboard <ArrowRight size={15} aria-hidden="true" />
          </Link>
          <Link href="/courses" className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-semibold text-muted transition hover:border-primary/60 hover:bg-surface-hover hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60">
            <BookOpen size={16} aria-hidden="true" /> Courses
          </Link>
          <Link href="/projects" className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-semibold text-muted transition hover:border-primary/60 hover:bg-surface-hover hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60">
            <FolderCode size={16} aria-hidden="true" /> Projects
          </Link>
        </div>
      </div>
    </main>
  );
}

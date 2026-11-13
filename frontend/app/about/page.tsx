import Link from "next/link";

export default function AboutPage() {
  return <section className="mx-auto max-w-3xl px-5 py-16 lg:px-8"><p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-300">CodeMaster Academy</p><h1 className="mt-3 text-4xl font-bold">About CodeMaster Academy</h1><p className="mt-6 leading-8 text-slate-300">CodeMaster Academy is a free programming learning platform for curious builders. Learn through courses, practice, projects, and community.</p><Link className="mt-8 inline-block text-sm font-semibold text-indigo-300" href="/">Return home <span aria-hidden="true">→</span></Link></section>;
}

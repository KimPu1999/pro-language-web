import Link from "next/link";

export default function PrivacyPage() {
  return <section className="mx-auto max-w-3xl px-5 py-16 lg:px-8"><p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-300">CodeMaster Academy</p><h1 className="mt-3 text-4xl font-bold">Privacy</h1><p className="mt-6 leading-8 text-slate-300">We design CodeMaster Academy to keep account and learning data protected. Use Privacy Requests to submit an account data request.</p><Link className="mt-8 inline-block text-sm font-semibold text-indigo-300" href="/">Return home <span aria-hidden="true">→</span></Link></section>;
}

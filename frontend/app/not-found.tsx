import Link from "next/link";

export default function NotFound() {
  return <main className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-5 text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">404</p><h1 className="mt-3 text-3xl font-bold text-white">Page not found</h1><p className="mt-3 text-slate-400">The page you requested does not exist.</p><Link href="/" className="mt-6 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-500">Return home</Link></main>;
}

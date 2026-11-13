import Link from "next/link";

export default function NotFound() {
  return <main className="flex min-h-[60vh] items-center justify-center px-5"><div className="max-w-md text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">404</p><h1 className="mt-3 text-3xl font-bold">Page not found</h1><p className="mt-3 text-slate-400">The page you requested does not exist or is no longer available.</p><Link className="mt-6 inline-flex rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white" href="/">Return home</Link></div></main>;
}

"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-5 text-center"><h1 className="text-3xl font-bold text-white">Something went wrong</h1><p className="mt-3 text-slate-400">We could not load this page. Please try again.</p><button type="button" onClick={() => reset()} className="mt-6 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-500">Try again</button></main>;
}

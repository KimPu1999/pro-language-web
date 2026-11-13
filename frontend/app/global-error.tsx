"use client";

export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <html lang="en"><body className="bg-[#0B1020] text-[#F8FAFC]"><main className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center px-5 text-center"><h1 className="text-3xl font-bold">Something went wrong</h1><p className="mt-3 text-slate-400">The application could not render this page.</p><button type="button" onClick={() => reset()} className="mt-6 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold">Reload</button></main></body></html>;
}

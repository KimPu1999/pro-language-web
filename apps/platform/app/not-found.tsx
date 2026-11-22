import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center px-6 text-center">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">Page not found</p>
      <h1 className="mt-3 text-3xl font-semibold text-foreground">We could not find that page.</h1>
      <p className="mt-3 max-w-xl text-muted">The page may have moved or is not available yet.</p>
      <Link href="/courses" className="mt-6 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-primary-hover">
        Browse courses
      </Link>
    </main>
  );
}

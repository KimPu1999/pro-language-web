import { AuthForm } from "@/components/auth-form";

export default async function Login({ searchParams }: { searchParams?: Promise<{ next?: string }> }) {
  const next = (await searchParams)?.next;
  const redirectTo = next && next.startsWith("/") && !next.startsWith("//") ? next : undefined;
  return <main className="grid min-h-[calc(100vh-73px)] place-items-center bg-gradient-to-br from-indigo-500/10 via-ink to-ink px-5 py-12"><AuthForm mode="login" redirectTo={redirectTo}/></main>;
}

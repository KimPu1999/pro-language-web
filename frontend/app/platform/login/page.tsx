import { AuthForm } from "@/components/auth-form";

export default function PlatformLoginPage() {
  return <main className="grid min-h-[calc(100vh-73px)] place-items-center bg-gradient-to-br from-indigo-500/10 via-ink to-ink px-5 py-12"><div><p className="mb-4 text-center text-sm text-indigo-300">Platform Control Center</p><AuthForm mode="login" redirectTo="/platform/analytics" /></div></main>;
}

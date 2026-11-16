"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Nav } from "@/components/nav";

export function SiteFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const dashboardPage = pathname.startsWith("/dashboard") || pathname.startsWith("/my-learning");
  return <>
    <Nav />
    <main className="min-h-screen pt-[73px]">{children}</main>
    {!dashboardPage && <footer className="border-t border-line bg-ink px-5 py-12 text-sm text-slate-400"><div className="mx-auto grid max-w-7xl gap-10 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]"><div><Link href="/" className="font-bold text-white">CodeMaster<span className="text-indigo-400"> Academy</span></Link><p className="mt-3 max-w-xs leading-6">Free programming education for curious builders, from first concepts to practical projects.</p></div><div><p className="font-semibold text-white">Learn</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/courses">Courses</Link><Link className="block hover:text-white" href="/learning-paths">Learning paths</Link><Link className="block hover:text-white" href="/challenges">Challenges</Link></div></div><div><p className="font-semibold text-white">Build</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/projects">Projects</Link><Link className="block hover:text-white" href="/community">Community</Link><Link className="block hover:text-white" href="/career">Career tools</Link></div></div><div><p className="font-semibold text-white">Platform</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/about">About</Link><Link className="block hover:text-white" href="/contact">Contact</Link><Link className="block hover:text-white" href="/privacy">Privacy</Link><Link className="block hover:text-white" href="/terms">Terms</Link></div></div></div><p className="mx-auto mt-10 max-w-7xl border-t border-line pt-6 text-xs">© 2026 CodeMaster Academy · Free learning for curious builders.</p></footer>}
  </>;
}

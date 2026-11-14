import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Nav } from "@/components/nav";
import { PwaRegister } from "@/components/pwa-register";

export const metadata: Metadata = {
  title: { default: "CodeMaster Academy | Master Coding. Build Your Future.", template: "%s | CodeMaster Academy" },
  description: "Free programming courses, coding challenges, learning paths, and practical projects for curious builders.",
  openGraph: { title: "CodeMaster Academy", description: "Master coding with free courses, challenges, and real-world projects.", type: "website" },
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en">
    <body><PwaRegister />
      <Nav />
      <main className="min-h-screen pt-[73px]">{children}</main>
      <footer className="border-t border-line bg-ink px-5 py-12 text-sm text-slate-400">
        <div className="mx-auto grid max-w-7xl gap-10 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div><Link href="/" className="font-bold text-white">CodeMaster<span className="text-indigo-400"> Academy</span></Link><p className="mt-3 max-w-xs leading-6">Free programming education for curious builders, from first concepts to practical projects.</p></div>
          <div><p className="font-semibold text-white">Learn</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/courses">Courses</Link><Link className="block hover:text-white" href="/learning-paths">Learning paths</Link><Link className="block hover:text-white" href="/challenges">Challenges</Link></div></div>
          <div><p className="font-semibold text-white">Build</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/projects">Projects</Link><Link className="block hover:text-white" href="/community">Community</Link><Link className="block hover:text-white" href="/career">Career tools</Link></div></div>
          <div><p className="font-semibold text-white">Platform</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href="/about">About</Link><Link className="block hover:text-white" href="/contact">Contact</Link><Link className="block hover:text-white" href="/privacy">Privacy</Link><Link className="block hover:text-white" href="/terms">Terms</Link></div></div>
        </div><p className="mx-auto mt-10 max-w-7xl border-t border-line pt-6 text-xs">© 2026 CodeMaster Academy · Free learning for curious builders.</p>
      </footer>
    </body>
  </html>;
}

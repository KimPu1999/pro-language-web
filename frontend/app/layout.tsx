import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "CodeMaster Academy",
  description: "Free programming lessons, challenges, projects, and community learning.",
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en">
    <body>
      <Nav />
      <main className="min-h-screen pt-[73px]">{children}</main>
      <footer className="border-t border-line px-5 py-10 text-center text-sm text-slate-500">
        <p>© 2026 CodeMaster Academy · Free learning for curious builders.</p>
      </footer>
    </body>
  </html>;
}

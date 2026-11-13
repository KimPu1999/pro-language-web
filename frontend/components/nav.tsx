"use client";
import Link from "next/link";
import { Menu, X, Code2, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LogoutButton } from "./auth-form";

const links = [["Home", "/"], ["Courses", "/courses"], ["Learning Paths", "/learning-paths"], ["Challenges", "/challenges"], ["Projects", "/projects"], ["Community", "/community"]] as const;

export function Nav() {
  const [open, setOpen] = useState(false);
  const [signedIn, setSignedIn] = useState(false);
  useEffect(() => { api.me().then(() => setSignedIn(true)).catch(() => setSignedIn(false)); }, []);
  return <header className="fixed inset-x-0 top-0 z-50 border-b border-line/70 bg-ink/90 backdrop-blur-xl">
    <div className="mx-auto flex h-[73px] max-w-7xl items-center justify-between px-5 lg:px-8">
      <Link href="/" className="flex items-center gap-2 font-bold"><span className="grid h-9 w-9 place-items-center rounded-xl bg-primary"><Code2 size={19} /></span><span>CodeMaster<span className="text-indigo-400"> Academy</span></span></Link>
      <nav className="hidden items-center gap-6 text-sm text-slate-300 md:flex">{links.map(([label, href]) => <Link className="transition hover:text-white" key={href} href={href}>{label}</Link>)}<Link aria-label="Search courses" className="rounded-lg p-2 transition hover:bg-surface hover:text-white" href="/courses"><Search size={17}/></Link>{signedIn ? <><Link className="text-indigo-300" href="/dashboard">Dashboard</Link><Link href="/profile">Profile</Link><LogoutButton /></> : <><Link href="/login">Log in</Link><Link className="rounded-lg bg-primary px-3 py-2 text-white" href="/register">Join free</Link></>}</nav>
      <button aria-label="Toggle menu" onClick={() => setOpen(!open)} className="rounded-lg p-2 md:hidden">{open ? <X /> : <Menu />}</button>
    </div>
    {open && <nav aria-label="Mobile navigation" className="border-t border-line bg-ink px-5 pb-4 md:hidden">{links.map(([label, href]) => <Link href={href} onClick={() => setOpen(false)} className="block border-b border-line/50 py-3 text-slate-300" key={href}>{label}</Link>)}<Link href="/courses" onClick={() => setOpen(false)} className="flex items-center gap-2 border-b border-line/50 py-3 text-slate-300"><Search size={16}/> Search</Link>{signedIn ? <><Link className="block py-3 text-indigo-300" onClick={() => setOpen(false)} href="/dashboard">Dashboard</Link><Link className="block py-3 text-slate-300" onClick={() => setOpen(false)} href="/profile">Profile</Link><div className="py-2"><LogoutButton /></div></> : <><Link className="block py-3 text-indigo-300" onClick={() => setOpen(false)} href="/login">Log in</Link><Link className="block rounded-lg bg-primary px-3 py-2 text-center text-white" onClick={() => setOpen(false)} href="/register">Join free</Link></>}</nav>}
  </header>;
}

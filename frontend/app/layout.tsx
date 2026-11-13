import "./globals.css"; import { Nav } from "@/components/nav";
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <><Nav/><main>{children}</main><footer className="border-t border-line px-5 py-10 text-center text-sm text-slate-500"><p>© 2026 CodeMaster Academy · Free learning for curious builders.</p></footer></>; }

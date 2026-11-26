"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Nav } from "@/components/nav";
import { routes } from "@/lib/routes";

export function SiteFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const managementPage = pathname.startsWith("/platform") || pathname.startsWith("/admin");
  const dashboardPage = pathname.startsWith("/dashboard") || pathname.startsWith("/my-learning");
  if (managementPage) return <>{children}</>;
  return <><Nav /><main className="min-h-screen">{children}</main>{!dashboardPage && <footer className="border-t border-line bg-ink px-5 py-12 text-sm text-slate-400"><div className="mx-auto grid max-w-7xl gap-10 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]"><div><Link href={routes.home} className="flex items-center gap-2 font-bold text-white"><Image src="/branding/tkp.png" alt="Languages-Platform logo" width={34} height={34} className="h-[34px] w-[34px] object-contain" />Languages-Platform</Link><p className="mt-3 max-w-xs leading-6">Free programming education for curious builders, from first concepts to practical projects.</p></div><div><p className="font-semibold text-white">Learn</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.courses}>Courses</Link><Link className="block hover:text-white" href="/learning-paths">Learning paths</Link><Link className="block hover:text-white" href={routes.challenges}>Challenges</Link></div></div><div><p className="font-semibold text-white">Build</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.projects}>Projects</Link><Link className="block hover:text-white" href="/community">Community</Link><Link className="block hover:text-white" href={routes.careers}>Careers</Link><Link className="block hover:text-white" href={routes.tools}>Developer tools</Link></div></div><div><p className="font-semibold text-white">Platform</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.about}>About</Link><Link className="block hover:text-white" href={routes.contact}>Contact</Link><Link className="block hover:text-white" href={routes.privacy}>Privacy</Link><Link className="block hover:text-white" href={routes.terms}>Terms</Link></div></div></div><p className="mx-auto mt-10 max-w-7xl border-t border-line pt-6 text-xs">© 2026 Languages-Platform · Free learning for curious builders.</p></footer>}</>;
}

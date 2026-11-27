"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Nav } from "@/components/nav";
import { routes } from "@/lib/routes";
import { useI18n } from "@/lib/i18n";

export function SiteFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const managementPage = pathname.startsWith("/platform") || pathname.startsWith("/admin");
  const dashboardPage = pathname.startsWith("/dashboard") || pathname.startsWith("/my-learning") || pathname.startsWith("/my-projects") || pathname.startsWith("/profile") || pathname.startsWith("/settings");
  const { t } = useI18n();
  if (managementPage || dashboardPage) return <>{children}</>;
  return <><Nav /><main className="min-h-screen pt-16">{children}</main>{!dashboardPage && <footer className="border-t border-line bg-ink py-12 text-sm text-slate-400"><div className="mx-auto grid max-w-7xl gap-10 px-5 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr] lg:px-8"><div><Link href={routes.home} className="flex items-center gap-2 font-bold text-white"><Image src="/branding/tkp.png" alt="Languages-Platform logo" width={34} height={34} className="h-[34px] w-[34px] object-contain" />Languages-Platform</Link><p className="mt-3 max-w-xs leading-6">{t("readCode")}</p></div><div><p className="font-semibold text-white">{t("courses")}</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.courses}>{t("courses")}</Link><Link className="block hover:text-white" href="/learning-paths">{t("learningPaths")}</Link><Link className="block hover:text-white" href={routes.challenges}>{t("challenges")}</Link></div></div><div><p className="font-semibold text-white">{t("projects")}</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.projects}>{t("projects")}</Link><Link className="block hover:text-white" href="/community">{t("community")}</Link><Link className="block hover:text-white" href={routes.careers}>{t("careers")}</Link><Link className="block hover:text-white" href={routes.tools}>{t("tools")}</Link></div></div><div><p className="font-semibold text-white">{t("platformControl")}</p><div className="mt-3 space-y-2"><Link className="block hover:text-white" href={routes.about}>{t("about")}</Link><Link className="block hover:text-white" href={routes.contact}>{t("contact")}</Link><Link className="block hover:text-white" href={routes.privacy}>{t("privacy")}</Link><Link className="block hover:text-white" href={routes.terms}>{t("terms")}</Link></div></div></div><p className="mx-auto mt-10 max-w-7xl border-t border-line px-5 pt-6 text-xs lg:px-8">© 2026 Languages-Platform · {t("readCode")}</p></footer>}</>;
}

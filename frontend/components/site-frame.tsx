"use client";

import { usePathname } from "next/navigation";
import { Nav } from "@/components/nav";
import { PublicFooter } from "@/components/public-footer";

export function SiteFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const managementPage = pathname.startsWith("/platform") || pathname.startsWith("/admin");
  const dashboardPage = pathname.startsWith("/dashboard") || pathname.startsWith("/my-learning") || pathname.startsWith("/my-projects") || pathname.startsWith("/profile") || pathname.startsWith("/settings");
  const learningPage = pathname.startsWith("/learn/");
  if (managementPage || dashboardPage) return <>{children}</>;
  return (
    <div className="flex min-h-[100dvh] flex-col">
      <Nav />
      <main className={`min-h-0 flex-1 pt-16${learningPage ? " lg:overflow-hidden" : ""}`}>{children}</main>
      {!learningPage && <PublicFooter />}
    </div>
  );
}

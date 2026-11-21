"use client";

import { usePathname } from "next/navigation";
import { PlatformFooter } from "@/components/platform-footer";
import { PlatformNav } from "@/components/platform-nav";

export function PlatformShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLessonPage = pathname.startsWith("/courses/") && pathname.includes("/learn/");

  return <div className={isLessonPage ? "flex h-dvh flex-col overflow-hidden" : "flex min-h-dvh flex-col"}>
    <PlatformNav />
    <main className={isLessonPage ? "flex min-h-0 flex-1 flex-col" : "flex-1"}>{children}</main>
    {!isLessonPage && <PlatformFooter />}
  </div>;
}

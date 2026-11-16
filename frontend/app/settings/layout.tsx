import { StudentDashboardShell } from "@/components/student-dashboard-shell";

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return <StudentDashboardShell>{children}</StudentDashboardShell>;
}

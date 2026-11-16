import { StudentDashboardShell } from "@/components/student-dashboard-shell";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <StudentDashboardShell>{children}</StudentDashboardShell>;
}

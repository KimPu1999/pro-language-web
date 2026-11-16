import { StudentDashboardShell } from "@/components/student-dashboard-shell";

export default function MyProjectsLayout({ children }: { children: React.ReactNode }) {
  return <StudentDashboardShell>{children}</StudentDashboardShell>;
}

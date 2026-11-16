import { StudentDashboardShell } from "@/components/student-dashboard-shell";

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return <StudentDashboardShell>{children}</StudentDashboardShell>;
}

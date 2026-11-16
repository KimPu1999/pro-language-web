import { StudentDashboardShell } from "@/components/student-dashboard-shell";

export default function MyLearningLayout({ children }: { children: React.ReactNode }) {
  return <StudentDashboardShell>{children}</StudentDashboardShell>;
}

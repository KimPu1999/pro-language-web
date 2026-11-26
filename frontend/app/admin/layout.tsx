import { ManagementShell } from "@/components/management-shell";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <ManagementShell>{children}</ManagementShell>;
}

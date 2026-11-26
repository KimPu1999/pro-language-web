import { ManagementShell } from "@/components/management-shell";

/**
 * Compatibility wrapper for existing /platform routes.
 * Admin and platform management now share one protected workspace shell.
 */
export function PlatformShell({ children }: { children: React.ReactNode }) {
  return <ManagementShell>{children}</ManagementShell>;
}

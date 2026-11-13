export type AnalyticsRange = { start: string; end: string };
export type AnalyticsOverview = { range: AnalyticsRange; kpis: Record<string, number>; trends: { date: string; enrollments: number; lesson_completions: number }[]; completion_rate: number; definitions: Record<string, string> };
export type AnalyticsPage = { range: AnalyticsRange; items?: Record<string, unknown>[]; [key: string]: unknown };
export type ReportHistory = { exports: { id: string; report_type: string; row_count: number; status: string; created_at: string }[]; page: number; page_size: number; total: number; pages: number };

const csrf = () => typeof document === "undefined" ? "" : document.cookie.split("; ").find((v) => v.startsWith("cm_csrf="))?.split("=")[1] ?? "";
const inflightGets = new Map<string, Promise<unknown>>();
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const key = typeof window !== "undefined" && method === "GET" ? path : "";
  const pending = key ? inflightGets.get(key) : undefined;
  if (pending) return pending as Promise<T>;
  const run = (async () => {
    const response = await fetch(path, { ...init, credentials: "include", headers: { Accept: "application/json", "Content-Type": "application/json", ...init?.headers } });
    if (!response.ok) {
      let message = `Analytics request failed (${response.status})`;
      try { const body = await response.json() as { detail?: string }; message = body.detail ?? message; } catch { /* preserve status */ }
      throw new Error(message);
    }
    return response.json() as Promise<T>;
  })().finally(() => { if (key) inflightGets.delete(key); });
  if (key) inflightGets.set(key, run);
  return run;
}
const query = (start: string, end: string) => `?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`;
export const analyticsApi = {
  overview: (start: string, end: string) => request<AnalyticsOverview>(`/api/v1/platform/analytics/overview${query(start, end)}`),
  students: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/students${query(start, end)}`),
  courses: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/courses${query(start, end)}`),
  instructors: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/instructors${query(start, end)}`),
  challenges: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/challenges${query(start, end)}`),
  learning: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/learning${query(start, end)}`),
  certificates: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/certificates${query(start, end)}`),
  community: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/community${query(start, end)}`),
  reports: () => request<ReportHistory>("/api/v1/platform/reports"),
  export: async (start: string, end: string) => {
    const response = await fetch(`/api/v1/platform/reports/export?report_type=overview&start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`, { method: "POST", credentials: "include", headers: { "X-CSRF-Token": csrf() } });
    if (!response.ok) throw new Error(`Export failed (${response.status})`);
    return response.blob();
  },
};

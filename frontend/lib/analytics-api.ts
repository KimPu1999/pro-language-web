export type AnalyticsRange = { start: string; end: string };
export type AnalyticsOverview = { range: AnalyticsRange; kpis: Record<string, number>; trends: { date: string; enrollments: number; lesson_completions: number }[]; completion_rate: number; definitions: Record<string, string> };
export type AnalyticsPage = { range: AnalyticsRange; items?: Record<string, unknown>[]; [key: string]: unknown };
export type ReportHistory = { exports: { id: string; report_type: string; row_count: number; status: string; created_at: string }[]; page: number; page_size: number; total: number; pages: number };
export type InstructorKpis = { total_instructors: number; active_instructors: number; published_courses: number; new_enrollments: number; active_learners: number; course_completions: number; lessons_published: number; project_reviews_completed: number; pending_project_reviews: number };
export type InstructorRow = { id: string; display_name: string; email?: string|null; associated_courses: number; published_courses: number; published_lessons: number; published_lesson_revisions: number; enrolled_learners: number; active_learners: number; course_completions: number; completed_reviews: number; review_turnaround_hours: number|null; last_recorded_activity: string|null; activity_state: "available"|"no_activity_recorded" };
export type InstructorOverview = { range: { start: string; end: string; start_date: string; end_date: string }; kpis: InstructorKpis; comparison: Record<string, { current: number; previous: number; difference: number; percentage: number|null }> | null; sources: Record<string, string>; definitions: Record<string, string>; data_state: string; updated_at: string };
export type InstructorList = { range: InstructorOverview["range"]; items: InstructorRow[]; page: number; page_size: number; total: number; pages: number; sources: Record<string, string>; definitions: Record<string, string>; data_state: string };
export type InstructorTrend = { date: string; activity: number; new_enrollments: number; active_learners: number; course_completions: number; project_reviews: number; lessons_published: number };
export type InstructorCourse = { id: string; title: string; slug: string; published: boolean; instructor_count: number; published_lessons: number; enrolled_learners: number; new_enrollments: number; active_learners: number; course_completions: number };
export type InstructorCourses = { items: InstructorCourse[]; page: number; page_size: number; total: number; pages: number; range: InstructorOverview["range"]; data_state: string };
export type InstructorReviews = { submitted_projects: number; reviews_completed: number; pending_reviews: number; resubmissions: number; feedback_completed: number; median_turnaround_hours: number|null; range: InstructorOverview["range"]; data_state: string };

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
      const requestId = response.headers.get("X-Request-ID");
      try { const body = await response.json() as { detail?: string; request_id?: string }; message = body.detail ?? message; } catch { /* preserve status */ }
      if (requestId && response.status >= 500) message = `${message} (request ${requestId})`;
      throw new Error(message);
    }
    return response.json() as Promise<T>;
  })().finally(() => { if (key) inflightGets.delete(key); });
  if (key) inflightGets.set(key, run);
  return run;
}
const query = (start: string, end: string) => `?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`;
const instructorQuery = (start: string, end: string, params: Record<string, string|number|undefined> = {}) => {
  const values = new URLSearchParams({ start_date: start, end_date: end });
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== "") values.set(key, String(value)); });
  return `?${values.toString()}`;
};
export const analyticsApi = {
  overview: (start: string, end: string) => request<AnalyticsOverview>(`/api/v1/platform/analytics/overview${query(start, end)}`),
  students: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/students${query(start, end)}`),
  courses: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/courses${query(start, end)}`),
  instructors: (start: string, end: string) => request<AnalyticsPage>(`/api/v1/platform/analytics/instructors${query(start, end)}`),
  instructorOverview: (start: string, end: string, params: Record<string, string|number|undefined> = {}) => request<InstructorOverview>(`/api/v1/platform/analytics/instructors/overview${instructorQuery(start, end, params)}`),
  instructorList: (start: string, end: string, params: Record<string, string|number|undefined> = {}) => request<InstructorList>(`/api/v1/platform/analytics/instructors/list${instructorQuery(start, end, params)}`),
  instructorTrends: (start: string, end: string, params: Record<string, string|number|undefined> = {}) => request<{ items: InstructorTrend[]; data_state: string }>(`/api/v1/platform/analytics/instructors/trends${instructorQuery(start, end, params)}`),
  instructorCourses: (start: string, end: string, params: Record<string, string|number|undefined> = {}) => request<InstructorCourses>(`/api/v1/platform/analytics/instructors/courses${instructorQuery(start, end, params)}`),
  instructorReviews: (start: string, end: string, params: Record<string, string|number|undefined> = {}) => request<InstructorReviews>(`/api/v1/platform/analytics/instructors/reviews${instructorQuery(start, end, params)}`),
  instructorDetail: (id: string, start: string, end: string) => request<{ instructor: InstructorRow|null; courses: { id: string; title: string; slug: string; published: boolean }[] }>(`/api/v1/platform/analytics/instructors/${id}${instructorQuery(start, end)}`),
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
  exportInstructors: async (start: string, end: string, params: Record<string, string|number|undefined> = {}) => {
    const response = await fetch(`/api/v1/platform/analytics/instructors/export${instructorQuery(start, end, params)}`, { method: "GET", credentials: "include", headers: { Accept: "text/csv" } });
    if (!response.ok) throw new Error(`Export failed (${response.status})`);
    return response.blob();
  },
};

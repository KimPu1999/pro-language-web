import type { Course, CourseDetail, Language, Module, Paginated } from "./types";

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try { const response = await fetch(`${base}${path}`, { ...init, signal: controller.signal, headers: { Accept: "application/json", ...init?.headers } }); if (!response.ok) throw new Error(`API request failed (${response.status})`); return response.json() as Promise<T>; } finally { clearTimeout(timer); }
}
export const api = { languages: () => request<Language[]>("/api/v1/languages"), courses: (query = "") => request<Paginated<Course>>(`/api/v1/courses${query}`), course: (slug: string) => request<CourseDetail>(`/api/v1/courses/${slug}`), modules: (slug: string) => request<Module[]>(`/api/v1/courses/${slug}/modules`), paths: () => request<unknown[]>("/api/v1/paths") };

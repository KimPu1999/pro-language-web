import type { AdminCourse, AdminDashboard, AdminPage, Challenge, ChallengePage, Course, CourseDetail, Dashboard, Enrollment, Language, Module, Paginated, RunnerJob, RunnerLanguage, SkillDashboard, User, LearningIntelligence, LearningPlan, RevisionItem } from "./types";

// Browser requests use the same-origin Next rewrite. Server rendering may use the private internal URL.
const base = process.env.NEXT_PUBLIC_API_BASE_URL || (typeof window === "undefined" ? process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000" : "");
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`${base}${path}`, { ...init, credentials: "include", signal: controller.signal, headers: { Accept: "application/json", "Content-Type": "application/json", ...init?.headers } });
    if (!response.ok) {
      let message = `API request failed (${response.status})`;
      try {
        const payload = await response.json() as { detail?: string; message?: string };
        message = payload.detail ?? payload.message ?? message;
      } catch {
        // Keep the status-based message when the server does not return JSON.
      }
      throw new Error(message);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("The API request timed out. Make sure the backend is running on port 8000.");
    }
    if (error instanceof TypeError) {
      throw new Error(`Cannot connect to the CodeMaster API at ${base}. Start FastAPI with: uvicorn app.main:app --reload --port 8000`);
    }
    throw error;
  } finally { clearTimeout(timer); }
}
const json = (body: unknown) => ({ method: "POST", body: JSON.stringify(body) });
export const api = { languages: () => request<Language[]>("/api/v1/languages"), courses: (query = "") => request<Paginated<Course>>(`/api/v1/courses${query}`), course: (slug: string) => request<CourseDetail>(`/api/v1/courses/${slug}`), modules: (slug: string) => request<Module[]>(`/api/v1/courses/${slug}/modules`), paths: () => request<unknown[]>("/api/v1/paths"), challenges:(query="")=>request<ChallengePage>(`/api/v1/challenges${query}`), challenge:(slug:string)=>request<Challenge>(`/api/v1/challenges/${slug}`), challengeRun:(id:string,body:unknown,csrf:string)=>request<{id:string;status:string;score:number|null}>(`/api/v1/challenges/${id}/run`,{...json(body),headers:{"X-CSRF-Token":csrf}}), challengeSubmit:(id:string,body:unknown,csrf:string)=>request<{id:string;status:string;score:number|null}>(`/api/v1/challenges/${id}/submit`,{...json(body),headers:{"X-CSRF-Token":csrf}}), challengeHistory:(id?:string)=>request<unknown[]>(`/api/v1/challenges/submissions/history${id?`?challenge_id=${id}`:""}`), skills:()=>request<SkillDashboard>("/api/v1/challenges/skills/me"), dailyChallenge:()=>request<unknown>("/api/v1/challenges/daily/today"), achievements:()=>request<unknown[]>("/api/v1/challenges/achievements/me"), me: () => request<User>("/api/v1/auth/me"), login: (body: unknown) => request<User>("/api/v1/auth/login", json(body)), register: (body: unknown) => request<User>("/api/v1/auth/register", json(body)), logout: (csrf: string) => request<{status:string}>("/api/v1/auth/logout", { method:"POST", headers:{"X-CSRF-Token":csrf} }), forgotPassword: (email: string) => request<{message:string}>("/api/v1/auth/forgot-password", json({email})), resetPassword: (body: unknown) => request<{status:string}>("/api/v1/auth/reset-password", json(body)), changePassword: (body: unknown, csrf: string) => request<{status:string}>("/api/v1/auth/change-password", { ...json(body), headers:{"X-CSRF-Token":csrf} }), verifyEmail: (token: string) => request<{status:string}>(`/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`), enroll: (slug: string, csrf: string) => request<Enrollment>(`/api/v1/me/enrollments/${slug}`, { ...json({}), headers:{"X-CSRF-Token":csrf} }), enrollments: () => request<Enrollment[]>("/api/v1/me/enrollments"), dashboard: () => request<Dashboard>("/api/v1/me/dashboard"), profile: () => request<User>("/api/v1/me/profile"), updateProfile: (body: unknown, csrf: string) => request<User>("/api/v1/me/profile", { ...json(body), method:"PATCH", headers:{"X-CSRF-Token":csrf} }), progress: (lessonId: string, completed: boolean, csrf: string) => request<{completed:boolean}>(`/api/v1/me/lessons/${lessonId}/progress`, { ...json({completed}), headers:{"X-CSRF-Token":csrf} }), runnerLanguages:()=>request<RunnerLanguage[]>("/api/v1/runner/languages"), execute:(body:{language:string;source_code:string;exercise_id?:string},csrf:string)=>request<RunnerJob>("/api/v1/runner/execute",{...json(body),headers:{"X-CSRF-Token":csrf}}), runnerJob:(id:string)=>request<RunnerJob>(`/api/v1/runner/jobs/${id}`), cancelRunnerJob:(id:string,csrf:string)=>request<RunnerJob>(`/api/v1/runner/jobs/${id}/cancel`,{method:"POST",headers:{"X-CSRF-Token":csrf}}), runnerExercise:(slug:string)=>request<unknown>(`/api/v1/runner/exercises/${slug}`), runnerSubmissions:()=>request<unknown[]>("/api/v1/runner/submissions"), runnerPreferences:()=>request<unknown>("/api/v1/runner/preferences"), updateRunnerPreferences:(body:unknown,csrf:string)=>request<unknown>("/api/v1/runner/preferences",{method:"PUT",body:JSON.stringify(body),headers:{"X-CSRF-Token":csrf}}), adminDashboard:()=>request<AdminDashboard>("/api/v1/admin/dashboard"), adminCourses:(query="")=>request<AdminPage>(`/api/v1/admin/courses${query}`), adminLanguages:()=>request<{items:Language[];total:number}>("/api/v1/admin/languages"), adminCategories:()=>request<{items:{id:string;name:string;slug:string;description:string;status:string}[];total:number}>("/api/v1/admin/categories"), adminCreateCourse:(body:unknown,csrf:string)=>request<AdminCourse>("/api/v1/admin/courses",{...json(body),headers:{"X-CSRF-Token":csrf}}), adminBuilder:(id:string)=>request<AdminCourse>(`/api/v1/admin/courses/${id}/builder`), adminCurriculum:(id:string)=>request<{id:string;title:string;position:number;lessons:{id:string;title:string;position:number;status:string}[]}[]>(`/api/v1/admin/courses/${id}/curriculum`), adminCreateModule:(id:string,body:unknown,csrf:string)=>request<unknown>(`/api/v1/admin/courses/${id}/modules`,{...json(body),headers:{"X-CSRF-Token":csrf}}), adminCreateLesson:(id:string,body:unknown,csrf:string)=>request<unknown>(`/api/v1/admin/modules/${id}/lessons`,{...json(body),headers:{"X-CSRF-Token":csrf}}), adminPublish:(id:string,body:unknown,csrf:string)=>request<AdminCourse>(`/api/v1/admin/courses/${id}/publish`,{...json(body),headers:{"X-CSRF-Token":csrf}}) };

export const learningApi = {
  intelligence: () => request<LearningIntelligence>("/api/v1/learning/intelligence"),
  skills: () => request<{items: import("./types").LearningSkill[]}>("/api/v1/learning/skills"),
  recommendations: () => request<{items: LearningIntelligence["recommendations"]; status:string}>("/api/v1/learning/recommendations"),
  plans: () => request<{items:LearningPlan[]}>("/api/v1/learning/study-plans"),
  createPlan: (body:unknown, csrf:string) => request<{id:string;title:string;status:string;items:number}>("/api/v1/learning/study-plans", { ...json(body), headers:{"X-CSRF-Token":csrf} }),
  revision: () => request<{items:RevisionItem[]}>("/api/v1/learning/revision"),
  coach: (message:string, csrf:string) => request<{status:string;message:string}>("/api/v1/learning/coach", { ...json({message}), headers:{"X-CSRF-Token":csrf} }),
};

export type AutomationDashboard = { metrics: { workflows:number; active_workflows:number; queued_runs:number; failed_runs:number; pending_approvals:number }; execution:{status:string;detail:string}; ai:{status:string}; data_source:string };
export type AutomationWorkflow = { id:string; name:string; slug:string; status:string; enabled:boolean };
export const automationApi = {
  dashboard: (slug:string) => request<AutomationDashboard>(`/api/v1/organizations/${slug}/automation`),
  workflows: (slug:string) => request<{items:AutomationWorkflow[];page:number;page_size:number;total:number}>(`/api/v1/organizations/${slug}/automation/workflows`),
  createWorkflow: (slug:string, body:unknown, csrf:string) => request<{id:string;status:string}>(`/api/v1/organizations/${slug}/automation/workflows`, {...json(body),headers:{"X-CSRF-Token":csrf}}),
  validate: (slug:string,id:string,body:unknown) => request<{valid:boolean;errors:string[]}>(`/api/v1/organizations/${slug}/automation/workflows/${id}/validate`,{...json(body)}),
  addVersion: (slug:string,id:string,body:unknown,csrf:string) => request<unknown>(`/api/v1/organizations/${slug}/automation/workflows/${id}/versions`,{...json(body),headers:{"X-CSRF-Token":csrf}}),
  run: (slug:string,id:string,body:unknown,csrf:string) => request<unknown>(`/api/v1/organizations/${slug}/automation/workflows/${id}/runs`,{...json(body),headers:{"X-CSRF-Token":csrf}}),
  runs: (slug:string) => request<{items:unknown[]}>(`/api/v1/organizations/${slug}/automation/runs`),
  approvals: (slug:string) => request<unknown[]>(`/api/v1/organizations/${slug}/automation/approvals`),
  agents: (slug:string) => request<unknown[]>(`/api/v1/organizations/${slug}/automation/agents`),
  usage: (slug:string) => request<{provider_status:string;items:unknown[]}>(`/api/v1/organizations/${slug}/automation/usage`),
  templates: (slug:string) => request<unknown[]>(`/api/v1/organizations/${slug}/automation/templates`),
  platform: () => request<unknown>("/api/v1/platform/automation"),
};

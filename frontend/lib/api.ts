import type { AdminCourse, AdminDashboard, AdminPage, Challenge, ChallengeCategory, ChallengePage, ChallengeProgress, Course, CourseDetail, Dashboard, Enrollment, Language, Lesson, LessonQuiz, Module, Paginated, RunnerJob, RunnerLanguage, SkillDashboard, User, LearningIntelligence, LearningPlan, RevisionItem } from "./types";

// Browser requests use the same-origin Next rewrite. Server rendering may use the private internal URL.
const base = process.env.NEXT_PUBLIC_API_BASE_URL || (typeof window === "undefined" ? process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000" : "");
const inflightGets = new Map<string, Promise<unknown>>();
export type ApiErrorKind = "timeout" | "unavailable" | "http" | "unknown";
export class ApiError extends Error { constructor(message: string, readonly kind: ApiErrorKind, readonly status?: number, readonly requestId?: string) { super(message); this.name = "ApiError"; } }
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const key = typeof window !== "undefined" && method === "GET" ? path : "";
  const pending = key ? inflightGets.get(key) : undefined;
  if (pending) return pending as Promise<T>;
  const controller = new AbortController();
  const abortFromCaller = () => controller.abort();
  if (init?.signal) {
    if (init.signal.aborted) controller.abort();
    else init.signal.addEventListener("abort", abortFromCaller, { once: true });
  }
  const timer = setTimeout(() => controller.abort(), 8000);
  const run = (async () => {
    const response = await fetch(`${base}${path}`, { ...init, credentials: "include", signal: controller.signal, headers: { Accept: "application/json", "Content-Type": "application/json", ...init?.headers } });
    if (!response.ok) {
      let message = `API request failed (${response.status})`;
      try {
        const payload = await response.json() as { detail?: string; message?: string };
        message = payload.detail ?? payload.message ?? message;
      } catch {
        // Keep the status-based message when the server does not return JSON.
      }
      throw new ApiError(message, "http", response.status, response.headers.get("X-Request-ID") ?? undefined);
    }
    return response.json() as Promise<T>;
  })().catch((error) => {
    if (error instanceof Error && error.name === "AbortError") {
      throw new ApiError("The API did not respond within 8 seconds. Check that FastAPI is healthy and that port 8000 is reachable.", "timeout");
    }
    if (error instanceof TypeError) {
      throw new ApiError("The CodeMaster API is unavailable. Start FastAPI on port 8000 or check API_INTERNAL_URL.", "unavailable");
    }
    throw error;
  }).finally(() => { clearTimeout(timer); init?.signal?.removeEventListener("abort", abortFromCaller); if (key) inflightGets.delete(key); });
  if (key) inflightGets.set(key, run);
  return run;
}
const json = (body: unknown) => ({ method: "POST", body: JSON.stringify(body) });
export const api = { organizations:()=>request<{slug:string;name:string;role:string}[]>("/api/v1/organizations"), languages: () => request<Language[]>("/api/v1/languages"), categories: () => request<{id:string;name:string;slug:string;description?:string}[]>("/api/v1/course-categories"), courses: (query = "") => request<Paginated<Course>>(`/api/v1/courses${query}`), course: (slug: string) => request<CourseDetail>(`/api/v1/courses/${slug}`), courseLessons: (slug: string) => request<Lesson[]>(`/api/v1/courses/${slug}/lessons`), lessonExamples: (id: string) => request<Lesson["code_examples"]>(`/api/v1/lessons/${id}/examples`), modules: (slug: string) => request<Module[]>(`/api/v1/courses/${slug}/modules`), paths: () => request<unknown[]>("/api/v1/paths"), challenges:(query="")=>request<ChallengePage>(`/api/v1/challenges${query}`), challengeCategories:()=>request<ChallengeCategory[]>("/api/v1/challenge-categories"), challengeTopics:()=>request<ChallengeCategory[]>("/api/v1/challenges/topics"), challengeProgress:()=>request<ChallengeProgress>("/api/v1/me/challenge-progress"), challenge:(slug:string)=>request<Challenge>(`/api/v1/challenges/${slug}`), challengeRun:(id:string,body:unknown,csrf:string)=>request<{id:string;status:string;score:number|null}>(`/api/v1/challenges/${id}/run`,{...json(body),headers:{"X-CSRF-Token":csrf}}), challengeSubmit:(id:string,body:unknown,csrf:string)=>request<{id:string;status:string;score:number|null}>(`/api/v1/challenges/${id}/submit`,{...json(body),headers:{"X-CSRF-Token":csrf}}), challengeHistory:(id?:string)=>request<unknown[]>(`/api/v1/challenges/submissions/history${id?`?challenge_id=${id}`:""}`), skills:()=>request<SkillDashboard>("/api/v1/challenges/skills/me"), dailyChallenge:()=>request<unknown>("/api/v1/challenges/daily/today"), achievements:()=>request<unknown[]>("/api/v1/challenges/achievements/me"), me: () => request<User>("/api/v1/auth/me"), login: (body: unknown) => request<User>("/api/v1/auth/login", json(body)), register: (body: unknown) => request<User>("/api/v1/auth/register", json(body)), logout: (csrf: string) => request<{status:string}>("/api/v1/auth/logout", { method:"POST", headers:{"X-CSRF-Token":csrf} }), forgotPassword: (email: string) => request<{message:string}>("/api/v1/auth/forgot-password", json({email})), resetPassword: (body: unknown) => request<{status:string}>("/api/v1/auth/reset-password", json(body)), changePassword: (body: unknown, csrf: string) => request<{status:string}>("/api/v1/auth/change-password", { ...json(body), headers:{"X-CSRF-Token":csrf} }), verifyEmail: (token: string) => request<{status:string}>(`/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`), enroll: (slug: string, csrf: string) => request<Enrollment>(`/api/v1/me/enrollments/${slug}`, { ...json({}), headers:{"X-CSRF-Token":csrf} }), enrollments: () => request<Enrollment[]>("/api/v1/me/enrollments"), dashboard: () => request<Dashboard>("/api/v1/me/dashboard"), profile: () => request<User>("/api/v1/me/profile"), updateProfile: (body: unknown, csrf: string) => request<User>("/api/v1/me/profile", { ...json(body), method:"PATCH", headers:{"X-CSRF-Token":csrf} }), progress: (lessonId: string, completed: boolean, csrf: string) => request<{completed:boolean}>(`/api/v1/me/lessons/${lessonId}/progress`, { ...json({completed}), headers:{"X-CSRF-Token":csrf} }), bookmark: (lessonId: string, csrf: string) => request<{lesson_id:string;bookmarked:boolean}>(`/api/v1/me/lessons/${lessonId}/bookmark`, { method:"POST", headers:{"X-CSRF-Token":csrf} }), runnerLanguages:()=>request<RunnerLanguage[]>("/api/v1/runner/languages"), execute:(body:{language:string;source_code:string;exercise_id?:string},csrf:string)=>request<RunnerJob>("/api/v1/runner/execute",{...json(body),headers:{"X-CSRF-Token":csrf}}), runnerJob:(id:string)=>request<RunnerJob>(`/api/v1/runner/jobs/${id}`), cancelRunnerJob:(id:string,csrf:string)=>request<RunnerJob>(`/api/v1/runner/jobs/${id}/cancel`,{method:"POST",headers:{"X-CSRF-Token":csrf}}), runnerExercise:(slug:string)=>request<unknown>(`/api/v1/runner/exercises/${slug}`), runnerSubmissions:()=>request<unknown[]>("/api/v1/runner/submissions"), runnerPreferences:()=>request<unknown>("/api/v1/runner/preferences"), updateRunnerPreferences:(body:unknown,csrf:string)=>request<unknown>("/api/v1/runner/preferences",{method:"PUT",body:JSON.stringify(body),headers:{"X-CSRF-Token":csrf}}), adminDashboard:()=>request<AdminDashboard>("/api/v1/admin/dashboard"), adminCourses:(query="")=>request<AdminPage>(`/api/v1/admin/courses${query}`), adminLanguages:()=>request<{items:Language[];total:number}>("/api/v1/admin/languages"), adminCategories:()=>request<{items:{id:string;name:string;slug:string;description:string;status:string}[];total:number}>("/api/v1/admin/categories"), adminCreateCourse:(body:unknown,csrf:string)=>request<AdminCourse>("/api/v1/admin/courses",{...json(body),headers:{"X-CSRF-Token":csrf}}), adminBuilder:(id:string)=>request<AdminCourse>(`/api/v1/admin/courses/${id}/builder`), adminCurriculum:(id:string)=>request<{id:string;title:string;position:number;lessons:{id:string;title:string;position:number;status:string}[]}[]>(`/api/v1/admin/courses/${id}/curriculum`), adminCreateModule:(id:string,body:unknown,csrf:string)=>request<unknown>(`/api/v1/admin/courses/${id}/modules`,{...json(body),headers:{"X-CSRF-Token":csrf}}), adminCreateLesson:(id:string,body:unknown,csrf:string)=>request<unknown>(`/api/v1/admin/modules/${id}/lessons`,{...json(body),headers:{"X-CSRF-Token":csrf}}), adminPublish:(id:string,body:unknown,csrf:string)=>request<AdminCourse>(`/api/v1/admin/courses/${id}/publish`,{...json(body),headers:{"X-CSRF-Token":csrf}}) };

export const lessonQuizApi = {
  get: (lessonId: string) => request<LessonQuiz>(`/api/v1/me/lessons/${lessonId}/quiz`),
  submit: (lessonId: string, answers: Record<string, string>, csrf: string) => request<{ attempt_id: string; score: number; total: number; passed: boolean; feedback: { question_id: string; correct: boolean; explanation: string }[] }>(`/api/v1/me/lessons/${lessonId}/quiz`, { ...json({ answers }), headers: { "X-CSRF-Token": csrf } }),
};
export const learningApi = {
  intelligence: () => request<LearningIntelligence>("/api/v1/learning/intelligence"),
  skills: () => request<{items: import("./types").LearningSkill[]}>("/api/v1/learning/skills"),
  recommendations: () => request<{items: LearningIntelligence["recommendations"]; status:string}>("/api/v1/learning/recommendations"),
  plans: () => request<{items:LearningPlan[]}>("/api/v1/learning/study-plans"),
  createPlan: (body:unknown, csrf:string) => request<{id:string;title:string;status:string;items:number}>("/api/v1/learning/study-plans", { ...json(body), headers:{"X-CSRF-Token":csrf} }),
  revision: () => request<{items:RevisionItem[]}>("/api/v1/learning/revision"),
  coach: (message:string, csrf:string) => request<{status:string;message:string}>("/api/v1/learning/coach", { ...json({message}), headers:{"X-CSRF-Token":csrf} }),
};

export const coursesApi = (query = "", signal?: AbortSignal) => request<Paginated<Course>>(`/api/v1/courses${query}`, signal ? { signal } : undefined);
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
export type ContentDashboard = { metrics:{draft_projects:number;generation_jobs:number;pending_reviews:number;published_revisions:number}; ai:{status:string}; data_source:string };
export const contentStudioApi = {
  dashboard:(slug:string)=>request<ContentDashboard>(`/api/v1/organizations/${slug}/content-studio`),
  projects:(slug:string)=>request<{items:{id:string;title:string;content_type:string;status:string}[]}>(`/api/v1/organizations/${slug}/content-studio/projects`),
  createProject:(slug:string,body:unknown,csrf:string)=>request<{id:string;status:string}>(`/api/v1/organizations/${slug}/content-studio/projects`,{...json(body),headers:{"X-CSRF-Token":csrf}}),
  generate:(slug:string,id:string,body:unknown,csrf:string)=>request<{id:string;status:string;message:string}>(`/api/v1/organizations/${slug}/content-studio/projects/${id}/generate`,{...json(body),headers:{"X-CSRF-Token":csrf}}),
  jobs:(slug:string)=>request<unknown[]>(`/api/v1/organizations/${slug}/content-studio/jobs`),
  reviews:(slug:string)=>request<unknown[]>(`/api/v1/organizations/${slug}/content-studio/reviews`),
  quality:(slug:string)=>request<unknown[]>(`/api/v1/organizations/${slug}/content-studio/quality`),
  usage:(slug:string)=>request<{provider_status:string;items:unknown[]}>(`/api/v1/organizations/${slug}/content-studio/usage`),
  platform:()=>request<unknown>("/api/v1/platform/content-studio"),
};
export const labsApi = {
  catalog:(query="")=>request<{items:unknown[];page:number;page_size:number;total:number}>(`/api/v1/labs${query}`),
  detail:(id:string)=>request<any>(`/api/v1/labs/${id}`),
  dashboard:()=>request<{items:unknown[]}>('/api/v1/me/labs'),
  workspace:(id:string,csrf:string)=>request<{id:string;status:string}>(`/api/v1/labs/${id}/workspace`,{...json({}),headers:{"X-CSRF-Token":csrf}}),
  getWorkspace:(id:string)=>request<any>(`/api/v1/lab-workspaces/${id}`),
  saveFile:(id:string,body:unknown,csrf:string)=>request<any>(`/api/v1/lab-workspaces/${id}/files`,{method:"PUT",body:JSON.stringify(body),headers:{"X-CSRF-Token":csrf}}),
  run:(id:string,body:unknown,csrf:string)=>request<any>(`/api/v1/lab-workspaces/${id}/run`,{...json(body),headers:{"X-CSRF-Token":csrf}}),
  instructor:()=>request<unknown[]>('/api/v1/instructor/labs'),
  platform:()=>request<any>('/api/v1/platform/labs'),
};
export const cloudLabsApi = {
  catalog: (query = "") => request<any>(`/api/v1/cloud-labs/catalog${query}`),
  dashboard: () => request<any>("/api/v1/cloud-labs/dashboard"),
  detail: (id: string) => request<any>(`/api/v1/cloud-labs/${id}`),
  createWorkspace: (id: string, csrf: string) => request<any>(`/api/v1/cloud-labs/${id}/workspaces`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  workspace: (id: string) => request<any>(`/api/v1/cloud-labs/workspaces/${id}`),
  lifecycle: (id: string, action: string, csrf: string) => request<any>(`/api/v1/cloud-labs/workspaces/${id}/lifecycle`, { method: "PATCH", body: JSON.stringify({ action }), headers: { "X-CSRF-Token": csrf } }),
  saveFile: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/cloud-labs/workspaces/${id}/files`, { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  snapshot: (id: string, csrf: string) => request<any>(`/api/v1/cloud-labs/workspaces/${id}/snapshots`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  modes: () => request<any>("/api/v1/cloud-labs/modes"),
  operations: () => request<any>("/api/v1/cloud-labs/platform/operations"),
};
export const cybersecurityApi = {
  dashboard: () => request<any>("/api/v1/cybersecurity/dashboard"),
  paths: () => request<any>("/api/v1/cybersecurity/paths"),
  path: (slug: string) => request<any>(`/api/v1/cybersecurity/paths/${slug}`),
  labs: (query = "") => request<any>(`/api/v1/cybersecurity/labs${query}`),
  lab: (id: string) => request<any>(`/api/v1/cybersecurity/labs/${id}`),
  attempt: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/cybersecurity/labs/${id}/attempts`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  evaluate: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/cybersecurity/attempts/${id}/evaluate`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  threatModels: () => request<any>("/api/v1/cybersecurity/threat-models"),
  createThreatModel: (body: unknown, csrf: string) => request<any>("/api/v1/cybersecurity/threat-models", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  aiStatus: () => request<any>("/api/v1/cybersecurity/ai-tutor/status"),
  operations: () => request<any>("/api/v1/cybersecurity/platform/operations"),
};
export const mobileApi = {
  dashboard: () => request<any>("/api/v1/mobile/dashboard"),
  library: () => request<any>("/api/v1/mobile/library"),
  manifest: (course_id: string, csrf: string) => request<any>("/api/v1/mobile/manifests", { ...json({ course_id }), headers: { "X-CSRF-Token": csrf } }),
  content: (manifest_id: string) => request<any>(`/api/v1/mobile/manifests/${manifest_id}/content`),
  sync: (events: unknown[], csrf: string) => request<any>("/api/v1/mobile/sync", { ...json({ events }), headers: { "X-CSRF-Token": csrf } }),
  preferences: () => request<any>("/api/v1/mobile/preferences"),
  updatePreferences: (body: unknown, csrf: string) => request<any>("/api/v1/mobile/preferences", { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  notifications: () => request<any>("/api/v1/mobile/notifications"),
  updateNotifications: (body: unknown, csrf: string) => request<any>("/api/v1/mobile/notifications", { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  push: (body: unknown, csrf: string) => request<any>("/api/v1/mobile/push-subscriptions", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  removePush: (body: unknown, csrf: string) => request<any>("/api/v1/mobile/push-subscriptions", { method: "DELETE", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  instructor: () => request<any>("/api/v1/mobile/instructor/offline-settings"),
  operations: () => request<any>("/api/v1/mobile/platform/operations"),
};
export const aiCompanionApi = {
  dashboard: () => request<any>("/api/v1/ai-companion/dashboard"),
  profile: () => request<any>("/api/v1/ai-companion/profile"),
  updateProfile: (body: unknown, csrf: string) => request<any>("/api/v1/ai-companion/profile", { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  sessions: () => request<any>("/api/v1/ai-companion/study-sessions"),
  createSession: (body: unknown, csrf: string) => request<any>("/api/v1/ai-companion/study-sessions", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  updateSession: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/ai-companion/study-sessions/${id}`, { method: "PATCH", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  revision: () => request<any>("/api/v1/ai-companion/revision"),
  review: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/ai-companion/revision/${id}/review`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  recommendations: () => request<any>("/api/v1/ai-companion/recommendations"),
  goals: () => request<any>("/api/v1/ai-companion/goals"),
  createGoal: (body: unknown, csrf: string) => request<any>("/api/v1/ai-companion/goals", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  insights: () => request<any>("/api/v1/ai-companion/insights"),
  planner: () => request<any>("/api/v1/ai-companion/planner"),
  createPlan: (body: unknown, csrf: string) => request<any>("/api/v1/ai-companion/planner", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  voiceStatus: () => request<any>("/api/v1/ai-companion/voice/status"),
  voiceSession: (body: unknown, csrf: string) => request<any>("/api/v1/ai-companion/voice/sessions", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  privacyDelete: (csrf: string) => request<any>("/api/v1/ai-companion/privacy", { method: "DELETE", headers: { "X-CSRF-Token": csrf } }),
  instructorInsights: () => request<any>("/api/v1/ai-companion/instructor/insights"),
  operations: () => request<any>("/api/v1/ai-companion/platform/operations"),
};

export const operationsApi = {
  status: () => request<any>("/api/v1/status"),
  monitoring: () => request<any>("/api/v1/platform/monitoring"),
  dashboard: () => Promise.all([request<any>("/api/v1/platform/quality"), request<any>("/api/v1/platform/monitoring"), request<any>("/api/v1/platform/operations/incidents")]),
  feedback: (body: unknown, csrf: string) => request<any>("/api/v1/feedback", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  myFeedback: () => request<any[]>("/api/v1/feedback/my"),
  bugs: (body: unknown, csrf: string) => request<any>("/api/v1/support/report-bug", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  myBugs: () => request<any[]>("/api/v1/support/report-bug/my"),
  incidents: () => request<any[]>("/api/v1/platform/operations/incidents"),
  improvements: () => request<any[]>("/api/v1/platform/improvements"),
  releases: () => request<any[]>("/api/v1/platform/releases"),
  flags: () => request<any[]>("/api/v1/platform/feature-flags"),
  maintenance: () => request<any[]>("/api/v1/platform/maintenance"),
  backups: () => request<any>("/api/v1/platform/backups"),
  reviews: () => request<any[]>("/api/v1/platform/reviews"),
};

export const scalabilityApi = {
  dashboard: () => request<any>("/api/v1/platform/scalability"),
  database: () => request<any>("/api/v1/platform/scalability/database"),
  workers: () => request<any>("/api/v1/platform/scalability/workers"),
  runners: () => request<any>("/api/v1/platform/scalability/runners"),
  cdn: () => request<any>("/api/v1/platform/scalability/cdn"),
  ai: () => request<any>("/api/v1/platform/scalability/ai"),
  costs: () => request<any>("/api/v1/platform/scalability/costs"),
  policies: () => request<any[]>("/api/v1/platform/scalability/policies"),
  events: () => request<any[]>("/api/v1/platform/scalability/events"),
  recovery: () => request<any>("/api/v1/platform/scalability/recovery"),
};

export const marketplaceApi = {
  home: () => request<any>("/api/v1/marketplace"),
  search: (query = "") => request<any>(`/api/v1/marketplace/search${query}`),
  resources: () => request<any>("/api/v1/marketplace/resources"),
  resource: (slug: string) => request<any>(`/api/v1/marketplace/resources/${slug}`),
  instructors: (slug: string) => request<any>(`/api/v1/marketplace/instructors/${encodeURIComponent(slug)}`),
  contributors: () => request<any[]>("/api/v1/marketplace/contributors"),
  requestVerification: (body: unknown, csrf: string) => request<any>("/api/v1/marketplace/instructors/verification", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  recommended: () => request<any>("/api/v1/marketplace/recommended"),
  collections: () => request<any[]>("/api/v1/marketplace/collections"),
  createCollection: (body: unknown, csrf: string) => request<any>("/api/v1/marketplace/collections", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  createResource: (body: unknown, csrf: string) => request<any>("/api/v1/marketplace/resources", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  submit: (id: string, csrf: string) => request<any>(`/api/v1/marketplace/resources/${id}/submit`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  review: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/marketplace/resources/${id}/reviews`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  report: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/marketplace/resources/${id}/report`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  moderation: () => request<any>("/api/v1/marketplace/moderation/queue"),
  verificationQueue: () => request<any[]>("/api/v1/marketplace/moderation/verification"),
  decideVerification: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/marketplace/moderation/verification/${id}`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  decide: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/marketplace/moderation/reviews/${id}`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  analytics: () => request<any>("/api/v1/marketplace/analytics"),
  instructorAnalytics: () => request<any>("/api/v1/marketplace/instructor/analytics"),
};

export const instructorAcademyApi = {
  dashboard: () => request<any>("/api/v1/instructor-academy/dashboard"),
  onboarding: () => request<any>("/api/v1/instructor-academy/onboarding"),
  submitOnboarding: (body: unknown, csrf: string) => request<any>("/api/v1/instructor-academy/onboarding", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  standards: () => request<any[]>("/api/v1/instructor-academy/standards"),
  training: () => request<any[]>("/api/v1/instructor-academy/training"),
  enrollTraining: (id: string, csrf: string) => request<any>(`/api/v1/instructor-academy/training/${id}/enroll`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  development: () => request<any[]>("/api/v1/instructor-academy/development"),
  createPlan: (body: unknown, csrf: string) => request<any>("/api/v1/instructor-academy/development", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  quality: () => request<any[]>("/api/v1/instructor-academy/quality"),
  peerReview: (body: unknown, csrf: string) => request<any>("/api/v1/instructor-academy/peer-reviews", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  analytics: () => request<any>("/api/v1/instructor-academy/analytics"),
  aiCoach: () => request<any>("/api/v1/instructor-academy/ai-coach"),
  certifications: () => request<any>("/api/v1/instructor-academy/certifications"),
  appeal: (body: unknown, csrf: string) => request<any>("/api/v1/instructor-academy/appeals", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  platform: () => request<any>("/api/v1/instructor-academy/platform/overview"),
  applications: () => request<any[]>("/api/v1/instructor-academy/platform/applications"),
  decideApplication: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/instructor-academy/platform/applications/${id}`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
};

export const studentSuccessApi = {
  dashboard: () => request<any>("/api/v1/student-success/dashboard"),
  tickets: () => request<any[]>("/api/v1/student-success/tickets"),
  createTicket: (body: unknown, csrf: string) => request<any>("/api/v1/student-success/tickets", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  ticket: (id: string) => request<any>(`/api/v1/student-success/tickets/${id}`),
  message: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/student-success/tickets/${id}/messages`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  transition: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/student-success/tickets/${id}/transition`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  signals: () => request<any>("/api/v1/student-success/learning-signals"),
  dismissSignal: (id: string, csrf: string) => request<any>(`/api/v1/student-success/learning-signals/${id}/dismiss`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  plans: () => request<any[]>("/api/v1/student-success/support-plans"),
  createPlan: (body: unknown, csrf: string) => request<any>("/api/v1/student-success/support-plans", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  updatePlan: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/student-success/support-plans/${id}`, { method: "PATCH", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  escalateMentor: (body: unknown, csrf: string) => request<any>("/api/v1/student-success/mentorship/escalations", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  guidance: () => request<any>("/api/v1/student-success/guidance"),
  help: (search = "") => request<any[]>(`/api/v1/student-success/help${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  feedback: () => request<any[]>("/api/v1/student-success/feedback"),
  outcomes: () => request<any>("/api/v1/student-success/outcomes"),
  privacy: () => request<any>("/api/v1/student-success/privacy"),
  updatePrivacy: (body: unknown, csrf: string) => request<any>("/api/v1/student-success/privacy", { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  staffTickets: () => request<any[]>("/api/v1/student-success/staff/tickets"),
  assignTicket: (id: string, staffId: string, csrf: string) => request<any>(`/api/v1/student-success/staff/tickets/${id}/assign?staff_id=${encodeURIComponent(staffId)}`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  instructorTickets: () => request<any[]>("/api/v1/student-success/instructor/tickets"),
  platform: () => request<any>("/api/v1/student-success/platform/overview"),
};

export const assessmentApi = {
  center: () => request<any>("/api/v1/assessments"),
  detail: (id: string) => request<any>(`/api/v1/assessments/${id}`),
  competencies: () => request<any>("/api/v1/assessments/competencies"),
  passport: () => request<any>("/api/v1/assessments/skill-passport"),
  credentials: () => request<any>("/api/v1/assessments/credentials"),
  verify: (id: string) => request<any>(`/api/v1/assessments/credentials/verify/${encodeURIComponent(id)}`),
  create: (body: unknown, csrf: string) => request<any>("/api/v1/assessments", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  version: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/${id}/versions`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  question: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/${id}/questions`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  publish: (id: string, csrf: string) => request<any>(`/api/v1/assessments/${id}/publish`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  start: (id: string, csrf: string) => request<any>(`/api/v1/assessments/${id}/attempts`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  answer: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/attempts/${id}/answers`, { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  submit: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/attempts/${id}/submit`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  appeal: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/attempts/${id}/appeals`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  grading: () => request<any[]>("/api/v1/assessments/instructor/grading"),
  grade: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/assessments/attempts/${id}/grade`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  integrity: () => request<any>("/api/v1/assessments/integrity"),
  analytics: (id: string) => request<any>(`/api/v1/assessments/analytics/${id}`),
  platformCredentials: () => request<any>("/api/v1/assessments/platform/credentials"),
  issueCredential: (body: unknown, csrf: string) => request<any>("/api/v1/assessments/platform/credentials", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  revokeCredential: (id: string, reason: string, csrf: string) => request<any>(`/api/v1/assessments/platform/credentials/${id}/revoke?reason=${encodeURIComponent(reason)}`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
};

export const careerNetworkApi = {
  dashboard: () => request<any>("/api/v1/career-network/dashboard"),
  talentProfile: () => request<any>("/api/v1/career-network/talent-profile"),
  saveTalentProfile: (body: unknown, csrf: string) => request<any>("/api/v1/career-network/talent-profile", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  visibility: () => request<any>("/api/v1/career-network/visibility"),
  saveVisibility: (body: unknown, csrf: string) => request<any>("/api/v1/career-network/visibility", { method: "PUT", body: JSON.stringify(body), headers: { "X-CSRF-Token": csrf } }),
  profile: (username: string) => request<any>(`/api/v1/career-network/profiles/${encodeURIComponent(username)}`),
  skillGap: (role = "") => request<any>(`/api/v1/career-network/skill-gap${role ? `?role_slug=${encodeURIComponent(role)}` : ""}`),
  jobs: (query = "") => request<any[]>(`/api/v1/career-network/jobs${query}`),
  saveJob: (id: string, csrf: string) => request<any>(`/api/v1/career-network/jobs/${id}/save`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  employer: (body: unknown, csrf: string) => request<any>("/api/v1/career-network/employer/organizations", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  createJob: (body: unknown, csrf: string) => request<any>("/api/v1/career-network/employer/jobs", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  talent: (query = "") => request<any[]>(`/api/v1/career-network/employer/talent${query}`),
  platform: () => request<any>("/api/v1/career-network/platform/overview"),
  employerDecision: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/career-network/platform/employers/${id}/decision`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  jobDecision: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/career-network/platform/jobs/${id}/decision`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  report: (body: unknown, csrf: string) => request<any>("/api/v1/career-network/reports", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
};

export const communityNetworkApi = {
  hub: () => request<any>("/api/v1/community-network/hub"),
  clubs: (technology = "") => request<any[]>(`/api/v1/community-network/clubs${technology ? `?technology=${encodeURIComponent(technology)}` : ""}`),
  createClub: (body: unknown, csrf: string) => request<any>("/api/v1/community-network/clubs", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  joinClub: (id: string, csrf: string) => request<any>(`/api/v1/community-network/clubs/${id}/join`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  developers: (search = "") => request<any[]>(`/api/v1/community-network/developers${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  connect: (body: unknown, csrf: string) => request<any>("/api/v1/community-network/connections", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  peer: (body: unknown, csrf: string) => request<any>("/api/v1/community-network/peer-learning", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  peerRequests: () => request<any[]>("/api/v1/community-network/peer-learning"),
  events: () => request<any[]>("/api/v1/community-network/events"),
  createEvent: (body: unknown, csrf: string) => request<any>("/api/v1/community-network/events", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  registerEvent: (id: string, csrf: string) => request<any>(`/api/v1/community-network/events/${id}/register`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  feed: () => request<any[]>("/api/v1/community-network/feed"),
  reputation: () => request<any>("/api/v1/community-network/reputation"),
  report: (body: unknown, csrf: string) => request<any>("/api/v1/community-network/reports", { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  moderation: () => request<any[]>("/api/v1/community-network/moderation"),
  analytics: () => request<any>("/api/v1/community-network/analytics"),
};

export const gamificationNetworkApi = {
  dashboard: () => request<any>("/api/v1/gamification-network/dashboard"),
  quests: () => request<any[]>("/api/v1/gamification-network/quests"),
  completeQuest: (id: string, csrf: string) => request<any>(`/api/v1/gamification-network/quests/${id}/complete`, { ...json({}), headers: { "X-CSRF-Token": csrf } }),
  challenges: (search = "") => request<any[]>(`/api/v1/gamification-network/challenges/global${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  competitions: () => request<any[]>("/api/v1/gamification-network/competitions"),
  leaderboards: (period = "all_time") => request<any>(`/api/v1/gamification-network/leaderboards?period=${period}`),
  appeal: (id: string, body: unknown, csrf: string) => request<any>(`/api/v1/gamification-network/competitions/${id}/appeals`, { ...json(body), headers: { "X-CSRF-Token": csrf } }),
  integrity: () => request<any[]>("/api/v1/gamification-network/platform/integrity"),
  analytics: () => request<any>("/api/v1/gamification-network/platform/analytics"),
};

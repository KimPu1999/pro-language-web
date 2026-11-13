import { api } from "./api";

export const challengeAdminApi = {
  create: (body: unknown, csrf: string) => fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? ""}/api/v1/challenges/admin`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify(body) }).then(async response => { if (!response.ok) throw new Error(`API request failed (${response.status})`); return response.json(); }),
  addLanguage: (id: string, body: unknown, csrf: string) => fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? ""}/api/v1/challenges/admin/${id}/languages`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify(body) }).then(async response => { if (!response.ok) throw new Error(`API request failed (${response.status})`); return response.json(); }),
  addTest: (id: string, body: unknown, csrf: string) => fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? ""}/api/v1/challenges/admin/${id}/tests`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify(body) }).then(async response => { if (!response.ok) throw new Error(`API request failed (${response.status})`); return response.json(); }),
};
void api;

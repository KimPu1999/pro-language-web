type ValidationIssue = { loc?: (string | number)[]; msg?: string };

export function apiErrorMessage(response: Response, path: string, method: string, detail: unknown, fallback: string) {
  if (response.status === 405) {
    const allow = response.headers.get("allow");
    return `Method Not Allowed: ${method} ${path}. Allowed method(s): ${allow || "not reported"}.`;
  }
  if (response.status === 401) return "Your administrator session has expired. Sign in again.";
  if (response.status === 403) return "You do not have permission to perform this action.";
  if (Array.isArray(detail)) {
    const issues = (detail as ValidationIssue[]).map(issue => {
      const field = issue.loc?.filter(item => item !== "body" && item !== "query").join(".") || "field";
      return `${field}: ${issue.msg || "is invalid"}`;
    });
    if (issues.length) return issues.join("; ");
  }
  if (typeof detail === "string" && detail.trim()) return detail;
  return `${fallback} (${response.status})`;
}

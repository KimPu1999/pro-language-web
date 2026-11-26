"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

export type Locale = "en" | "my";
type Messages = Record<string, string>;
const messages: Record<Locale, Messages> = {
  en: { home: "Home", courses: "Courses", projects: "Projects", challenges: "Challenges", careers: "Careers", tools: "Tools", about: "About", contact: "Contact", profile: "Profile", signIn: "Sign in", signOut: "Sign out", language: "Language", backToCourse: "Back to course", course: "Course", curriculum: "Course curriculum", courseLessons: "Course lessons", complete: "complete", lesson: "Lesson", module: "Module", bookmark: "Bookmark", bookmarked: "Bookmarked", markComplete: "Mark complete", completed: "Completed", lessonMarked: "Lesson marked complete.", lessonReopened: "Lesson reopened.", copied: "Copied", copy: "Copy", codeExamples: "Code examples", knowledgeCheck: "Knowledge check", submitQuiz: "Submit quiz", submitting: "Submitting…", latestResult: "Latest result", lastVisited: "Last visited", myanmarMissing: "Myanmar translation is not available yet. Showing the approved English content.", loading: "Loading…", save: "Save", cancel: "Cancel" },
  my: { home: "ပင်မစာမျက်နှာ", courses: "သင်တန်းများ", projects: "ပရောဂျက်များ", challenges: "စိန်ခေါ်မှုများ", careers: "အလုပ်အကိုင်လမ်းကြောင်းများ", tools: "ကိရိယာများ", about: "အကြောင်း", contact: "ဆက်သွယ်ရန်", profile: "ပရိုဖိုင်", signIn: "ဝင်ရောက်ရန်", signOut: "ထွက်ရန်", language: "ဘာသာစကား", backToCourse: "သင်တန်းသို့ ပြန်သွားရန်", course: "သင်တန်း", curriculum: "သင်တန်းသင်ရိုး", courseLessons: "သင်တန်းသင်ခန်းစာများ", complete: "ပြီးဆုံး", lesson: "သင်ခန်းစာ", module: "အခန်း", bookmark: "မှတ်သားရန်", bookmarked: "မှတ်သားထားသည်", markComplete: "ပြီးဆုံးအဖြစ် မှတ်ရန်", completed: "ပြီးဆုံးပြီ", lessonMarked: "သင်ခန်းစာကို ပြီးဆုံးအဖြစ် မှတ်သားပြီးပါပြီ။", lessonReopened: "သင်ခန်းစာကို ပြန်ဖွင့်ပြီးပါပြီ။", copied: "ကူးယူပြီးပါပြီ", copy: "ကူးယူရန်", codeExamples: "ကုဒ်နမူနာများ", knowledgeCheck: "နားလည်မှု စစ်ဆေးရန်", submitQuiz: "မေးခွန်းစာမေးပွဲ ပို့ရန်", submitting: "ပို့နေသည်…", latestResult: "နောက်ဆုံးရလဒ်", lastVisited: "နောက်ဆုံးကြည့်ရှုချိန်", myanmarMissing: "မြန်မာဘာသာပြန် မရရှိသေးပါ။ ခွင့်ပြုထားသော အင်္ဂလိပ်အကြောင်းအရာကို ပြသနေပါသည်။", loading: "ဖွင့်နေသည်…", save: "သိမ်းရန်", cancel: "ပယ်ဖျက်ရန်" },
};
type ContextValue = { locale: Locale; setLocale: (locale: Locale) => void; t: (key: string) => string; localized: (english?: string | null, burmese?: string | null) => string };
const Context = createContext<ContextValue | null>(null);
function cookie(name: string) { return typeof document === "undefined" ? "" : document.cookie.split("; ").find(value => value.startsWith(`${name}=`))?.split("=")[1] ?? ""; }
function csrf() { return cookie("cm_csrf"); }
export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en");
  const [ready, setReady] = useState(false);
  useEffect(() => { const stored = cookie("cm_locale"); if (stored === "my" || stored === "mm") setLocale("my"); if (stored === "en") setLocale("en"); fetch("/api/v1/auth/me", { credentials: "include" }).then(response => response.ok ? response.json() : null).then(user => { const preferred = user?.profile?.preferred_language; if (preferred === "my" || preferred === "mm") setLocale("my"); if (preferred === "en") setLocale("en"); }).catch(() => undefined).finally(() => setReady(true)); }, []);
  useEffect(() => { if (!ready) return; document.cookie = `cm_locale=${locale}; Max-Age=31536000; Path=/; SameSite=Lax`; document.documentElement.lang = locale; if (csrf()) fetch("/api/v1/me/locale", { method: "PATCH", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() }, body: JSON.stringify({ language: locale }) }).catch(() => undefined); }, [locale, ready]);
  const value = useMemo(() => ({ locale, setLocale, t: (key: string) => messages[locale][key] ?? messages.en[key] ?? key, localized: (english?: string | null, burmese?: string | null) => locale === "my" && burmese?.trim() ? burmese : english ?? "" }), [locale]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useI18n() { const value = useContext(Context); if (!value) throw new Error("useI18n must be used inside I18nProvider"); return value; }

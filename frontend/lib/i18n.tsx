"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, localeApi } from "@/lib/api";

export type Locale = "en" | "my";
type Messages = Record<string, string>;

const messages: Record<Locale, Messages> = {
  en: {
    home: "Home", courses: "Courses", projects: "Projects", challenges: "Challenges", careers: "Careers", tools: "Tools", about: "About", contact: "Contact", dashboard: "Dashboard", profile: "Profile", login: "Log in", joinFree: "Join free", logout: "Log out", search: "Search", learningPaths: "Learning paths", community: "Community", students: "Students", instructors: "Instructors", contentReview: "Content Review", mediaLibrary: "Media Library", analytics: "Analytics", notifications: "Notifications", settings: "Settings", language: "Language", previous: "Previous", next: "Next", bookmark: "Bookmark", bookmarked: "Bookmarked", completed: "Completed", markComplete: "Mark complete", complete: "complete", lesson: "Lesson", module: "Module", explainedExamples: "Explained examples", readCode: "Read the code and expected behavior before trying it yourself.", example: "Example", signInProgress: "Sign in and enroll to save progress", lessonMarked: "Lesson marked complete.", signInBookmark: "Sign in to bookmark this lesson.", myanmarMissing: "Myanmar translation is not available yet. Showing the English lesson.", adminWorkspace: "Admin workspace", managePlatform: "Manage your learning platform", platformControl: "Platform Control Center", workspace: "Workspace", peopleContent: "People & content", insights: "Insights", operations: "Operations", navigation: "Navigation", needHelp: "Need help?", viewHealth: "View health", translations: "Translations", translationCoverage: "Translation coverage", missing: "Missing", available: "Available", editCurriculum: "Edit curriculum", reviewQueue: "Review queue", noTranslation: "No Burmese translation is stored for this item yet.", save: "Save", cancel: "Cancel",
  },
  my: {
    home: "ပင်မစာမျက်နှာ", courses: "သင်တန်းများ", projects: "ပရောဂျက်များ", challenges: "စိန်ခေါ်မှုများ", careers: "အလုပ်အကိုင်လမ်းကြောင်းများ", tools: "ကိရိယာများ", about: "အကြောင်း", contact: "ဆက်သွယ်ရန်", dashboard: "ဒက်ရှ်ဘုတ်", profile: "ပရိုဖိုင်", login: "ဝင်ရောက်ရန်", joinFree: "အခမဲ့ စတင်ရန်", logout: "ထွက်ရန်", search: "ရှာဖွေရန်", learningPaths: "လေ့လာရေးလမ်းကြောင်းများ", community: "အသိုင်းအဝိုင်း", students: "သင်ယူသူများ", instructors: "ဆရာများ", contentReview: "အကြောင်းအရာ စစ်ဆေးမှု", mediaLibrary: "မီဒီယာစာကြည့်တိုက်", analytics: "ခွဲခြမ်းစိတ်ဖြာမှု", notifications: "အသိပေးချက်များ", settings: "ဆက်တင်များ", language: "ဘာသာစကား", previous: "ယခင်", next: "နောက်တစ်ခု", bookmark: "မှတ်သားရန်", bookmarked: "မှတ်သားထားသည်", completed: "ပြီးဆုံးပြီ", markComplete: "ပြီးဆုံးအဖြစ် မှတ်ရန်", complete: "ပြီးဆုံး", lesson: "သင်ခန်းစာ", module: "အခန်း", explainedExamples: "ရှင်းလင်းထားသော နမူနာများ", readCode: "ကိုယ်တိုင်မစမ်းမီ ကုဒ်နှင့် မျှော်မှန်းရလဒ်ကို ဖတ်ပါ။", example: "နမူနာ", signInProgress: "တိုးတက်မှုသိမ်းရန် ဝင်ရောက်ပြီး သင်တန်းစာရင်းသွင်းပါ", lessonMarked: "သင်ခန်းစာကို ပြီးဆုံးအဖြစ် မှတ်သားပြီးပါပြီ။", signInBookmark: "ဤသင်ခန်းစာကို မှတ်သားရန် ဝင်ရောက်ပါ။", myanmarMissing: "မြန်မာဘာသာပြန် မရရှိသေးပါ။ အင်္ဂလိပ်သင်ခန်းစာကို ပြသနေပါသည်။", adminWorkspace: "စီမံခန့်ခွဲရေး အလုပ်နေရာ", managePlatform: "သင်ယူရေးပလက်ဖောင်းကို စီမံပါ", platformControl: "ပလက်ဖောင်း ထိန်းချုပ်ရေးစင်တာ", workspace: "အလုပ်နေရာ", peopleContent: "လူများနှင့် အကြောင်းအရာ", insights: "အချက်အလက်များ", operations: "လုပ်ငန်းများ", navigation: "လမ်းညွှန်", needHelp: "အကူအညီလိုပါသလား။", viewHealth: "စနစ်အခြေအနေကြည့်ရန်", translations: "ဘာသာပြန်များ", translationCoverage: "ဘာသာပြန် လွှမ်းခြုံမှု", missing: "မရှိသေး", available: "ရရှိနိုင်", editCurriculum: "သင်ရိုးပြင်ရန်", reviewQueue: "စစ်ဆေးရန်စာရင်း", noTranslation: "ဤအကြောင်းအရာအတွက် မြန်မာဘာသာပြန် မသိမ်းထားသေးပါ။", save: "သိမ်းရန်", cancel: "ပယ်ဖျက်ရန်",
  },
};

const supplementalMessages: Record<Locale, Messages> = {
  en: { learnProgramming: "Learn programming from first principles", chooseLanguage: "Choose a language, follow its prerequisites, and learn the theory before you ever need to write or execute code." },
  my: { learnProgramming: "Programming ကို အခြေခံမှ စတင်လေ့လာပါ", chooseLanguage: "ဘာသာစကားတစ်ခုရွေးပြီး လိုအပ်သောအခြေခံများကို လိုက်နာလေ့လာပါ။ ကုဒ်ရေးခြင်းမစမီ သီအိုရီကို နားလည်ပါ။" },
};

type I18nValue = { locale: Locale; setLocale: (locale: Locale) => void; t: (key: string) => string; localized: (english?: string | null, burmese?: string | null) => string };
const I18nContext = createContext<I18nValue | null>(null);

function readCookie(name: string) {
  if (typeof document === "undefined") return "";
  return document.cookie.split("; ").find(item => item.startsWith(`${name}=`))?.split("=")[1] ?? "";
}

function readCsrf() { return readCookie("cm_csrf"); }

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const cookieLocale = readCookie("cm_locale");
    if (cookieLocale === "en") setLocaleState("en");
    if (cookieLocale === "my" || cookieLocale === "mm") setLocaleState("my");
    api.me().then(user => {
      const preferred = user.profile?.preferred_language;
      if (preferred === "en") setLocaleState("en");
      if (preferred === "my" || preferred === "mm") setLocaleState("my");
    }).catch(() => {}).finally(() => setReady(true));
  }, []);

  useEffect(() => {
    if (!ready) return;
    document.cookie = `cm_locale=${locale}; Max-Age=31536000; Path=/; SameSite=Lax`;
    document.documentElement.lang = locale;
    if (readCsrf()) localeApi.set(locale, readCsrf()).catch(() => {});
  }, [locale, ready]);

  const value = useMemo<I18nValue>(() => ({
    locale,
    setLocale: setLocaleState,
    t: (key) => messages[locale][key] ?? supplementalMessages[locale][key] ?? messages.en[key] ?? supplementalMessages.en[key] ?? key,
    localized: (english, burmese) => locale === "my" && burmese?.trim() ? burmese : english ?? "",
  }), [locale]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside I18nProvider");
  return value;
}

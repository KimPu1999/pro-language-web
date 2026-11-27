"use client";

import { Card } from "@/components/ui";
import { useI18n } from "@/lib/i18n";

export default function CommunityGuidelines() {
  const { locale } = useI18n();
  const myanmar = locale === "my";
  const sections = myanmar ? [
    ["လေးစားစွာ ဆွေးနွေးပါ", "အခြားသင်ယူသူများကို လေးစားပြီး အကြောင်းအရာကို အာရုံစိုက်ဆွေးနွေးပါ။"],
    ["ကုဒ်ကို လုံခြုံစွာ မျှဝေပါ", "Password၊ token၊ private key သို့မဟုတ် ကိုယ်ရေးအချက်အလက်များကို မထည့်ပါနှင့်။ User code ကို server တွင် execute မလုပ်ပါ။"],
    ["အကူအညီဖြစ်သော အဖြေများပေးပါ", "ပြဿနာကို ရှင်းလင်းစွာဖတ်ပြီး အကြောင်းပြချက်နှင့် စမ်းသပ်နိုင်သော အဆင့်များကို ထည့်ရေးပါ။"],
    ["Spam နှင့် နှောင့်ယှက်မှု မပြုပါနှင့်", "Spam၊ မုန်းတီးစကား၊ မလုံခြုံသော link နှင့် မသင့်လျော်သောအကြောင်းအရာများကို report လုပ်နိုင်ပါသည်။"],
  ] : [
    ["Keep discussions respectful", "Address the problem and the code, and give other learners room to ask questions."],
    ["Share code safely", "Never include passwords, tokens, private keys, or personal records. User code is stored as text and is never executed on the server."],
    ["Write helpful answers", "Explain the reasoning and verification steps so the author can learn and reproduce the result."],
    ["No spam or harassment", "Spam, abuse, unsafe links, and inappropriate content may be reported for moderator review."],
  ];
  return <section className="mx-auto max-w-4xl px-5 py-12 lg:px-8"><p className="text-sm text-indigo-300">{myanmar ? "အသိုင်းအဝိုင်း" : "Community"}</p><h1 className="mt-2 text-4xl font-bold">{myanmar ? "အသိုင်းအဝိုင်း လမ်းညွှန်ချက်များ" : "Community guidelines"}</h1><p className="mt-4 text-slate-400">{myanmar ? "အားလုံးအတွက် လုံခြုံပြီး အကူအညီဖြစ်သော developer learning space တစ်ခုကို အတူတကွ ထိန်းသိမ်းပါ။" : "Help keep this developer learning space safe, focused, and useful for everyone."}</p><div className="mt-8 space-y-4">{sections.map(([title, body]) => <Card className="p-6" key={title}><h2 className="text-xl font-semibold">{title}</h2><p className="mt-3 leading-7 text-slate-400">{body}</p></Card>)}</div></section>;
}

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, MessageSquare, Search, Sparkles, Users } from "lucide-react";
import { Badge, Card, EmptyState, Skeleton } from "@/components/ui";
import { communityApi } from "@/lib/ai-api";
import { useI18n } from "@/lib/i18n";

const filters = [["All posts", ""], ["Questions", "question"], ["Discussions", "discussion"], ["Tutorials", "tutorial"], ["Showcases", "project_showcase"]] as const;

export default function Community() {
  const { locale } = useI18n();
  const [items, setItems] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState("latest");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const copy = locale === "my"
    ? { badge: "လူတိုင်းအတွက် အသိုင်းအဝိုင်း", title: "အတူတကွ လေ့လာပြီး", titleAccent: "အတူတကွ တည်ဆောက်ပါ။", intro: "မေးခွန်းများမေးရန်၊ ကိုယ်တိုင်တည်ဆောက်ထားသည်များကို မျှဝေရန်နှင့် အခြား developer များနှင့် လေ့လာရန် နေရာတစ်ခု။", ask: "မေးခွန်းမေးရန်", discussion: "ဆွေးနွေးချက်ဖန်တီးရန်", search: "ဆွေးနွေးချက်များ ရှာရန်", latest: "နောက်ဆုံးဆွေးနွေးချက်များ", browse: "မေးခွန်းများ ကြည့်ရန်", noData: "အများမြင် ဆွေးနွေးချက် မရှိသေးပါ", noDataDescription: "ပထမဆုံး ဆွေးနွေးချက်ကို စတင်ပါ။", unavailable: "Community API ကို မရရှိနိုင်ပါ။", retry: "ပြန်ကြိုးစားရန်", categories: "အမျိုးအစားများ", explore: "အသိုင်းအဝိုင်းကို လေ့လာရန်", groups: "လေ့လာရေးအဖွဲ့များ", showcases: "ပရောဂျက်ပြခန်း", members: "အဖွဲ့ဝင်များ", snippets: "ကုဒ်အပိုင်းများ", guidelines: "အသိုင်းအဝိုင်းလမ်းညွှန်ချက်များ" }
    : { badge: "Community, open to everyone", title: "Build in public.", titleAccent: "Learn together.", intro: "A thoughtful place for developers to ask better questions, share work, and find their next study partner.", ask: "Ask a question", discussion: "Create discussion", search: "Search discussions", latest: "Latest conversations", browse: "Browse questions", noData: "No public discussions yet", noDataDescription: "Be the first developer to start a conversation.", unavailable: "The Community API is unavailable.", retry: "Retry", categories: "Categories", explore: "Explore community", groups: "Study groups", showcases: "Project showcases", members: "Meet members", snippets: "Code snippets", guidelines: "Community guidelines" };

  const load = async (nextQuery = query, nextType = type, nextCategory = category, nextSort = sort) => {
    setLoading(true); setError("");
    try {
      const response = await communityApi.feed(nextQuery, nextType, { category_id: nextCategory || undefined, sort: nextSort });
      setItems(response.items ?? []);
    } catch (cause) {
      setItems([]); setError(cause instanceof Error ? cause.message : copy.unavailable);
    } finally { setLoading(false); }
  };

  useEffect(() => {
    let active = true;
    Promise.all([communityApi.categories(), communityApi.feed("", "", { sort: "latest" })]).then(([categoryRows, feed]) => {
      if (!active) return;
      setCategories(categoryRows); setItems(feed.items ?? []); setError("");
    }).catch(cause => { if (active) setError(cause instanceof Error ? cause.message : copy.unavailable); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
    // The first load intentionally uses the initial filter values.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const postHref = (post: any) => `/community/questions/${post.slug}`;
  return <div className="min-h-screen bg-ink">
    <section className="relative overflow-hidden border-b border-line bg-gradient-to-br from-indigo-500/15 via-ink to-ink"><div className="mx-auto max-w-7xl px-5 py-16 lg:px-8 lg:py-20"><div className="max-w-3xl"><Badge><Sparkles className="mr-1 inline h-3 w-3" />{copy.badge}</Badge><h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-6xl">{copy.title}<br /><span className="text-indigo-300">{copy.titleAccent}</span></h1><p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">{copy.intro}</p><div className="mt-8 flex flex-wrap gap-3"><Link href="/community/questions/ask?type=question" className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold hover:bg-indigo-500">{copy.ask}</Link><Link href="/community/questions/ask?type=discussion" className="rounded-xl bg-surface px-5 py-3 text-sm font-semibold hover:bg-elevated">{copy.discussion}</Link></div></div></div></section>
    <main className="mx-auto grid max-w-7xl gap-8 px-5 py-10 lg:grid-cols-[minmax(0,1fr)_300px] lg:px-8"><div><div className="flex flex-col gap-3 sm:flex-row"><div className="flex flex-1 items-center gap-3 rounded-xl bg-surface px-4"><Search className="h-4 w-4 text-slate-500" /><input value={query} onChange={event => setQuery(event.target.value)} onKeyDown={event => event.key === "Enter" && load()} placeholder={copy.search} className="w-full bg-transparent py-3 text-sm outline-none" /></div><button onClick={() => load()} className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold">{copy.search}</button></div>
      <div className="mt-4 flex flex-wrap gap-3"><div className="flex gap-2 overflow-x-auto pb-1">{filters.map(([label, value]) => <button key={value} onClick={() => { setType(value); load(query, value); }} className={`whitespace-nowrap rounded-full px-4 py-2 text-sm ${type === value ? "bg-primary text-white" : "bg-surface text-slate-400 hover:text-white"}`}>{locale === "my" && value === "" ? "အားလုံး" : locale === "my" && value === "question" ? "မေးခွန်းများ" : locale === "my" && value === "discussion" ? "ဆွေးနွေးချက်များ" : label}</button>)}</div><select aria-label="Sort discussions" value={sort} onChange={event => { setSort(event.target.value); load(query, type, category, event.target.value); }} className="rounded-full border border-line bg-surface px-4 py-2 text-sm text-slate-300"><option value="latest">Latest</option><option value="active">Most active</option><option value="votes">Most helpful</option></select></div>
      {categories.length > 0 && <div className="mt-4 flex gap-2 overflow-x-auto pb-1"><button onClick={() => { setCategory(""); load(query, type, "", sort); }} className={`whitespace-nowrap rounded-full border px-3 py-1.5 text-xs ${!category ? "border-indigo-400 bg-indigo-500/15 text-indigo-200" : "border-line text-slate-500"}`}>{copy.categories}</button>{categories.map(item => <button key={item.id} onClick={() => { setCategory(item.id); load(query, type, item.id, sort); }} className={`whitespace-nowrap rounded-full border px-3 py-1.5 text-xs ${category === item.id ? "border-indigo-400 bg-indigo-500/15 text-indigo-200" : "border-line text-slate-500"}`}>{item.name}</button>)}</div>}
      <div className="mt-7 flex items-center justify-between"><div><p className="text-sm text-slate-500">COMMUNITY FEED</p><h2 className="mt-1 text-2xl font-semibold">{copy.latest}</h2></div><Link href="/community/questions" className="text-sm text-indigo-300">{copy.browse} <ArrowRight className="ml-1 inline h-4 w-4" /></Link></div>
      {error && <Card className="mt-4 border-red-400/30 p-5 text-sm text-red-200" role="alert"><p>{error || copy.unavailable}</p><button className="mt-3 font-semibold underline" onClick={() => load()}>{copy.retry}</button></Card>}
      <div className="mt-4 space-y-3">{loading ? [1, 2, 3].map(index => <Skeleton key={index} className="h-36" />) : items.length ? items.map(post => <Link key={post.id} href={postHref(post)}><Card className="p-5 transition hover:bg-elevated"><div className="flex items-start justify-between gap-4"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><Badge className="bg-indigo-500/10 text-indigo-300">{post.post_type.replaceAll("_", " ")}</Badge>{post.category && <span className="text-xs text-slate-500">{post.category.name}</span>}{(post.tags ?? []).slice(0, 3).map((tag: string) => <span key={tag} className="text-xs text-slate-500">#{tag}</span>)}</div><h3 className="mt-3 text-lg font-semibold">{post.title}</h3><p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-400">{post.body}</p></div><ArrowRight className="h-5 w-5 shrink-0 text-slate-600" /></div><div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500"><span>{post.author?.display_name ?? "Community member"}</span><span>{post.vote_count ?? 0} votes</span><span><MessageSquare className="mr-1 inline h-3.5 w-3.5" />{post.comment_count ?? 0} replies</span></div></Card></Link>) : <EmptyState title={copy.noData} description={copy.noDataDescription} />}</div></div>
      <aside className="space-y-4"><Card className="p-5"><h3 className="font-semibold">{copy.explore}</h3><div className="mt-4 space-y-3 text-sm text-slate-400"><Link className="block hover:text-white" href="/community/groups"><Users className="mr-2 inline h-4 w-4" /> {copy.groups}</Link><Link className="block hover:text-white" href="/community/showcase">{copy.showcases}</Link><Link className="block hover:text-white" href="/community/members">{copy.members}</Link><Link className="block hover:text-white" href="/community/snippets">{copy.snippets}</Link></div></Card><Card className="p-5"><p className="text-xs font-semibold tracking-widest text-indigo-300">{copy.guidelines.toUpperCase()}</p><p className="mt-3 text-sm leading-6 text-slate-400">{locale === "my" ? "သီးခြားအချက်အလက်များနှင့် secret များကို မမျှဝေဘဲ ယဉ်ကျေးစွာ ဆွေးနွေးပါ။" : "Be specific, be kind, and keep private data and secrets out of posts. User code is stored as text and is never executed on the application server."}</p><Link href="/community/guidelines" className="mt-4 block text-sm text-white">{copy.guidelines} →</Link></Card></aside>
    </main>
  </div>;
}

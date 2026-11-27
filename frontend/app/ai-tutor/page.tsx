"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { aiApi, streamUrl } from "@/lib/ai-api";
import { csrf } from "@/components/auth-form";
import { notesApi } from "@/lib/api";
import { Card } from "@/components/ui";

type Message = { id: string; role: "user" | "assistant"; content: string; status: string; created_at?: string };
type Conversation = { id: string; title: string; language?: "en" | "mm"; lesson_id?: string | null };
type Language = "en" | "mm";
type Mode = "tutor" | "explain" | "debug" | "example" | "hint" | "practice" | "quiz" | "review" | "plan";

function MarkdownContent({ value }: { value: string }) {
  const parts = value.split(/```([\w-]*)\n?([\s\S]*?)```/g);
  return <div className="space-y-3 text-sm leading-7 text-slate-200">
    {parts.map((part, index) => {
      if (index % 3 === 1) return <span key={index} className="sr-only">{part}</span>;
      if (index % 3 === 2) return <pre key={index} className="overflow-x-auto rounded-xl border border-line bg-black/30 p-4 text-xs leading-6 text-emerald-200"><code>{part.trim()}</code></pre>;
      return part.split(/\n\s*\n/).filter(Boolean).map((block, blockIndex) => {
        const lines = block.split("\n");
        if (lines.every(line => /^\s*[-*]\s+/.test(line))) return <ul key={`${index}-${blockIndex}`} className="list-disc space-y-1 pl-5">{lines.map((line, itemIndex) => <li key={itemIndex}>{line.replace(/^\s*[-*]\s+/, "")}</li>)}</ul>;
        const heading = block.match(/^\s*(#{1,3})\s+(.+)$/);
        if (heading) return <h3 key={`${index}-${blockIndex}`} className="text-base font-semibold text-white">{heading[2]}</h3>;
        return <p key={`${index}-${blockIndex}`} className="whitespace-pre-wrap">{block}</p>;
      });
    })}
  </div>;
}

export default function AITutor() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [current, setCurrent] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [mode, setMode] = useState<Mode>("tutor");
  const [mobileHistory, setMobileHistory] = useState(false);
  const [lessonId, setLessonId] = useState<string | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const assistantRef = useRef("");

  const loadConversations = useCallback(async () => {
    const result = await aiApi.conversations(search);
    setConversations(result.items);
    if (!current && result.items[0]) setCurrent(result.items[0].id);
  }, [current, search]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setLessonId(params.get("lesson_id"));
    void loadConversations().catch(e => setError(e instanceof Error ? e.message : "Unable to load conversations"));
  }, [loadConversations]);

  useEffect(() => {
    if (!current) return;
    void aiApi.conversation(current).then(x => { setMessages(x.messages); setLanguage(x.language === "mm" ? "mm" : "en"); }).catch(e => setError(e instanceof Error ? e.message : "Unable to load conversation"));
  }, [current]);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const filtered = useMemo(() => conversations.filter(item => item.title.toLowerCase().includes(search.toLowerCase())), [conversations, search]);

  const newChat = async () => {
    try {
      const row = await aiApi.create("New conversation", csrf());
      setConversations(items => [row, ...items]); setCurrent(row.id); setMessages([]); setMobileHistory(false); setError("");
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to create chat"); }
  };

  const stop = async () => {
    abortRef.current?.abort();
    if (current) await aiApi.stop(current, csrf()).catch(() => undefined);
    setBusy(false);
  };

  const sendText = async (value: string) => {
    if (!value.trim() || !current || busy) return;
    const text = value.trim(); setInput(""); setBusy(true); setError(""); setNotice("");
    const userId = `local-user-${Date.now()}`; const assistantId = `local-assistant-${Date.now()}`; assistantRef.current = assistantId;
    setMessages(items => [...items, { id: userId, role: "user", content: text, status: "complete" }, { id: assistantId, role: "assistant", content: "", status: "streaming" }]);
    const abort = new AbortController(); abortRef.current = abort;
    try {
      const response = await fetch(streamUrl(current), { method: "POST", credentials: "include", signal: abort.signal, headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() }, body: JSON.stringify({ message: text, language, mode, context_type: lessonId ? "lesson" : undefined, context_id: lessonId || undefined }) });
      if (!response.ok) throw new Error(`AI request failed (${response.status})`);
      if (!response.body) throw new Error("AI stream unavailable");
      const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "";
      const applyEvent = (event: string) => {
        const eventName = event.split("\n").find(line => line.startsWith("event:"))?.slice(6).trim();
        const dataLine = event.split("\n").find(line => line.startsWith("data:")); if (!dataLine) return;
        const data = JSON.parse(dataLine.slice(5).trim()) as { text?: string; message?: string; code?: string };
        if (eventName === "token" && data.text) setMessages(items => items.map(item => item.id === assistantRef.current ? { ...item, content: item.content + data.text } : item));
        if (eventName === "complete") setMessages(items => items.map(item => item.id === assistantRef.current ? { ...item, status: "complete" } : item));
        if (eventName === "cancelled") setMessages(items => items.map(item => item.id === assistantRef.current ? { ...item, status: "cancelled" } : item));
        if (eventName === "error") { setError(data.message || "AI tutor is unavailable"); setMessages(items => items.map(item => item.id === assistantRef.current ? { ...item, status: "failed" } : item)); }
      };
      while (true) { const part = await reader.read(); if (part.done) break; buffer += decoder.decode(part.value, { stream: true }); const events = buffer.split("\n\n"); buffer = events.pop() || ""; events.forEach(applyEvent); }
      if (buffer.trim()) applyEvent(buffer);
    } catch (e) { if ((e as Error).name !== "AbortError") setError(e instanceof Error ? e.message : "AI tutor unavailable"); }
    finally { abortRef.current = null; setBusy(false); if (current) void aiApi.conversation(current).then(x => setMessages(x.messages)).catch(() => undefined); }
  };

  const send = () => void sendText(input);
  const regenerate = () => { const lastUser = [...messages].reverse().find(item => item.role === "user"); if (lastUser && !busy) void sendText(lastUser.content); };
  const rename = async () => { if (!current) return; const title = window.prompt("Conversation name", conversations.find(item => item.id === current)?.title || "New conversation"); if (!title?.trim()) return; await aiApi.rename(current, title.trim(), csrf()).then(row => setConversations(items => items.map(item => item.id === current ? { ...item, title: row.title } : item))).catch(e => setError(e instanceof Error ? e.message : "Unable to rename chat")); };
  const remove = async () => { if (!current || !window.confirm("Delete this conversation?")) return; await aiApi.remove(current, csrf()).then(() => { const next = conversations.find(item => item.id !== current); setConversations(items => items.filter(item => item.id !== current)); setCurrent(next?.id || ""); setMessages([]); }).catch(e => setError(e instanceof Error ? e.message : "Unable to delete chat")); };
  const saveNote = async (message: Message) => { try { await notesApi.create({ title: "AI Tutor note", content: message.content, lesson_id: lessonId }, csrf()); setNotice("Saved to your notebook."); } catch (e) { setError(e instanceof Error ? e.message : "Unable to save the note"); } };

  return <section className="mx-auto flex min-h-[calc(100vh-160px)] max-w-7xl gap-5 px-5 py-8 lg:px-8">
    <Card className={`${mobileHistory ? "block" : "hidden"} fixed inset-4 z-20 w-auto p-4 md:static md:block md:w-72 md:shrink-0`}><div className="flex items-center justify-between"><h2 className="font-semibold">Conversations</h2><button aria-label="New chat" onClick={() => void newChat()} className="rounded-lg bg-indigo-500 px-3 py-1.5">+</button></div><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search chats" className="mt-4 w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm"/><div className="mt-4 space-y-1">{filtered.map(item => <button key={item.id} onClick={() => { setCurrent(item.id); setMobileHistory(false); }} className={`w-full rounded-lg p-3 text-left text-sm ${current === item.id ? "bg-indigo-500/15 text-white" : "text-slate-400"}`}>{item.title}</button>)}</div>{mobileHistory && <button className="mt-4 text-xs text-slate-400 md:hidden" onClick={() => setMobileHistory(false)}>Close history</button>}</Card>
    <Card className="flex min-h-[620px] min-w-0 flex-1 flex-col overflow-hidden"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4"><div><p className="text-xs uppercase tracking-widest text-indigo-300">AI Programming Tutor</p><h1 className="mt-1 text-lg font-bold">Learn with guidance</h1></div><div className="flex items-center gap-2"><button onClick={() => setMobileHistory(true)} className="rounded-lg border border-line px-3 py-2 text-xs md:hidden">History</button><button onClick={() => void newChat()} className="rounded-lg bg-indigo-500 px-3 py-2 text-sm">New chat</button></div></div><div className="flex flex-wrap items-center gap-2 border-b border-line px-4 py-3"><label className="text-xs text-slate-500">Language<select value={language} onChange={e => setLanguage(e.target.value as Language)} className="ml-2 rounded-lg border border-line bg-ink px-2 py-1.5 text-xs text-slate-200"><option value="en">EN / English</option><option value="mm">MM / မြန်မာ</option></select></label><label className="text-xs text-slate-500">Mode<select value={mode} onChange={e => setMode(e.target.value as Mode)} className="ml-2 rounded-lg border border-line bg-ink px-2 py-1.5 text-xs text-slate-200"><option value="tutor">Tutor</option><option value="explain">Explain</option><option value="debug">Debug</option><option value="example">Example</option><option value="hint">Hint</option><option value="practice">Practice</option><option value="quiz">Quiz</option><option value="review">Review</option><option value="plan">Plan</option></select></label>{lessonId && <span className="rounded-full border border-indigo-400/30 px-3 py-1 text-xs text-indigo-200">Lesson context attached</span>}<div className="ml-auto flex gap-2"><button disabled={!current} onClick={() => void rename()} className="rounded-lg border border-line px-2.5 py-1.5 text-xs text-slate-300 disabled:opacity-50">Rename</button><button disabled={!current} onClick={() => void remove()} className="rounded-lg border border-red-400/20 px-2.5 py-1.5 text-xs text-red-200 disabled:opacity-50">Delete</button></div></div><div className="flex-1 space-y-5 overflow-y-auto p-5">{!messages.length && <div className="mx-auto max-w-xl py-16 text-center"><h2 className="text-2xl font-bold">Ask a programming question</h2><p className="mt-3 text-sm text-slate-400">The tutor uses authorized published learning context. It never executes code or reveals hidden tests.</p></div>}{messages.map(message => <div key={message.id} className={message.role === "user" ? "ml-auto max-w-2xl rounded-2xl bg-indigo-500/15 p-4" : "max-w-3xl rounded-2xl bg-ink p-4"}>{message.role === "assistant" ? <MarkdownContent value={message.content || "Thinking…"} /> : <p className="whitespace-pre-wrap text-sm leading-7 text-slate-100">{message.content}</p>}{message.role === "assistant" && message.content && <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-500"><button onClick={() => void navigator.clipboard.writeText(message.content)} className="hover:text-white">Copy answer</button><button onClick={() => void saveNote(message)} className="hover:text-white">Save to notebook</button><button onClick={regenerate} disabled={busy} className="hover:text-white disabled:opacity-50">Regenerate</button></div>}</div>)}<div ref={end}/></div>{(error || notice || busy) && <div className="border-t border-line px-5 py-3 text-sm">{error && <span className="text-amber-200">{error}</span>}{notice && !error && <span className="text-emerald-300">{notice}</span>}{busy && <button onClick={() => void stop()} className="float-right rounded-lg border border-amber-400/30 px-3 py-1 text-xs text-amber-200">Stop</button>}</div>}<div className="border-t border-line p-4"><div className="flex gap-3"><textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} placeholder="Ask about a lesson, code, or debugging problem…" rows={2} className="min-w-0 flex-1 resize-none rounded-xl border border-line bg-ink p-3 text-sm"/><button onClick={send} disabled={busy || !current} aria-label="Send message" className="self-end rounded-xl bg-indigo-500 px-4 py-3 text-sm font-semibold disabled:opacity-50">Send</button></div><p className="mt-2 text-xs text-slate-500">Enter to send · Shift+Enter for a new line · code is explained, never executed here.</p></div></Card>
  </section>;
}

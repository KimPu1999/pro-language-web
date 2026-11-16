"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, BookOpen, Clock, ListChecks, Sparkles } from "lucide-react";

const sections = [
  ["Introduction", "We built Languages-Platform to make practical programming education easier to access and easier to apply."],
  ["Information Collected", "The platform may process account, enrollment, progress, and support information needed to provide authenticated learning features. Administrators should review the configured data inventory before publishing this policy."],
  ["Use of Information", "Information is used to provide courses, preserve verified progress, protect accounts, respond to support requests, and improve platform reliability where configured."],
  ["Cookies and Analytics", "Browser storage may be used for preferences such as theme and navigation state. Any analytics or third-party tracking must be reviewed and configured by an administrator before this section is treated as final."],
  ["User Content and Code", "Do not submit passwords, private keys, personal secrets, or data that you are not authorized to share. Code and project content remain subject to the permissions and visibility settings shown in the platform."],
  ["Data Sharing", "We do not promise a specific provider or sharing practice here. The published version must be reviewed against the actual hosting, email, analytics, and storage configuration."],
  ["Data Retention", "Retention periods depend on the configured account, progress, support, audit, and legal records policies. Administrators should confirm the applicable periods before publishing."],
  ["Data Security", "The platform is designed around authenticated access, user-scoped records, server-side authorization, validation, and protected administrative actions. No online system can guarantee absolute security."],
  ["User Privacy Rights", "Signed-in users can use the available privacy request tools for account data requests. The available rights and response process must be reviewed for the operating jurisdiction."],
  ["Children's Privacy", "The service is not presented as a child-directed service. Administrators should publish age and consent requirements appropriate to their actual operation."],
  ["International Transfers", "Hosting and service-provider locations must be confirmed before this section is finalized."],
  ["Policy Updates", "Published changes should be versioned with an effective date and retained history."],
  ["Contact", "Use the Contact page for support questions once the configured support channel is available."],
] as const;

const terms = [
  ["Acceptance of Terms", "Using Languages-Platform means you agree to use the service lawfully and responsibly. If you do not agree, do not use the service."],
  ["Eligibility", "Account eligibility and any age or consent requirements must be confirmed by the platform operator and published here before launch."],
  ["User Accounts", "Keep account credentials private, provide accurate information, and notify the platform of suspected unauthorized access."],
  ["Educational Services", "Courses, challenges, projects, and examples are educational resources. They do not guarantee a qualification, job, result, or production readiness."],
  ["Acceptable Use", "Do not abuse the service, bypass authorization, upload malware or secrets, attack other systems, or submit content you do not have permission to use."],
  ["Code Execution Rules", "Only use supported and clearly labeled sandboxes. Never submit credentials, destructive commands, or code intended to harm systems or people."],
  ["User-Generated Content", "You are responsible for content you submit and must respect copyright, privacy, confidentiality, and applicable law."],
  ["Intellectual Property", "Platform content, branding, and software remain subject to their applicable ownership and license terms. Do not copy private solutions or hidden tests."],
  ["Submissions and Grading", "Where projects or assessments are supported, records and grades are governed by the relevant workflow and review permissions."],
  ["Payments if Applicable", "The current platform experience is presented as free learning. Any paid feature requires separate, clearly published terms before use."],
  ["Service Availability", "Features may be unavailable during maintenance, configuration changes, provider outages, or security response."],
  ["Suspension and Termination", "Access may be restricted when necessary to protect users, records, or the service, subject to the platform's review process."],
  ["Disclaimers", "Learning examples are provided for educational purposes and should be reviewed, tested, and secured before real-world use."],
  ["Limitation of Liability", "This draft does not state a governing limitation. An authorized operator and legal adviser must review and approve this section."],
  ["Governing Law", "No jurisdiction is asserted in this draft. Add the correct legal identity and governing law only after review."],
  ["Changes to Terms", "Material changes should be versioned, dated, and communicated through the platform."],
  ["Contact", "Questions about these terms should use the configured support channel shown on the Contact page."],
] as const;

export function AboutPage() {
  return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8 lg:py-16">
    <section className="relative overflow-hidden rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-500/25 via-surface to-surface p-7 sm:p-10 lg:p-14">
      <div className="pointer-events-none absolute -right-20 -top-24 h-72 w-72 rounded-full bg-violet-500/20 blur-3xl" />
      <div className="relative max-w-3xl"><span className="inline-flex items-center gap-2 rounded-full bg-indigo-400/15 px-3 py-1 text-xs font-semibold uppercase tracking-[.18em] text-indigo-200"><Sparkles size={14} /> About the platform</span><h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-6xl">Learn to code. Build real projects.</h1><p className="mt-5 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">Languages-Platform helps curious builders move from first principles to practical, reviewable software through structured learning and hands-on work.</p><div className="mt-8 flex flex-wrap gap-3"><Link href="/courses" className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500">Explore courses <ArrowRight size={16} /></Link><Link href="/projects" className="inline-flex items-center gap-2 rounded-lg border border-line px-4 py-2.5 text-sm font-semibold text-slate-200 hover:bg-elevated">View projects</Link></div></div>
    </section>
    <section className="mt-10 grid gap-5 md:grid-cols-3"><InfoCard icon={<BookOpen />} title="Structured learning" text="Follow courses with clear lessons, prerequisites, examples, and verified progress." /><InfoCard icon={<ListChecks />} title="Practice that matters" text="Use challenges and projects to turn concepts into skills you can explain and maintain." /><InfoCard icon={<Sparkles />} title="Responsible defaults" text="Learn with explicit boundaries around privacy, security, testing, and real-world use." /></section>
    <section className="mt-10 grid gap-6 lg:grid-cols-2"><InfoBlock title="Our mission" text="Make high-quality programming education accessible, practical, and honest about what has been verified. The platform favors clear explanations, small feedback loops, and projects that build durable understanding." /><InfoBlock title="Our learning approach" text="Start with a concept, inspect a complete example, practice a small change, verify the result, and connect it to a larger project. This keeps progress measurable without pretending that a page visit is mastery." /></section>
    <section className="mt-10 rounded-2xl border border-line bg-surface p-6 sm:p-8"><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Your learning journey</p><div className="mt-6 grid gap-4 md:grid-cols-4">{["Choose a path", "Learn the foundations", "Build and verify", "Keep improving"].map((step, index) => <div className="rounded-xl bg-elevated/60 p-4" key={step}><span className="text-xs font-bold text-indigo-300">0{index + 1}</span><h2 className="mt-3 font-semibold">{step}</h2><p className="mt-2 text-sm leading-6 text-slate-400">A focused step with clear evidence and a useful next action.</p></div>)}</div></section>
  </div>;
}

export function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  return <div className="mx-auto max-w-6xl px-5 py-12 lg:px-8 lg:py-16"><div className="max-w-3xl"><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Support</p><h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">Contact Languages-Platform</h1><p className="mt-4 text-base leading-8 text-slate-400">Have a question about a course, project, or account? Send a clear message and include only information you are authorized to share.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.75fr_1.25fr]"><aside className="space-y-4"><InfoCard icon={<Sparkles />} title="Support channel" text="A public support email is not configured yet. The form will not claim delivery until an administrator connects the approved email provider." /><InfoCard icon={<Clock />} title="Before you send" text="Never include passwords, access tokens, private keys, or sensitive student data in a support message." /></aside><form className="rounded-2xl border border-line bg-surface p-6 sm:p-8" onSubmit={event => { event.preventDefault(); setSubmitted(true); }}><div className="grid gap-5 sm:grid-cols-2"><Field label="Name" name="name" /><Field label="Email" name="email" type="email" /></div><Field label="Subject" name="subject" /><label className="mt-5 block text-sm font-medium text-slate-300">Message<textarea name="message" required minLength={20} maxLength={5000} className="mt-2 min-h-36 w-full rounded-lg border border-line bg-ink px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-indigo-400" /></label><button type="submit" className="mt-5 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500">Send message</button>{submitted && <p role="status" className="mt-4 rounded-lg bg-amber-400/10 p-3 text-sm text-amber-200">Message delivery is unavailable because the platform support provider is not configured. No message was marked as sent.</p>}</form></div></div>;
}

export function LegalPage({ type }: { type: "privacy" | "terms" }) {
  const isPrivacy = type === "privacy";
  const content = isPrivacy ? sections : terms;
  return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8 lg:py-16"><div className="max-w-3xl"><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Languages-Platform · {isPrivacy ? "Privacy" : "Terms"}</p><h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">{isPrivacy ? "Privacy policy" : "Terms of service"}</h1><p className="mt-4 leading-7 text-slate-400">Draft for administrator and legal review. Version 0.1 · Last updated November 16, 2026.</p></div><div className="mt-10 grid gap-8 lg:grid-cols-[210px_minmax(0,760px)] lg:items-start"><nav className="rounded-2xl border border-line bg-surface p-4 lg:sticky lg:top-24"><p className="text-xs font-semibold uppercase tracking-[.16em] text-slate-500">On this page</p><div className="mt-3 space-y-1">{content.map(([title]) => <a className="block rounded-md px-2 py-1.5 text-xs text-slate-400 hover:bg-elevated hover:text-white" href={`#${slug(title)}`} key={title}>{title}</a>)}</div></nav><article className="rounded-2xl border border-line bg-surface p-6 sm:p-8">{content.map(([title, text], index) => <section className="scroll-mt-24 border-b border-line/60 py-6 first:pt-0 last:border-0 last:pb-0" id={slug(title)} key={title}><h2 className="text-xl font-semibold text-slate-100">{index + 1}. {title}</h2><p className="mt-3 text-sm leading-7 text-slate-400">{text}</p></section>)}</article></div></div>;
}

function InfoCard({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) { return <div className="rounded-2xl border border-line bg-surface p-5"><div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/15 text-indigo-300">{icon}</div><h2 className="mt-4 font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{text}</p></div>; }
function InfoBlock({ title, text }: { title: string; text: string }) { return <div className="rounded-2xl border border-line bg-surface p-6 sm:p-8"><h2 className="text-2xl font-semibold">{title}</h2><p className="mt-4 leading-8 text-slate-400">{text}</p></div>; }
function Field({ label, name, type = "text" }: { label: string; name: string; type?: string }) { return <label className="block text-sm font-medium text-slate-300">{label}<input name={name} type={type} required className="mt-2 h-10 w-full rounded-lg border border-line bg-ink px-3 text-sm text-slate-100 outline-none focus:border-indigo-400" /></label>; }
function slug(value: string) { return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }

import Link from "next/link";
import { Sparkles, Terminal, X } from "lucide-react";

const files = [
  ["config/urls.py", "Add a named root path that points to learning.views.home."],
  ["learning/views.py", "Return an HttpResponse first, then switch to render with context."],
  ["learning/templates/learning/home.html", "Render a heading using the course_name context value."],
  ["learning/tests.py", "Assert the response status and visible heading text."],
];

export default function DjangoLabsPage() {
  return (
    <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8">
      <Link href="/courses/django" className="text-sm text-emerald-300 hover:text-white">← Back to Django course</Link>
      <div className="mt-8 max-w-3xl">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">Guided lab 01</p>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Build your first Django page</h1>
        <p className="mt-4 text-lg leading-8 text-slate-400">Create a project, connect one app, route a request, and render a tested welcome page.</p>
      </div>
      <div className="mt-10 grid gap-6 lg:grid-cols-[1fr_320px]">
        <article className="space-y-6">
          <section className="rounded-2xl border border-line bg-surface p-5 sm:p-7">
            <h2 className="text-xl font-bold">Objective</h2>
            <p className="mt-3 leading-7 text-slate-400">By the end, a local Django project will serve a named route at / and render a template through a view.</p>
            <h3 className="mt-6 font-semibold">Prerequisites</h3>
            <p className="mt-2 text-sm text-slate-400">Python 3, a terminal, a text editor, and the Module 1 lessons about project and app setup.</p>
          </section>
          <section className="rounded-2xl border border-line bg-surface p-5 sm:p-7">
            <div className="flex items-center gap-3"><Terminal className="text-emerald-300" size={20} /><h2 className="text-xl font-bold">Commands</h2></div>
            <pre className="mt-4 overflow-x-auto rounded-xl bg-[#0a1220] p-4 text-sm leading-7 text-emerald-100"><code>{`mkdir django-lab\ncd django-lab\npython3 -m venv .venv\nsource .venv/bin/activate\npip install \"Django>=5.0,<6.0\"\ndjango-admin startproject config .\npython manage.py startapp learning\npython manage.py check\npython manage.py runserver`}</code></pre>
          </section>
          <section className="rounded-2xl border border-line bg-surface p-5 sm:p-7">
            <h2 className="text-xl font-bold">Files to edit</h2>
            <div className="mt-4 space-y-3">{files.map(([file, action]) => <div key={file} className="flex gap-3 rounded-xl bg-ink/60 p-4"><Sparkles className="mt-0.5 shrink-0 text-emerald-400" size={17} /><div><p className="font-mono text-sm text-slate-200">{file}</p><p className="mt-1 text-sm text-slate-400">{action}</p></div></div>)}</div>
          </section>
          <section className="rounded-2xl border border-line bg-surface p-5 sm:p-7">
            <h2 className="text-xl font-bold">Verification and expected result</h2>
            <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm leading-6 text-slate-400"><li>Run <code className="text-emerald-200">python manage.py check</code>; it should report no issues.</li><li>Open <code className="text-emerald-200">http://127.0.0.1:8000/</code>.</li><li>Confirm the page displays the Course Welcome heading.</li><li>Run the focused test and confirm the response status is 200.</li></ol>
            <div className="mt-5 flex gap-3 rounded-xl bg-amber-400/10 p-4 text-sm leading-6 text-amber-200"><X className="mt-0.5 shrink-0" size={17} /><p>This lab is read-only guidance. The platform never executes untrusted student code on the application server.</p></div>
          </section>
          <section className="rounded-2xl border border-line bg-surface p-5 sm:p-7"><h2 className="text-xl font-bold">Troubleshooting and cleanup</h2><p className="mt-3 text-sm leading-7 text-slate-400">If Django cannot be imported, activate .venv again. If the route returns 404, check the URL pattern and trailing slash. If the template is missing, verify the nested templates/learning path. Stop the local server with Ctrl+C and remove the lab folder only when you no longer need it.</p></section>
        </article>
        <aside className="h-fit rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-5 sm:p-6 lg:sticky lg:top-24"><p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">Lab outcome</p><h2 className="mt-3 text-2xl font-bold">Request → view → template</h2><p className="mt-3 text-sm leading-6 text-slate-300">This is the first complete vertical slice of the Django course. Continue with the eight Module 1 lessons to understand each boundary.</p><Link href="/courses/django/visualizer" className="mt-6 inline-flex rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500">Open MVT visualizer</Link></aside>
      </div>
    </section>
  );
}

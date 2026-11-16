"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import type { ProjectTemplate } from "@/lib/types";
import { projectApi } from "@/lib/project-api";
import { csrf } from "@/components/auth-form";
import { Badge, Card } from "@/components/ui";
import { ProjectLearningSystem } from "@/components/project-learning-system";

const sourceCode = `#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_STUDENTS 100
#define DATA_FILE "data/students.dat"

typedef struct {
    int id;
    char name[80];
    int age;
    char grade;
    char email[120];
} Student;

static Student students[MAX_STUDENTS];
static size_t student_count = 0;

static void trim_newline(char *text) {
    text[strcspn(text, "\\n")] = '\\0';
}

static int read_int(const char *prompt, int min, int max) {
    char buffer[64];
    int value;
    for (;;) {
        printf("%s", prompt);
        if (!fgets(buffer, sizeof buffer, stdin)) exit(EXIT_FAILURE);
        if (sscanf(buffer, "%d", &value) == 1 && value >= min && value <= max) return value;
        printf("Enter a number between %d and %d.\\n", min, max);
    }
}

static int find_student(int id) {
    for (size_t i = 0; i < student_count; i++) {
        if (students[i].id == id) return (int)i;
    }
    return -1;
}

static void save_students(void) {
    FILE *file = fopen(DATA_FILE, "wb");
    if (!file) { perror("Could not save records"); return; }
    fwrite(&student_count, sizeof student_count, 1, file);
    fwrite(students, sizeof(Student), student_count, file);
    fclose(file);
}

static void add_student(void) {
    if (student_count == MAX_STUDENTS) { puts("Capacity limit reached."); return; }
    int id = read_int("Student ID: ", 1, 999999);
    if (find_student(id) >= 0) { puts("That ID already exists."); return; }
    Student *student = &students[student_count++];
    student->id = id;
    printf("Full name: "); fgets(student->name, sizeof student->name, stdin); trim_newline(student->name);
    student->age = read_int("Age: ", 5, 120);
    printf("Grade (A-F): "); fgets(&student->grade, 2, stdin); getchar();
    printf("Email: "); fgets(student->email, sizeof student->email, stdin); trim_newline(student->email);
    save_students();
    puts("Student added and saved.");
}

static void list_students(void) {
    if (student_count == 0) { puts("No student records yet."); return; }
    for (size_t i = 0; i < student_count; i++) {
        printf("%d | %-24s | age %d | %c | %s\\n", students[i].id, students[i].name,
               students[i].age, students[i].grade, students[i].email);
    }
}

int main(void) {
    puts("Student Record Management System");
    for (;;) {
        puts("\\n1. Add  2. View  3. Search  4. Update  5. Delete  6. Exit");
        switch (read_int("Choose an option: ", 1, 6)) {
            case 1: add_student(); break;
            case 2: list_students(); break;
            case 6: save_students(); puts("Records saved. Goodbye."); return 0;
            default: puts("Continue with the guided milestone for this operation."); break;
        }
    }
}`;

const testCases = [
  ["Add valid student", "ID 1001, age 20, grade A", "Record is added and persisted"],
  ["Reject duplicate ID", "ID 1001 when it already exists", "No new record; clear validation message"],
  ["Reject invalid age", "Age 2 or 121", "Input is rejected and the prompt repeats"],
  ["Search missing student", "Search ID 9999", "Not-found result without a crash"],
  ["Reload records", "Restart after saving", "Previously saved records are restored"],
  ["Corrupted data", "Truncated data file", "Safe error path; no silent overwrite"],
];

const rubric: [string, number][] = [
  ["Student data structure", 10], ["Add and view records", 15], ["Search, update and delete", 20],
  ["Sorting and statistics", 10], ["File persistence", 15], ["Input validation", 10],
  ["Error handling", 10], ["Code quality and tests", 10],
];

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return <section id={id} className="scroll-mt-24"><Card className="p-5 sm:p-7"><h2 className="text-xl font-bold tracking-tight">{title}</h2><div className="mt-4">{children}</div></Card></section>;
}

export function ProjectDetail({ project }: { project: ProjectTemplate }) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const isStudentRecord = project.slug === "c-student-record-program";
  const totalRubric = useMemo(() => rubric.reduce((sum, [, weight]) => sum + weight, 0), []);

  const start = async () => {
    setBusy(true);
    try {
      const result = await projectApi.start(project.slug, csrf());
      setMessage("Project started. Your workspace is ready.");
      window.location.assign(`/my-projects/${result.id}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to start project");
    } finally { setBusy(false); }
  };

  const bookmark = async () => {
    try {
      const result = await projectApi.bookmark(project.id, csrf());
      setMessage(result.bookmarked ? "Saved to your projects." : "Removed from saved projects.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to update saved projects"); }
  };

  const downloadSource = () => {
    const url = URL.createObjectURL(new Blob([sourceCode], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "main.c"; anchor.click(); URL.revokeObjectURL(url);
  };

  if (!isStudentRecord) return <ProjectLearningSystem project={project} onStart={start} onBookmark={bookmark} busy={busy} message={message} />;

  return <div className="space-y-7">
    <div className="flex flex-wrap items-center gap-2 text-sm text-slate-400"><Link href="/projects" className="hover:text-white">Projects</Link><span>/</span><span className="text-slate-200">C Student Record Program</span></div>
    <div className="grid gap-7 xl:grid-cols-[minmax(0,1fr)_260px]">
      <main className="min-w-0 space-y-7">
        <div className="rounded-2xl border border-indigo-400/20 bg-gradient-to-br from-indigo-600/30 via-blue-900/20 to-slate-900 p-6 sm:p-9"><div className="flex flex-wrap items-center gap-2"><Badge>Intermediate</Badge><span className="rounded-full bg-white/10 px-3 py-1 text-xs text-indigo-100">C · 4–6 hours</span><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">Free project</span></div><h1 className="mt-5 max-w-4xl text-3xl font-extrabold tracking-tight sm:text-5xl">C Student Record Management System</h1><p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">Build a safe command-line student record manager in standard C11. You will model records, implement CRUD operations, validate user input, persist data, and prepare the program for testing.</p><div className="mt-7 flex flex-wrap gap-3"><button disabled={busy} onClick={start} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-wait disabled:opacity-60">{busy ? "Starting…" : "Start project"}</button><button onClick={bookmark} className="rounded-xl border border-white/15 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:border-indigo-300/60 hover:bg-white/5">Save project</button></div>{message && <p className="mt-4 text-sm text-emerald-300" role="status">{message}</p>}</div>

        <Section id="overview" title="Project overview"><div className="grid gap-5 sm:grid-cols-2"><div><p className="text-sm leading-7 text-slate-300">This project simulates a small school administration tool. It is intentionally terminal-based so the data model, validation boundaries, file format, and error paths remain visible and testable.</p><p className="mt-4 text-sm leading-7 text-slate-400">Expected result: an application that can add, view, search, update, delete, sort, summarize, and persist student records without unsafe unbounded input.</p></div><dl className="grid grid-cols-2 gap-4 text-sm"><div className="rounded-xl bg-ink/70 p-4"><dt className="text-slate-500">Language</dt><dd className="mt-1 font-semibold text-white">C11</dd></div><div className="rounded-xl bg-ink/70 p-4"><dt className="text-slate-500">Duration</dt><dd className="mt-1 font-semibold text-white">4–6 hours</dd></div><div className="rounded-xl bg-ink/70 p-4"><dt className="text-slate-500">Level</dt><dd className="mt-1 font-semibold text-white">Beginner → Intermediate</dd></div><div className="rounded-xl bg-ink/70 p-4"><dt className="text-slate-500">Evaluation</dt><dd className="mt-1 font-semibold text-white">100 points</dd></div></dl></div></Section>

        <Section id="objectives" title="Learning objectives"><div className="grid gap-3 sm:grid-cols-2">{["Design a Student struct and bounded record store", "Use arrays, pointers, functions, and strings safely", "Implement CRUD, searching, sorting, and statistics", "Persist records and handle missing or corrupt data", "Validate IDs, age, grade, email, and menu input", "Separate UI, data operations, storage, and tests"].map(item => <div key={item} className="rounded-xl bg-ink/60 p-4 text-sm text-slate-300"><span className="mr-2 text-emerald-400">✓</span>{item}</div>)}</div></Section>

        <Section id="requirements" title="Functional requirements"><ul className="grid gap-3 text-sm leading-7 text-slate-300 sm:grid-cols-2">{["Add student with a unique ID, full name, age, grade, and email", "View all records with an empty-state message", "Search by student ID", "Update and delete an existing record", "Sort records and show basic statistics", "Persist data with an explicit documented format", "Reject invalid input and capacity overflow", "Exit only after attempting a safe save"].map(item => <li key={item} className="rounded-xl border border-line bg-ink/40 px-4 py-3">{item}</li>)}</ul></Section>

        <Section id="structure" title="Recommended project structure"><pre className="overflow-x-auto rounded-xl bg-[#080d1b] p-5 text-sm leading-7 text-indigo-100"><code>{`student-record-system/\n├── src/\n│   ├── main.c\n│   ├── student.c\n│   └── storage.c\n├── include/\n│   ├── student.h\n│   └── storage.h\n├── data/\n├── tests/\n│   └── test_student.c\n├── README.md\n└── Makefile`}</code></pre><p className="mt-4 text-sm leading-7 text-slate-400">Keep <code>data/</code> out of version control when it contains local records. A production implementation should validate its file header and record count, write to a temporary file, then replace the original only after a successful write.</p></Section>

        <Section id="implementation" title="Implementation guide"><div className="space-y-3">{["Project setup — create the folders, Makefile, and a C11 compiler check.", "Define Student — add bounded fields and constants for capacity.", "Build the menu — read a complete line with fgets and validate the option.", "Implement Add — reject duplicate IDs, invalid boundaries, and full capacity.", "Implement View and Search — keep display and lookup functions small and testable.", "Implement Update and Delete — find by ID, confirm the operation, and preserve array invariants.", "Add Sorting and Statistics — sort a copy when the original order matters.", "Add File Persistence — validate reads, handle failures, and avoid silent data loss.", "Compile and Test — run warnings as errors where practical and exercise error paths."].map((step, index) => <div key={step} className="flex gap-4 rounded-xl bg-ink/50 p-4"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/20 text-sm font-bold text-indigo-200">{index + 1}</span><p className="text-sm leading-7 text-slate-300">{step}</p></div>)}</div></Section>

        <Section id="source" title="Safe C11 starter implementation"><div className="flex flex-wrap items-center justify-between gap-3"><p className="text-sm text-slate-400">The starter demonstrates bounded input, duplicate-ID checks, capacity handling, and binary persistence. Extend the guided milestones for update, delete, sorting, statistics, and corruption checks.</p><button onClick={downloadSource} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400">Download main.c</button></div><div className="mt-5 overflow-hidden rounded-xl border border-line bg-[#080d1b]"><div className="border-b border-line px-4 py-3 text-xs text-slate-500">src/main.c · C11</div><pre className="max-h-[620px] overflow-auto p-5 text-sm leading-7 text-indigo-100"><code>{sourceCode}</code></pre></div><p className="mt-4 text-xs leading-6 text-amber-200/80">Run this code locally in an isolated practice directory. The Academy displays source code and does not execute arbitrary student code on the production host.</p></Section>

        <Section id="terminal" title="Terminal preview"><pre className="overflow-x-auto rounded-xl bg-[#080d1b] p-5 text-sm leading-7 text-emerald-200"><code>{`Student Record Management System\n\n1. Add  2. View  3. Search  4. Update  5. Delete  6. Exit\nChoose an option: 1\nStudent ID: 1001\nFull name: Aye Chan\nAge: 20\nGrade (A-F): A\nEmail: aye@example.com\nStudent added and saved.\n\nChoose an option: 3\nSearch ID: 1001\nFound: Aye Chan (A)`}</code></pre></Section>

        <Section id="tests" title="Test cases"><div className="overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm"><thead className="text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-3 py-3">Test</th><th className="px-3 py-3">Input</th><th className="px-3 py-3">Expected result</th></tr></thead><tbody>{testCases.map(([name, input, expected]) => <tr key={name} className="border-t border-line"><td className="px-3 py-4 font-medium text-slate-200">{name}</td><td className="px-3 py-4 text-slate-400">{input}</td><td className="px-3 py-4 text-slate-300">{expected}</td></tr>)}</tbody></table></div><p className="mt-4 text-xs text-slate-500">Pass/fail results are intentionally not fabricated; run the test suite in your local C11 environment and record the actual result.</p></Section>

        <Section id="exercises" title="Exercises and challenges"><div className="grid gap-4 md:grid-cols-3">{[["Beginner", "Add a student, display all records, and search by ID."], ["Intermediate", "Implement update, delete, sorting, and safe file persistence."], ["Advanced", "Add CSV import/export, pagination, dynamic storage, and stronger corruption checks."]].map(([level, text]) => <div key={level} className="rounded-xl bg-ink/60 p-4"><p className="text-xs font-semibold uppercase tracking-wider text-indigo-300">{level}</p><p className="mt-3 text-sm leading-6 text-slate-300">{text}</p></div>)}</div></Section>

        <Section id="rubric" title={`Grading rubric · ${totalRubric}/100`}><div className="grid gap-3 sm:grid-cols-2">{rubric.map(([name, weight]) => <div key={name} className="flex items-center justify-between rounded-xl bg-ink/60 px-4 py-3 text-sm"><span className="text-slate-300">{name}</span><span className="font-semibold text-indigo-200">{weight} pts</span></div>)}</div><p className="mt-4 text-xs leading-6 text-slate-500">Grades are assigned only from an actual submission review. Hidden solutions and tests are not exposed in this page.</p></Section>

        <Section id="related" title="Related learning"><div className="flex flex-wrap gap-3">{project.milestones.map(step => <Link key={step.id} href={`/projects/${project.slug}/learn/${step.slug || `step-${step.position}`}`} className="rounded-lg border border-line px-4 py-2 text-sm text-indigo-200 hover:border-indigo-400/60">{step.title}</Link>)}</div></Section>
      </main>
      <aside className="h-fit space-y-4 xl:sticky xl:top-24"><Card className="p-4"><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">On this page</p><nav className="mt-3 space-y-1 text-sm">{[["overview", "Overview"], ["objectives", "Objectives"], ["requirements", "Requirements"], ["implementation", "Implementation"], ["source", "Source code"], ["tests", "Test cases"], ["rubric", "Rubric"]].map(([id, label]) => <a key={id} href={`#${id}`} className="block rounded-lg px-3 py-2 text-slate-400 hover:bg-indigo-500/10 hover:text-indigo-200">{label}</a>)}</nav></Card><Card className="border-indigo-400/20 bg-indigo-500/10 p-5"><p className="text-xs font-semibold uppercase tracking-wider text-indigo-200">Project workflow</p><p className="mt-3 text-sm leading-6 text-slate-300">Start the project to create your authenticated workspace, save milestone progress, and submit your repository for review.</p><button onClick={start} disabled={busy} className="mt-5 w-full rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-60">{busy ? "Starting…" : "Open workspace"}</button></Card></aside>
    </div>
  </div>;
}

function GenericProject({ project, start, bookmark, message }: { project: ProjectTemplate; start: () => void; bookmark: () => void; message: string }) {
  return <div><div className="flex flex-wrap justify-between gap-6"><div className="max-w-4xl">{project.category && <p className="text-sm text-indigo-300">{project.category.name}</p>}<div className="mt-3 flex gap-2"><Badge>{project.difficulty}</Badge>{project.estimated_hours > 0 && <Badge>{project.estimated_hours}h estimate</Badge>}</div><h1 className="mt-4 text-4xl font-bold md:text-5xl">{project.title}</h1><p className="mt-4 text-lg leading-8 text-slate-400">{project.description_en}</p></div><div className="flex shrink-0 flex-col gap-3"><button className="rounded-xl bg-indigo-500 px-5 py-3 font-semibold" onClick={start}>Start project</button><button className="rounded-xl border border-line px-5 py-3 text-sm" onClick={bookmark}>Save project</button></div></div><div className="mt-10 grid gap-5 lg:grid-cols-2"><Card className="p-6"><h2 className="text-xl font-bold">Learning outcomes</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-400">{project.learning_outcomes}</p><h2 className="mt-8 text-xl font-bold">Requirements</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-400">{project.requirements || "No additional requirements were published."}</p></Card><Card className="p-6"><h2 className="text-xl font-bold">Architecture and structure</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-400">{project.architecture_overview || "Architecture notes are not available yet."}</p><pre className="mt-5 overflow-auto rounded-xl bg-ink p-4 text-sm text-slate-300">{project.folder_structure || "Folder structure not published."}</pre></Card></div><div className="mt-10 grid gap-5 lg:grid-cols-2"><Card className="p-6"><h2 className="text-xl font-bold">Testing guide</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-400">{project.testing_guide || "Testing guidance is not available yet."}</p></Card><Card className="p-6"><h2 className="text-xl font-bold">Deployment guide</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-400">{project.deployment_guide || "Deployment guidance is not available yet."}</p></Card></div><h2 className="mt-12 text-2xl font-bold">Project learning steps</h2><div className="mt-5 space-y-4">{project.milestones.map((milestone, index) => <Link href={`/projects/${project.slug}/learn/${milestone.slug || `step-${milestone.position}`}`} key={milestone.id}><Card className="p-5 transition hover:border-indigo-400/50"><p className="text-xs uppercase tracking-wider text-indigo-300">Step {index + 1}</p><h3 className="mt-2 text-lg font-semibold">{milestone.title}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{milestone.description_en}</p><span className="mt-3 inline-block text-sm text-indigo-300">Read this step →</span></Card></Link>)}</div>{message && <p className="mt-5 text-sm text-green-300" role="status">{message}</p>}</div>;
}

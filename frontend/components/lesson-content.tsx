"use client";

import { useEffect, useState, type ReactNode } from "react";

export type ContentBlock =
  | { kind: "heading"; text: string; level: 2 | 3; section: string }
  | { kind: "paragraph"; text: string; section: string }
  | { kind: "list"; ordered: boolean; items: string[]; section: string }
  | { kind: "code"; language: string; code: string; section: string }
  | { kind: "note"; label: string; text: string; section: string };

const SECTION_HEADINGS = new Set([
  "Introduction",
  "Learning objectives",
  "Prerequisites",
  "Detailed theory",
  "Detailed theory and real-world example",
  "Detailed theory and syntax",
  "Visual explanation",
  "Diagram",
  "Key definitions",
  "Technical definitions",
  "Syntax example",
  "Syntax and theory",
  "Complete example",
  "Step-by-step setup",
  "Portable VS Code workspace examples",
  "Troubleshooting",
  "Expected output",
  "Line-by-line explanation",
  "Additional complete example",
  "Explanation",
  "Common mistakes",
  "Practice exercises",
  "Exercises",
  "Myanmar explanation",
  "Summary",
  "Next lesson",
]);

function headingFor(line: string): string | null {
  if (SECTION_HEADINGS.has(line)) return line;
  if (line.startsWith("Complete C program — ")) return line;
  return null;
}

function noteFor(line: string): { label: string; text: string } | null {
  if (line === "Solution:") return { label: "Solution", text: "" };
  if (line.startsWith("Why it works:")) return { label: "Why it works", text: line.slice("Why it works:".length).trim() };
  return null;
}

/** Split authored lesson markdown into renderable blocks. */
export function parseLessonContent(content: string): ContentBlock[] {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: ContentBlock[] = [];
  let section = "";
  let paragraph: string[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;

  const flushParagraph = () => {
    if (!paragraph.length) return;
    blocks.push({ kind: "paragraph", text: paragraph.join("\n").trimEnd(), section });
    paragraph = [];
  };
  const flushList = () => {
    if (!list) return;
    blocks.push({ kind: "list", ordered: list.ordered, items: list.items, section });
    list = null;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const rawLine = lines[index];
    const line = rawLine.trim();

    if (line.startsWith("```")) {
      flushParagraph();
      flushList();
      const language = line.slice(3).trim().split(/\s+/)[0] || "text";
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index += 1;
      }
      blocks.push({ kind: "code", language, code: codeLines.join("\n"), section });
      continue;
    }

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = headingFor(line);
    if (heading) {
      flushParagraph();
      flushList();
      section = heading;
      blocks.push({ kind: "heading", text: heading, level: 2, section });
      continue;
    }

    const note = noteFor(line);
    if (note) {
      flushParagraph();
      flushList();
      blocks.push({ kind: "note", label: note.label, text: note.text, section });
      continue;
    }

    if (/^-\s+/.test(line)) {
      flushParagraph();
      if (!list || list.ordered) {
        flushList();
        list = { ordered: false, items: [] };
      }
      list.items.push(line.replace(/^-\s+/, ""));
      continue;
    }

    if (/^\d+\.\s+/.test(line)) {
      flushParagraph();
      if (!list || !list.ordered) {
        flushList();
        list = { ordered: true, items: [] };
      }
      list.items.push(line.replace(/^\d+\.\s+/, ""));
      continue;
    }

    flushList();
    paragraph.push(rawLine.trimEnd());
  }

  flushParagraph();
  flushList();

  // A paragraph directly before a code fence inside "Additional complete example"
  // is the example title, so promote it to a subheading.
  return blocks.map((block, index) => {
    if (
      block.kind === "paragraph" &&
      block.section === "Additional complete example" &&
      blocks[index + 1]?.kind === "code"
    ) {
      return { kind: "heading", text: block.text, level: 3, section: block.section } as ContentBlock;
    }
    return block;
  });
}

const C_KEYWORDS = new Set([
  "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else",
  "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register",
  "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
  "union", "unsigned", "void", "volatile", "while", "_Bool", "_Complex", "_Imaginary",
  "bool", "class", "concept", "constexpr", "catch", "delete", "explicit", "final", "namespace",
  "new", "noexcept", "nullptr", "operator", "override", "private", "protected", "public", "template",
  "this", "throw", "try", "typename", "using", "virtual", "friend", "mutable", "static_assert",
  "string", "vector", "array", "map", "set", "pair", "tuple", "cin", "cout", "cerr", "endl",
]);

const C_TOKEN_PATTERN = /(\/\*[\s\S]*?\*\/|\/\/[^\n]*|#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)\b|\b[A-Za-z_]\w*\b|[^\sA-Za-z0-9_]+|\s+)/g;

/** Small dependency-free C highlighter for lesson theory snippets. */
export function highlightC(code: string): ReactNode[] {
  const tokens = code.match(C_TOKEN_PATTERN) ?? [code];
  return tokens.map((token, index) => {
    let className = "";
    if (token.startsWith("/*") || token.startsWith("//")) className = "text-slate-500 italic";
    else if (token.startsWith("#")) className = "text-fuchsia-300";
    else if (token.startsWith('"')) className = "text-emerald-300";
    else if (token.startsWith("'")) className = "text-amber-300";
    else if (/^\d/.test(token)) className = "text-orange-300";
    else if (/^[A-Za-z_]\w*$/.test(token)) {
      if (C_KEYWORDS.has(token)) className = "text-sky-300";
      else {
        const next = tokens.slice(index + 1).find(part => part.trim());
        if (next?.startsWith("(")) className = "text-indigo-300";
      }
    }
    return className ? <span className={className} key={`${index}-${token.slice(0, 8)}`}>{token}</span> : token;
  });
}

async function copyText(text: string) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  document.execCommand("copy");
  document.body.removeChild(area);
}

function InlineText({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return <>{parts.map((part, index) => part.length > 2 && part.startsWith("`") && part.endsWith("`")
    ? <code className="rounded bg-elevated px-1.5 py-0.5 font-mono text-[0.9em] text-indigo-200" key={index}>{part.slice(1, -1)}</code>
    : part)}</>;
}

function CodeBlock({ language, code, output, label: explicitLabel }: { language: string; code: string; output: boolean; label?: string }) {
  const [copied, setCopied] = useState(false);
  useEffect(() => {
    if (!copied) return;
    const timer = window.setTimeout(() => setCopied(false), 1600);
    return () => window.clearTimeout(timer);
  }, [copied]);
  const label = explicitLabel ?? (output ? "Expected output" : language.toLowerCase() === "c" ? "C" : language.toUpperCase());
  return (
    <div className="mt-4 overflow-hidden rounded-2xl border border-line bg-[#0d1528]">
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-2.5 text-xs">
        <span className="truncate font-mono text-slate-400">{label}</span>
        <button
          type="button"
          onClick={() => { copyText(code).then(() => setCopied(true)).catch(() => setCopied(false)); }}
          className="shrink-0 rounded-md px-2 py-1 font-medium text-indigo-300 transition hover:bg-indigo-500/10 hover:text-white"
          aria-label={copied ? "Code copied" : "Copy code"}
        >
          {copied ? "Copied" : "Copy code"}
        </button>
      </div>
      <pre className={`overflow-x-auto p-5 text-sm leading-7 ${output ? "text-emerald-200" : "text-slate-200"}`}>
        <code className="font-mono">{output ? code : highlightC(code)}</code>
      </pre>
    </div>
  );
}

export function CodeSample({ code, language = "c", output = false, label }: { code: string; language?: string; output?: boolean; label?: string }) {
  return <CodeBlock code={code} language={language} output={output} label={label} />;
}


export function LessonContent({ content, className = "" }: { content: string; className?: string }) {
  // Myanmar is rendered by the explicit Show MM control in LessonReader.
  // Older seeded lessons also contain a legacy inline translation section;
  // hide that duplicate so the toggle remains authoritative for all 75 lessons.
  const blocks = parseLessonContent(content).filter(block => block.section !== "Myanmar explanation");
  return (
    <div className={`lesson-content max-w-none text-slate-300 ${className}`}>
      {blocks.map((block, index) => {
        if (block.kind === "heading") {
          const id = block.text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
          return block.level === 3 ? (
            <h3 className="mt-7 text-lg font-semibold text-indigo-200" key={index} id={id}>{block.text}</h3>
          ) : (
            <h2 className="mt-10 border-b border-line pb-2 text-2xl font-bold text-white first:mt-0" key={index} id={id}>{block.text}</h2>
          );
        }
        if (block.kind === "code") {
          return <CodeBlock key={index} language={block.language} code={block.code} output={block.language.toLowerCase() === "text"} />;
        }
        if (block.kind === "note") {
          return (
            <div className="mt-3 rounded-lg border-l-2 border-indigo-400/60 bg-indigo-500/5 px-4 py-3 text-sm leading-7" key={index}>
              <span className="font-semibold text-indigo-200">{block.label}{block.text ? ":" : ""}</span>
              {block.text && <span className="ml-1 whitespace-pre-line text-slate-300"><InlineText text={block.text} /></span>}
            </div>
          );
        }
        if (block.kind === "list") {
          const List = block.ordered ? "ol" : "ul";
          return (
            <List className={`mt-4 space-y-2 pl-6 ${block.ordered ? "list-decimal" : "list-disc"}`} key={index}>
              {block.items.map((item, itemIndex) => (
                <li className="whitespace-pre-line leading-7" key={itemIndex}><InlineText text={item} /></li>
              ))}
            </List>
          );
        }
        if (block.section === "Visual explanation") {
          return (
            <pre className="mt-4 overflow-x-auto rounded-2xl border border-line bg-surface/70 p-5 font-mono text-xs leading-6 text-slate-300 sm:text-sm" key={index}>
              {block.text}
            </pre>
          );
        }
        return <p className="mt-4 whitespace-pre-line leading-8" key={index}><InlineText text={block.text} /></p>;
      })}
    </div>
  );
}

import type { Config } from "tailwindcss";

const config: Config = { darkMode: "class", content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"], theme: { extend: { colors: { ink: "#0B1020", surface: "#111827", elevated: "#172033", line: "#1E293B", primary: "#6366F1", success: "#22C55E", warning: "#F59E0B" }, fontFamily: { sans: ["Inter", "Noto Sans Myanmar", "sans-serif"], mono: ["JetBrains Mono", "monospace"] }, boxShadow: { glow: "0 0 40px rgba(99,102,241,.18)" } } }, plugins: [] };
export default config;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Keep the development webpack cache separate from production builds. A
  // concurrent `next build` must not overwrite a running dev server's chunks.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
  // The frontend is the intended Next.js workspace. This avoids accidentally
  // selecting an unrelated lockfile from /Users/kimpu as the tracing root.
  outputFileTracingRoot: process.cwd(),
  async rewrites() {
    const backendUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};
export default nextConfig;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The frontend is the intended Next.js workspace. This avoids accidentally
  // selecting an unrelated lockfile from /Users/kimpu as the tracing root.
  outputFileTracingRoot: process.cwd(),
  async rewrites() {
    const backendUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};
export default nextConfig;

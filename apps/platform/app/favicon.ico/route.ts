import { readFile } from "node:fs/promises";
import path from "node:path";

export async function GET() {
  const logo = await readFile(path.join(process.cwd(), "public", "branding", "tkp.png"));
  return new Response(logo, {
    headers: {
      "Cache-Control": "public, max-age=86400",
      "Content-Type": "image/png",
    },
  });
}

"use client";
import { useEffect, useState } from "react";
import { AboutPage } from "@/components/about-page";
export default function AboutRoute() {
  const [page, setPage] = useState<any>({ title: "About Learn-Coding", body: "" });
  useEffect(() => { fetch("/api/v1/site/pages/about", { cache: "no-store" }).then(response => response.ok ? response.json() : null).then(value => { if (value) setPage(value); }).catch(() => undefined); }, []);
  return <AboutPage page={page} />;
}

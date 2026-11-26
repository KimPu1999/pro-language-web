import { redirect } from "next/navigation";

export default async function Page({params}:{params:Promise<{slug:string}>}){
  redirect(`/careers/paths/${encodeURIComponent((await params).slug)}`);
}

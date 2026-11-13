"use client";
import { useEffect, useState } from "react";
import { automationApi } from "@/lib/api";
import { Card, Skeleton } from "@/components/ui";
export default function Page(){const [data,setData]=useState<any>();const [error,setError]=useState("");useEffect(()=>{automationApi.platform().then(setData).catch(e=>setError(e.message));},[]);if(error)return <Card><p className="text-rose-300">{error}</p></Card>;if(!data)return <Skeleton/>;return <Card><p className="text-sm text-slate-400">Platform automation oversight</p><h1 className="mt-2 text-3xl font-semibold">Automation health</h1><div className="mt-5 grid gap-3 sm:grid-cols-3">{Object.entries(data.metrics).map(([k,v])=><div className="rounded-lg bg-slate-900 p-4" key={k}><p className="text-sm text-slate-400">{k.replaceAll("_"," ")}</p><p className="mt-1 text-2xl">{String(v)}</p></div>)}</div><p className="mt-5 text-sm text-amber-200">AI provider: {data.ai_status}</p></Card>}

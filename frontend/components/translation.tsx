"use client";
import { useEffect, useState } from "react";
import { Button } from "./ui";
import { LessonContent } from "./lesson-content";
export function LessonTranslationToggle({ onChange }: { onChange: (show: boolean) => void }) { const [show,setShow]=useState(false); useEffect(()=>{ const value=window.localStorage.getItem("showMyanmar")==="true"; setShow(value); onChange(value); },[onChange]); function toggle(){const next=!show; setShow(next); window.localStorage.setItem("showMyanmar",String(next)); onChange(next);} return <Button onClick={toggle} className="bg-elevated text-slate-200 hover:bg-line">{show?"Hide MM":"Show MM"}</Button>; }
export function BilingualLessonContent({ english, myanmar }: { english: string; myanmar?: string|null }) { const [show,setShow]=useState(false); return <div><div className="mb-6 flex justify-end"><LessonTranslationToggle onChange={setShow}/></div><LessonContent content={english}/>{show&&<div className="mt-6 rounded-xl border border-indigo-400/20 bg-indigo-500/5 p-5">{myanmar?<LessonContent content={myanmar}/>:<p className="leading-8 text-slate-300">Myanmar explanation is not available for this lesson yet.</p>}</div>}</div>; }

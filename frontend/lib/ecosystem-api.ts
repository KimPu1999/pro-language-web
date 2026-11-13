const base=process.env.NEXT_PUBLIC_API_BASE_URL??"";
async function request<T>(path:string,init?:RequestInit):Promise<T>{const r=await fetch(`${base}${path}`,{...init,credentials:"include",headers:{Accept:"application/json",...init?.headers}});if(!r.ok){let message=`API request failed (${r.status})`;try{const body=await r.json();message=body.detail??message}catch{}throw new Error(message)}return r.json() as Promise<T>}
export type GithubStatus={enabled:boolean;connected:boolean;login:string|null;message:string;provider:string};
export const ecosystemApi={
  hub:()=>request<any>("/api/v1/developers"), status:()=>request<GithubStatus>("/api/v1/github/status"),
  projects:()=>request<any[]>("/api/v1/open-source/projects"), opportunities:()=>request<any[]>("/api/v1/open-source/opportunities"),
  contributions:()=>request<any>("/api/v1/developers/contributions"), reviews:()=>request<any[]>("/api/v1/developers/reviews"),
  profile:(username:string)=>request<any>(`/api/v1/developers/${encodeURIComponent(username)}`),
};

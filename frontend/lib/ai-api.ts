const base=process.env.NEXT_PUBLIC_API_BASE_URL??"";
async function request<T>(path:string,init?:RequestInit){
  const r=await fetch(`${base}${path}`,{...init,credentials:"include",headers:{Accept:"application/json","Content-Type":"application/json",...init?.headers}});
  if(!r.ok){let message=`API request failed (${r.status})`;try{const body=await r.json() as {detail?:string};message=body.detail??message}catch{}throw new Error(message)}
  return r.json() as Promise<T>
}
export const aiApi={
  conversations:(search="")=>request<{items:any[]}>(`/api/v1/ai/conversations${search?`?search=${encodeURIComponent(search)}`:""}`),
  conversation:(id:string)=>request<any>(`/api/v1/ai/conversations/${id}`),
  create:(title:string,csrf:string)=>request<any>('/api/v1/ai/conversations',{method:'POST',body:JSON.stringify({title}),headers:{'X-CSRF-Token':csrf}}),
  rename:(id:string,title:string,csrf:string)=>request<any>(`/api/v1/ai/conversations/${id}`,{method:'PATCH',body:JSON.stringify({title}),headers:{'X-CSRF-Token':csrf}}),
  remove:(id:string,csrf:string)=>request<any>(`/api/v1/ai/conversations/${id}`,{method:'DELETE',headers:{'X-CSRF-Token':csrf}}),
  stop:(id:string,csrf:string)=>request<any>(`/api/v1/ai/conversations/${id}/stop`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),
  preferences:()=>request<any>('/api/v1/ai/preferences'),
  savePreferences:(body:any,csrf:string)=>request<any>('/api/v1/ai/preferences',{method:'PUT',body:JSON.stringify(body),headers:{'X-CSRF-Token':csrf}}),
  usage:()=>request<any>('/api/v1/ai/usage'),
  adminSettings:()=>request<any>('/api/v1/ai/admin/settings'),
  adminUsage:()=>request<any>('/api/v1/ai/admin/usage'),
  adminRetrieval:()=>request<any>('/api/v1/ai/admin/retrieval'),
  adminPrompts:()=>request<any>('/api/v1/ai/admin/prompts'),
  createPrompt:(body:any,csrf:string)=>request<any>('/api/v1/ai/admin/prompts',{method:'POST',body:JSON.stringify(body),headers:{'X-CSRF-Token':csrf}}),
  promptAction:(id:string,action:string,csrf:string)=>request<any>(`/api/v1/ai/admin/prompts/${id}/action`,{method:'POST',body:JSON.stringify({action}),headers:{'X-CSRF-Token':csrf}}),
};
export function streamUrl(id:string){return `${base}/api/v1/ai/conversations/${id}/stream`}
export const gamificationApi={summary:()=>request<any>('/api/v1/gamification/summary'),achievements:()=>request<any>('/api/v1/gamification/achievements'),certificates:()=>request<any>('/api/v1/gamification/certificates'),leaderboard:(period='all_time')=>request<any>(`/api/v1/gamification/leaderboard?period=${period}`),preference:()=>request<any>('/api/v1/gamification/leaderboard/preferences'),savePreference:(body:any,csrf:string)=>request<any>('/api/v1/gamification/leaderboard/preferences',{method:'PUT',body:JSON.stringify(body),headers:{'X-CSRF-Token':csrf}})};
export const communityApi={
  feed:(search='',postType='')=>request<any>(`/api/v1/community/posts?search=${encodeURIComponent(search)}${postType?`&post_type=${postType}`:''}`),
  post:(body:any,csrf:string)=>request<any>('/api/v1/community/posts',{method:'POST',body:JSON.stringify(body),headers:{'X-CSRF-Token':csrf}}),
  postDetail:(slug:string)=>request<any>(`/api/v1/community/posts/${slug}`),
  updatePost:(id:string,body:any,csrf:string)=>request<any>(`/api/v1/community/posts/${id}`,{method:'PATCH',body:JSON.stringify(body),headers:{'X-CSRF-Token':csrf}}),
  deletePost:(id:string,csrf:string)=>request<void>(`/api/v1/community/posts/${id}`,{method:'DELETE',headers:{'X-CSRF-Token':csrf}}),
  answer:(id:string,body:string,csrf:string)=>request<any>(`/api/v1/community/posts/${id}/answers`,{method:'POST',body:JSON.stringify({body}),headers:{'X-CSRF-Token':csrf}}),
  editAnswer:(id:string,body:string,csrf:string)=>request<any>(`/api/v1/community/answers/${id}`,{method:'PATCH',body:JSON.stringify({body}),headers:{'X-CSRF-Token':csrf}}),
  accept:(postId:string,answerId:string,csrf:string)=>request<any>(`/api/v1/community/posts/${postId}/accept/${answerId}`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),
  comment:(id:string,body:string,csrf:string,parentId?:string)=>request<any>(`/api/v1/community/posts/${id}/comments`,{method:'POST',body:JSON.stringify({body,parent_id:parentId??null}),headers:{'X-CSRF-Token':csrf}}),
  vote:(id:string,csrf:string)=>request<any>(`/api/v1/community/posts/${id}/vote`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),
  bookmark:(id:string,csrf:string)=>request<any>(`/api/v1/community/posts/${id}/bookmark`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),
  snippets:()=>request<any[]>('/api/v1/community/snippets'),
  groups:()=>request<any[]>('/api/v1/community/groups'),
  group:(slug:string)=>request<any>(`/api/v1/community/groups/${slug}`),
  joinGroup:(id:string,csrf:string)=>request<any>(`/api/v1/community/groups/${id}/join`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),
  members:(search='')=>request<any>(`/api/v1/community/members?search=${encodeURIComponent(search)}`),
  notifications:()=>request<any[]>('/api/v1/community/notifications'),
  adminOverview:()=>request<any>('/api/v1/community/admin/overview'),
  reports:()=>request<any[]>('/api/v1/community/admin/reports'),
};
export const liveClassApi={catalog:(search='')=>request<any>(`/api/v1/live-classes?search=${encodeURIComponent(search)}`),detail:(id:string)=>request<any>(`/api/v1/live-classes/${id}`),register:(id:string,csrf:string)=>request<any>(`/api/v1/live-classes/${id}/register`,{method:'POST',headers:{'X-CSRF-Token':csrf}}),cancel:(id:string,csrf:string)=>request<any>(`/api/v1/live-classes/${id}/register`,{method:'DELETE',headers:{'X-CSRF-Token':csrf}}),roomToken:(id:string)=>request<any>(`/api/v1/live-classes/${id}/room-token`)};

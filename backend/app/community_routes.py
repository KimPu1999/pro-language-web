import re
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf
from .db import get_db
from .models import User, CommunityPost, CommunityAnswer, CommunityComment, CommunityVote, CommunityBookmark, CommunitySnippet, StudyGroup, StudyGroupMember, CommunityNotification, CommunityReport, UserBlock
from .admin_routes import full_admin
router=APIRouter(prefix="/api/v1/community",tags=["community"])
def clean(s:str)->str:return re.sub(r"<script[\s\S]*?</script>|javascript:","",s,flags=re.I).strip()
class PostIn(BaseModel): title:str=Field(min_length=3,max_length=220); body:str=Field(min_length=1,max_length=30000); post_type:str="discussion"
class AnswerIn(BaseModel): body:str=Field(min_length=1,max_length=30000)
class CommentIn(BaseModel): body:str=Field(min_length=1,max_length=10000); parent_id:UUID|None=None
class SnippetIn(BaseModel): title:str=Field(min_length=1,max_length=180); language:str=Field(min_length=1,max_length=50); source_code:str=Field(min_length=1,max_length=50000); description:str=Field(default="",max_length=10000)
class GroupIn(BaseModel): name:str=Field(min_length=2,max_length=160); description:str=Field(min_length=1,max_length=10000); visibility:str="public"
def post_out(x):return {"id":str(x.id),"slug":x.slug,"title":x.title,"body":x.body,"post_type":x.post_type,"author_id":str(x.author_id),"created_at":x.created_at}
@router.get("/feed")
def feed(search:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=50),db:Session=Depends(get_db)):
 q=select(CommunityPost).where(CommunityPost.status=="published",CommunityPost.visibility=="public");count=select(func.count()).select_from(CommunityPost).where(CommunityPost.status=="published",CommunityPost.visibility=="public")
 if search:q=q.where(CommunityPost.title.ilike(f"%{search}%"));count=count.where(CommunityPost.title.ilike(f"%{search}%"))
 total=db.scalar(count) or 0;return {"items":[post_out(x) for x in db.scalars(q.order_by(CommunityPost.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all()],"total":total,"page":page,"pages":(total+page_size-1)//page_size if total else 0}
@router.post("/posts",status_code=201)
def create_post(p:PostIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 slug=re.sub(r"[^a-z0-9]+","-",p.title.lower()).strip("-")+f"-{str(user.id)[:8]}";x=CommunityPost(author_id=user.id,title=clean(p.title),slug=slug,body=clean(p.body),post_type=p.post_type);db.add(x);db.commit();return post_out(x)
@router.get("/posts/{slug}")
def get_post(slug:str,db:Session=Depends(get_db)):
 x=db.scalar(select(CommunityPost).where(CommunityPost.slug==slug,CommunityPost.status=="published",CommunityPost.visibility=="public"));
 if not x:raise HTTPException(404,"Post not found")
 answers=db.scalars(select(CommunityAnswer).where(CommunityAnswer.post_id==x.id,CommunityAnswer.status=="published")).all();comments=db.scalars(select(CommunityComment).where(CommunityComment.post_id==x.id,CommunityComment.status=="published").order_by(CommunityComment.created_at)).all();return {**post_out(x),"answers":[{"id":str(a.id),"body":a.body,"author_id":str(a.author_id),"accepted":x.accepted_answer_id==a.id} for a in answers],"comments":[{"id":str(c.id),"body":c.body,"parent_id":str(c.parent_id) if c.parent_id else None} for c in comments]}
@router.post("/posts/{post_id}/answers",status_code=201)
def answer(post_id:UUID,p:AnswerIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 post=db.get(CommunityPost,post_id)
 if not post or post.status!="published":raise HTTPException(404,"Post not found")
 x=CommunityAnswer(post_id=post.id,author_id=user.id,body=clean(p.body));db.add(x);db.flush();
 if post.author_id!=user.id:db.add(CommunityNotification(user_id=post.author_id,notification_type="new_answer",target_id=post.id,preview="Your question received a new answer."))
 db.commit();return {"id":str(x.id),"body":x.body}
@router.post("/posts/{post_id}/accept/{answer_id}")
def accept(post_id:UUID,answer_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 post=db.get(CommunityPost,post_id);a=db.get(CommunityAnswer,answer_id)
 if not post or not a or post.author_id!=user.id or a.post_id!=post.id:raise HTTPException(403,"Only the question owner can accept an answer")
 post.accepted_answer_id=a.id;db.commit();return {"accepted_answer_id":str(a.id)}
@router.post("/posts/{post_id}/comments",status_code=201)
def comment(post_id:UUID,p:CommentIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 if not db.get(CommunityPost,post_id):raise HTTPException(404,"Post not found")
 if p.parent_id:
  parent=db.get(CommunityComment,p.parent_id)
  if not parent or parent.post_id!=post_id or parent.parent_id:raise HTTPException(422,"Comment nesting limit reached")
 x=CommunityComment(post_id=post_id,author_id=user.id,parent_id=p.parent_id,body=clean(p.body));db.add(x);db.commit();return {"id":str(x.id),"body":x.body}
@router.post("/posts/{post_id}/vote")
def vote(post_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 post=db.get(CommunityPost,post_id)
 if not post:raise HTTPException(404,"Post not found")
 if post.author_id==user.id:raise HTTPException(409,"Self-voting is not allowed")
 x=db.scalar(select(CommunityVote).where(CommunityVote.user_id==user.id,CommunityVote.target_type=="post",CommunityVote.target_id==post_id))
 if x:db.delete(x);state="removed"
 else:db.add(CommunityVote(user_id=user.id,target_type="post",target_id=post_id));state="added"
 db.commit();return {"status":state}
@router.post("/posts/{post_id}/bookmark")
def bookmark(post_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 x=db.scalar(select(CommunityBookmark).where(CommunityBookmark.user_id==user.id,CommunityBookmark.post_id==post_id));
 if x:db.delete(x);state="removed"
 else:db.add(CommunityBookmark(user_id=user.id,post_id=post_id));state="added"
 db.commit();return {"status":state}
@router.get("/snippets")
def snippets(db:Session=Depends(get_db)):return db.scalars(select(CommunitySnippet).where(CommunitySnippet.status=="published",CommunitySnippet.visibility=="public").order_by(CommunitySnippet.created_at.desc())).all()
@router.post("/snippets",status_code=201)
def create_snippet(p:SnippetIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 x=CommunitySnippet(author_id=user.id,title=clean(p.title),language=p.language,source_code=p.source_code,description=clean(p.description));db.add(x);db.commit();return {"id":str(x.id),"title":x.title}
@router.get("/groups")
def groups(db:Session=Depends(get_db)):return db.scalars(select(StudyGroup).where(StudyGroup.visibility=="public",StudyGroup.status=="active").order_by(StudyGroup.name)).all()
@router.post("/groups",status_code=201)
def create_group(p:GroupIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 slug=re.sub(r"[^a-z0-9]+","-",p.name.lower()).strip("-")+f"-{str(user.id)[:8]}";g=StudyGroup(owner_id=user.id,name=clean(p.name),slug=slug,description=clean(p.description),visibility=p.visibility if p.visibility in {"public","private"} else "public");db.add(g);db.flush();db.add(StudyGroupMember(group_id=g.id,user_id=user.id,role="owner"));db.commit();return {"id":str(g.id),"slug":g.slug}
@router.get("/notifications")
def notifications(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalars(select(CommunityNotification).where(CommunityNotification.user_id==user.id).order_by(CommunityNotification.created_at.desc()).limit(50)).all()
@router.post("/reports")
def report(target_type:str,target_id:UUID,reason:str=Query(...,min_length=3,max_length=500),user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 db.add(CommunityReport(reporter_id=user.id,target_type=target_type,target_id=target_id,reason=clean(reason)));db.commit();return {"status":"reported"}
@router.post("/blocks/{blocked_user_id}")
def block(blocked_user_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 if blocked_user_id==user.id:raise HTTPException(422,"Cannot block yourself")
 if not db.scalar(select(UserBlock).where(UserBlock.user_id==user.id,UserBlock.blocked_user_id==blocked_user_id)):db.add(UserBlock(user_id=user.id,blocked_user_id=blocked_user_id));db.commit()
 return {"status":"blocked"}
@router.get("/admin/reports")
def admin_reports(user:User=Depends(full_admin),db:Session=Depends(get_db)):return db.scalars(select(CommunityReport).order_by(CommunityReport.created_at.desc()).limit(100)).all()

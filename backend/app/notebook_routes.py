import re
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf
from .db import get_db
from .models import Course, CourseModule, Lesson, NoteTag, NotebookFolder, PersonalNote, PersonalNoteTag, User


router = APIRouter(prefix="/api/v1/notebook", tags=["notebook"])


class NoteCreateIn(BaseModel):
    title: str = Field(default="Untitled note", max_length=240)
    content: str = Field(default="", max_length=200_000)
    course_id: uuid.UUID | None = None
    lesson_id: uuid.UUID | None = None
    folder_id: uuid.UUID | None = None
    tags: list[str] = Field(default_factory=list, max_length=20)
    is_favorite: bool = False
    is_pinned: bool = False


class NoteUpdateIn(BaseModel):
    title: str | None = Field(default=None, max_length=240)
    content: str | None = Field(default=None, max_length=200_000)
    course_id: uuid.UUID | None = None
    lesson_id: uuid.UUID | None = None
    folder_id: uuid.UUID | None = None
    tags: list[str] | None = Field(default=None, max_length=20)
    is_favorite: bool | None = None
    is_pinned: bool | None = None
    version: int = Field(ge=1)


class FolderIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)


class TagIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    color: str = Field(default="#818CF8", max_length=20)


def _clean_tags(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = re.sub(r"\s+", " ", value.strip())
        if not clean:
            continue
        if len(clean) > 60:
            raise HTTPException(422, "Tags must be 60 characters or shorter")
        key = clean.casefold()
        if key not in seen:
            seen.add(key)
            result.append(clean)
    if len(result) > 20:
        raise HTTPException(422, "A note can have at most 20 tags")
    return result


def _owned_folder(db: Session, user: User, folder_id: uuid.UUID | None) -> NotebookFolder | None:
    if folder_id is None:
        return None
    folder = db.scalar(select(NotebookFolder).where(NotebookFolder.id == folder_id, NotebookFolder.owner_id == user.id))
    if not folder:
        raise HTTPException(404, "Notebook folder not found")
    return folder


def _validate_links(db: Session, course_id: uuid.UUID | None, lesson_id: uuid.UUID | None, folder_id: uuid.UUID | None, user: User) -> tuple[uuid.UUID | None, uuid.UUID | None, NotebookFolder | None]:
    course = db.get(Course, course_id) if course_id else None
    if course_id and not course:
        raise HTTPException(404, "Course not found")
    lesson = None
    lesson_course_id = None
    if lesson_id:
        lesson, module = db.execute(select(Lesson, CourseModule).join(CourseModule, Lesson.module_id == CourseModule.id).where(Lesson.id == lesson_id)).first() or (None, None)
        if not lesson:
            raise HTTPException(404, "Lesson not found")
        lesson_course_id = module.course_id
        if course_id and course_id != lesson_course_id:
            raise HTTPException(422, "Lesson does not belong to the selected course")
        course_id = lesson_course_id
    folder = _owned_folder(db, user, folder_id)
    return course_id, lesson_id, folder


def _owned_note(db: Session, user: User, note_id: uuid.UUID, lock: bool = False) -> PersonalNote:
    statement = select(PersonalNote).where(PersonalNote.id == note_id, PersonalNote.owner_id == user.id)
    if lock:
        statement = statement.with_for_update()
    note = db.scalar(statement)
    if not note:
        raise HTTPException(404, "Notebook note not found")
    return note


def _tags_for(db: Session, note_id: uuid.UUID) -> list[NoteTag]:
    return db.scalars(select(NoteTag).join(PersonalNoteTag, PersonalNoteTag.tag_id == NoteTag.id).where(PersonalNoteTag.note_id == note_id).order_by(NoteTag.name)).all()


def _set_tags(db: Session, note: PersonalNote, owner_id: uuid.UUID, values: list[str]) -> None:
    names = _clean_tags(values)
    db.execute(delete(PersonalNoteTag).where(PersonalNoteTag.note_id == note.id))
    if not names:
        return
    keys = [name.casefold() for name in names]
    existing = db.scalars(select(NoteTag).where(NoteTag.owner_id == owner_id, func.lower(NoteTag.name).in_(keys))).all()
    by_key = {tag.name.casefold(): tag for tag in existing}
    for name in names:
        tag = by_key.get(name.casefold())
        if not tag:
            tag = NoteTag(owner_id=owner_id, name=name, color="#818CF8")
            db.add(tag)
            db.flush()
            by_key[name.casefold()] = tag
        db.add(PersonalNoteTag(note_id=note.id, tag_id=tag.id))


def _context(db: Session, note: PersonalNote) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    course = db.get(Course, note.course_id) if note.course_id else None
    lesson = db.get(Lesson, note.lesson_id) if note.lesson_id else None
    folder = db.get(NotebookFolder, note.folder_id) if note.folder_id else None
    return (
        {"id": course.id, "title": course.title, "slug": course.slug} if course else None,
        {"id": lesson.id, "title": lesson.title, "slug": lesson.slug} if lesson else None,
        {"id": folder.id, "name": folder.name, "description": folder.description, "created_at": folder.created_at, "updated_at": folder.updated_at} if folder else None,
    )


def _payload(db: Session, note: PersonalNote, include_content: bool = True) -> dict[str, Any]:
    course, lesson, folder = _context(db, note)
    tags = _tags_for(db, note.id)
    value: dict[str, Any] = {
        "id": note.id,
        "title": note.title,
        "excerpt": re.sub(r"\s+", " ", note.content).strip()[:220],
        "course": course,
        "lesson": lesson,
        "folder": folder,
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags],
        "is_favorite": note.is_favorite,
        "is_pinned": note.is_pinned,
        "version": note.version,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }
    if include_content:
        value["content"] = note.content
    return value


@router.get("/notes")
def list_notes(
    view: str = Query("all", pattern=r"^(all|course|personal|favorites|pinned)$"),
    search: str | None = None,
    course_id: uuid.UUID | None = None,
    lesson_id: uuid.UUID | None = None,
    folder_id: uuid.UUID | None = None,
    tag: str | None = None,
    sort: str = Query("updated_at", pattern=r"^(updated_at|created_at|title)$"),
    order: str = Query("desc", pattern=r"^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    filters = [PersonalNote.owner_id == user.id]
    if view == "course":
        filters.append(PersonalNote.course_id.is_not(None))
    elif view == "personal":
        filters.extend([PersonalNote.course_id.is_(None), PersonalNote.lesson_id.is_(None)])
    elif view == "favorites":
        filters.append(PersonalNote.is_favorite.is_(True))
    elif view == "pinned":
        filters.append(PersonalNote.is_pinned.is_(True))
    if course_id:
        filters.append(PersonalNote.course_id == course_id)
    if lesson_id:
        filters.append(PersonalNote.lesson_id == lesson_id)
    if folder_id:
        _owned_folder(db, user, folder_id)
        filters.append(PersonalNote.folder_id == folder_id)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        filters.append((PersonalNote.title.ilike(pattern)) | (PersonalNote.content.ilike(pattern)))
    if tag and tag.strip():
        tag_notes = select(PersonalNoteTag.note_id).join(NoteTag, NoteTag.id == PersonalNoteTag.tag_id).where(NoteTag.owner_id == user.id, func.lower(NoteTag.name) == tag.strip().casefold())
        filters.append(PersonalNote.id.in_(tag_notes))
    sort_column = {"updated_at": PersonalNote.updated_at, "created_at": PersonalNote.created_at, "title": PersonalNote.title}[sort]
    statement = select(PersonalNote).where(*filters).order_by(sort_column.asc() if order == "asc" else sort_column.desc(), PersonalNote.id.desc())
    total = db.scalar(select(func.count(PersonalNote.id)).where(*filters)) or 0
    notes = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [_payload(db, note, include_content=False) for note in notes], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size}


@router.get("/notes/{note_id}/export")
def export_note(note_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    note = _owned_note(db, user, note_id)
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "-", note.title.strip()).strip("-") or "note"
    return {"filename": f"{safe_name}.md", "content": f"# {note.title}\n\n{note.content}"}


@router.get("/notes/{note_id}")
def get_note(note_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _payload(db, _owned_note(db, user, note_id))


@router.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreateIn, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    course_id, lesson_id, _ = _validate_links(db, payload.course_id, payload.lesson_id, payload.folder_id, user)
    note = PersonalNote(owner_id=user.id, title=payload.title.strip() or "Untitled note", content=payload.content, course_id=course_id, lesson_id=lesson_id, folder_id=payload.folder_id, is_favorite=payload.is_favorite, is_pinned=payload.is_pinned)
    db.add(note)
    db.flush()
    _set_tags(db, note, user.id, payload.tags)
    db.commit()
    db.refresh(note)
    return _payload(db, note)


@router.patch("/notes/{note_id}")
def update_note(note_id: uuid.UUID, payload: NoteUpdateIn, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    note = _owned_note(db, user, note_id, lock=True)
    if payload.version != note.version:
        raise HTTPException(409, "This note was changed on another device. Reload before overwriting it.")
    values = payload.model_dump(exclude_unset=True)
    course_id = values.get("course_id", note.course_id)
    lesson_id = values.get("lesson_id", note.lesson_id)
    folder_id = values.get("folder_id", note.folder_id)
    course_id, lesson_id, _ = _validate_links(db, course_id, lesson_id, folder_id, user)
    if "title" in values:
        note.title = (payload.title or "").strip() or "Untitled note"
    if "content" in values:
        note.content = payload.content or ""
    note.course_id, note.lesson_id, note.folder_id = course_id, lesson_id, folder_id
    if "is_favorite" in values:
        note.is_favorite = bool(payload.is_favorite)
    if "is_pinned" in values:
        note.is_pinned = bool(payload.is_pinned)
    if "tags" in values:
        _set_tags(db, note, user.id, payload.tags or [])
    note.version += 1
    db.commit()
    db.refresh(note)
    return _payload(db, note)


@router.delete("/notes/{note_id}")
def delete_note(note_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    note = _owned_note(db, user, note_id)
    db.delete(note)
    db.commit()
    return {"status": "deleted"}


@router.get("/folders")
def list_folders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    folders = db.scalars(select(NotebookFolder).where(NotebookFolder.owner_id == user.id).order_by(NotebookFolder.name)).all()
    return [{"id": folder.id, "name": folder.name, "description": folder.description, "note_count": db.scalar(select(func.count(PersonalNote.id)).where(PersonalNote.owner_id == user.id, PersonalNote.folder_id == folder.id)) or 0, "created_at": folder.created_at, "updated_at": folder.updated_at} for folder in folders]


@router.post("/folders", status_code=status.HTTP_201_CREATED)
def create_folder(payload: FolderIn, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    folder = NotebookFolder(owner_id=user.id, name=payload.name.strip(), description=payload.description.strip())
    if not folder.name:
        raise HTTPException(422, "Folder name is required")
    db.add(folder)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        if "UNIQUE" in str(exc).upper():
            raise HTTPException(409, "A folder with this name already exists") from exc
        raise
    db.refresh(folder)
    return {"id": folder.id, "name": folder.name, "description": folder.description, "note_count": 0, "created_at": folder.created_at, "updated_at": folder.updated_at}


@router.patch("/folders/{folder_id}")
def update_folder(folder_id: uuid.UUID, payload: FolderIn, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    folder = _owned_folder(db, user, folder_id)
    folder.name, folder.description = payload.name.strip(), payload.description.strip()
    if not folder.name:
        raise HTTPException(422, "Folder name is required")
    db.commit()
    db.refresh(folder)
    count = db.scalar(select(func.count(PersonalNote.id)).where(PersonalNote.owner_id == user.id, PersonalNote.folder_id == folder.id)) or 0
    return {"id": folder.id, "name": folder.name, "description": folder.description, "note_count": count, "created_at": folder.created_at, "updated_at": folder.updated_at}


@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    folder = _owned_folder(db, user, folder_id)
    db.execute(update(PersonalNote).where(PersonalNote.owner_id == user.id, PersonalNote.folder_id == folder.id).values(folder_id=None))
    db.delete(folder)
    db.commit()
    return {"status": "deleted"}


@router.get("/tags")
def list_tags(user: User = Depends(current_user), db: Session = Depends(get_db)):
    tags = db.scalars(select(NoteTag).where(NoteTag.owner_id == user.id).order_by(NoteTag.name)).all()
    return [{"id": tag.id, "name": tag.name, "color": tag.color, "note_count": db.scalar(select(func.count(PersonalNoteTag.note_id)).where(PersonalNoteTag.tag_id == tag.id)) or 0} for tag in tags]


@router.post("/tags", status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagIn, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    name = re.sub(r"\s+", " ", payload.name.strip())
    if not name:
        raise HTTPException(422, "Tag name is required")
    existing = db.scalar(select(NoteTag).where(NoteTag.owner_id == user.id, func.lower(NoteTag.name) == name.casefold()))
    if existing:
        return {"id": existing.id, "name": existing.name, "color": existing.color, "note_count": db.scalar(select(func.count(PersonalNoteTag.note_id)).where(PersonalNoteTag.tag_id == existing.id)) or 0}
    tag = NoteTag(owner_id=user.id, name=name, color=payload.color.strip() or "#818CF8")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return {"id": tag.id, "name": tag.name, "color": tag.color, "note_count": 0}


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db), _: None = Depends(require_csrf)):
    tag = db.scalar(select(NoteTag).where(NoteTag.id == tag_id, NoteTag.owner_id == user.id))
    if not tag:
        raise HTTPException(404, "Notebook tag not found")
    db.delete(tag)
    db.commit()
    return {"status": "deleted"}

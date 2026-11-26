from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import Course, Lesson, User


def login(client, email: str):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("note-pass1"), display_name=email.split("@")[0], role="student", account_status="active"))
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "note-pass1"})
    assert response.status_code == 200, response.text
    return {"X-CSRF-Token": client.cookies.get("cm_csrf")}


def course_and_lesson(client):
    with client.session_factory() as db:
        course = db.scalar(select(Course))
        lesson = db.scalar(select(Lesson))
        return str(course.id), str(lesson.id)


def test_notebook_crud_autosave_version_and_export(client):
    headers = login(client, "notebook-one@example.com")
    course_id, lesson_id = course_and_lesson(client)
    created = client.post("/api/v1/notebook/notes", headers=headers, json={"title": "Python pointers", "content": "# Variables\n\nKeep this private.", "course_id": course_id, "lesson_id": lesson_id, "tags": ["Python", "review"], "is_pinned": True})
    assert created.status_code == 201, created.text
    note = created.json()
    assert note["lesson"]["id"] == lesson_id
    assert {tag["name"] for tag in note["tags"]} == {"Python", "review"}

    listed = client.get(f"/api/v1/notebook/notes?lesson_id={lesson_id}&tag=python")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    detail = client.get(f"/api/v1/notebook/notes/{note['id']}")
    assert detail.status_code == 200
    assert detail.json()["content"].startswith("# Variables")

    saved = client.patch(f"/api/v1/notebook/notes/{note['id']}", headers=headers, json={"content": "Updated after autosave", "version": 1})
    assert saved.status_code == 200
    assert saved.json()["version"] == 2
    conflict = client.patch(f"/api/v1/notebook/notes/{note['id']}", headers=headers, json={"content": "stale", "version": 1})
    assert conflict.status_code == 409

    exported = client.get(f"/api/v1/notebook/notes/{note['id']}/export")
    assert exported.status_code == 200
    assert "Updated after autosave" in exported.json()["content"]
    assert client.delete(f"/api/v1/notebook/notes/{note['id']}", headers=headers).status_code == 200
    assert client.get(f"/api/v1/notebook/notes/{note['id']}").status_code == 404


def test_notebook_folders_search_filters_and_owner_isolation(client):
    owner_headers = login(client, "notebook-owner@example.com")
    folder = client.post("/api/v1/notebook/folders", headers=owner_headers, json={"name": "Interview prep", "description": "Private"})
    assert folder.status_code == 201, folder.text
    folder_id = folder.json()["id"]
    created = client.post("/api/v1/notebook/notes", headers=owner_headers, json={"title": "SQL joins", "content": "Remember the LEFT JOIN example", "folder_id": folder_id, "tags": ["database"]})
    assert created.status_code == 201, created.text
    note_id = created.json()["id"]
    assert client.get("/api/v1/notebook/notes?search=left+join").json()["total"] == 1
    assert client.get(f"/api/v1/notebook/notes?folder_id={folder_id}").json()["total"] == 1
    assert client.get("/api/v1/notebook/notes?tag=DATABASE").json()["total"] == 1
    assert client.get("/api/v1/notebook/folders").json()[0]["note_count"] == 1

    other_headers = login(client, "notebook-other@example.com")
    assert client.get(f"/api/v1/notebook/notes/{note_id}").status_code == 404
    assert client.patch(f"/api/v1/notebook/notes/{note_id}", headers=other_headers, json={"content": "no", "version": 1}).status_code == 404
    assert client.delete(f"/api/v1/notebook/notes/{note_id}", headers=other_headers).status_code == 404


def test_notebook_requires_csrf_for_mutations(client):
    login(client, "notebook-csrf@example.com")
    response = client.post("/api/v1/notebook/notes", json={"title": "Blocked"})
    assert response.status_code == 403

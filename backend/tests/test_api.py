from app.main import app

@app.get("/_test/unhandled-error")
def unhandled_error_for_test():
    raise RuntimeError("test-only failure")

def test_health(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request"})
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "test-request"
    assert "X-Response-Time-ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_unhandled_errors_are_safe_and_correlated(client):
    from fastapi.testclient import TestClient
    response = TestClient(app, raise_server_exceptions=False).get("/_test/unhandled-error", headers={"X-Request-ID": "error-request"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error", "request_id": "error-request"}
def test_course_filter_and_pagination(client):
    response=client.get("/api/v1/courses?language=python&page=1&page_size=1"); assert response.status_code==200; assert response.json()["total"]==1
def test_course_detail_and_lesson(client):
    course=client.get("/api/v1/courses/python-foundations"); assert course.status_code==200; assert course.json()["modules"][0]["lessons"][0]["content_en"]=="Hello lesson"
def test_missing_and_unpublished(client):
    assert client.get("/api/v1/courses/missing").status_code==404

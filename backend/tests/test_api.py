def test_health(client): assert client.get("/api/v1/health").json()["status"]=="ok"
def test_course_filter_and_pagination(client):
    response=client.get("/api/v1/courses?language=python&page=1&page_size=1"); assert response.status_code==200; assert response.json()["total"]==1
def test_course_detail_and_lesson(client):
    course=client.get("/api/v1/courses/python-foundations"); assert course.status_code==200; assert course.json()["modules"][0]["lessons"][0]["content_en"]=="Hello lesson"
def test_missing_and_unpublished(client):
    assert client.get("/api/v1/courses/missing").status_code==404

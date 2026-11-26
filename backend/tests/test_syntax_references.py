from app.models import Course, SyntaxReference, SyntaxReferenceExample


def make_reference(course_id, status="published", count=5, slug="python-variables"):
    row = SyntaxReference(
        course_id=course_id,
        title="Python variables",
        slug=slug,
        category="Basics",
        description="Store values with readable names.",
        basic_syntax="name = value",
        when_to_use="Use this when a value should be named and reused.",
        important_notes="Names should describe the value and follow the language rules.",
        status=status,
    )
    row.examples = [SyntaxReferenceExample(example_number=index, title=f"Example {index}", code=f"value = {index}", language="python", expected_output=str(index), explanation="This example stores a value for later use.") for index in range(1, count + 1)]
    return row


def test_public_syntax_references_only_returns_complete_published_entries(client):
    with client.session_factory() as db:
        course = db.query(Course).filter_by(slug="python-foundations").one()
        db.add(make_reference(course.id, "published", 5))
        db.add(make_reference(course.id, "draft", 2, "python-variables-draft"))
        db.commit()

    response = client.get("/api/v1/courses/python-foundations/syntax-references")

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["python-variables"]
    assert len(response.json()[0]["examples"]) == 5


def test_public_syntax_reference_rejects_incomplete_published_entry(client):
    with client.session_factory() as db:
        course = db.query(Course).filter_by(slug="python-foundations").one()
        db.add(make_reference(course.id, "published", 4))
        db.commit()

    response = client.get("/api/v1/courses/python-foundations/syntax-references/python-variables")

    assert response.status_code == 404

from app.models import DeveloperTool, ToolCategory


def seed_tool(client):
    Session = client.session_factory
    with Session() as db:
        category = ToolCategory(name="Data", slug="data", description="Data tools", display_order=1)
        db.add(category)
        db.flush()
        tool = DeveloperTool(category_id=category.id, name="JSON Formatter", slug="json-formatter", short_description="Format JSON", full_description="Format JSON locally", icon_key="braces", route_path="/tools/json-formatter", implementation_key="json_formatter", tags="json|format", display_order=1, is_featured=True, status="published", is_enabled=True)
        draft = DeveloperTool(category_id=category.id, name="Draft Tool", slug="draft-tool", short_description="Draft", full_description="Draft", icon_key="wrench", route_path="/tools/draft-tool", implementation_key="json_formatter", status="draft", is_enabled=True)
        disabled = DeveloperTool(category_id=category.id, name="Disabled Tool", slug="disabled-tool", short_description="Disabled", full_description="Disabled", icon_key="wrench", route_path="/tools/disabled-tool", implementation_key="json_formatter", status="published", is_enabled=False)
        db.add_all([tool, draft, disabled]); db.commit()


def test_public_catalog_search_and_filters(client):
    seed_tool(client)
    response = client.get("/api/v1/tools", params={"search": "json", "category": "data", "tag": "format", "featured": "true"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["slug"] == "json-formatter"
    assert "implementation_key" not in payload["items"][0]


def test_draft_and_disabled_tools_are_not_public(client):
    seed_tool(client)
    assert client.get("/api/v1/tools/draft-tool").status_code == 404
    assert client.get("/api/v1/tools/disabled-tool").status_code == 404
    assert client.get("/api/v1/admin/tools").status_code == 401


def test_categories_only_include_active_categories(client):
    seed_tool(client)
    response = client.get("/api/v1/tools/categories")
    assert response.status_code == 200
    assert response.json()[0]["slug"] == "data"

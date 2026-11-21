"""Idempotently import the approved built-in tools into PostgreSQL.

Run after ``alembic upgrade head``.  Existing rows are never overwritten;
this only creates missing registry-backed categories and tools.
"""

from pathlib import Path
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db import SessionLocal
from app.models import DeveloperTool, ToolCategory
from app.tool_registry import category_definitions, tool_definitions


def import_tools() -> tuple[int, int]:
    created_categories = created_tools = 0
    with SessionLocal.begin() as db:
        categories: dict[str, ToolCategory] = {}
        for definition in category_definitions():
            row = db.scalar(select(ToolCategory).where(ToolCategory.slug == definition["slug"]))
            if row is None:
                row = ToolCategory(**definition)
                db.add(row)
                db.flush()
                created_categories += 1
            categories[definition["slug"]] = row
        for definition in tool_definitions():
            row = db.scalar(select(DeveloperTool).where(DeveloperTool.slug == definition.slug))
            if row is not None:
                continue
            db.add(DeveloperTool(
                category_id=categories[definition.category_slug].id,
                name=definition.name,
                slug=definition.slug,
                short_description=definition.short_description,
                full_description=definition.full_description,
                icon_key=definition.icon_key,
                route_path=definition.route_path,
                implementation_key=definition.implementation_key,
                tags="|".join(definition.tags),
                display_order=definition.display_order,
                is_featured=definition.is_featured,
                is_enabled=True,
                status="published",
                published_at=datetime.now(timezone.utc),
            ))
            created_tools += 1
    return created_categories, created_tools


if __name__ == "__main__":
    categories, tools = import_tools()
    print(f"Developer tools import complete: {categories} categories created, {tools} tools created")

# Project-based learning system

The project catalog reuses the existing `project_templates`, `project_milestones`, and student progress tables. Migration `0026_project_learning_content` adds editorial project metadata, read-only step content, and per-user bookmarks without changing existing enrollment or progress rows.

Public endpoints are `GET /api/v1/projects`, `GET /api/v1/project-categories`, `GET /api/v1/projects/{slug}`, `GET /api/v1/projects/{slug}/modules`, and `GET /api/v1/projects/{slug}/steps`. Authenticated users can start a project, bookmark it, read their progress, and mark owned milestones complete. All public responses are limited to published projects; private progress remains authenticated and ownership checked.

The seed is idempotent and creates a reviewed starter catalog with complete guided reading steps. Existing projects and educational content are preserved. The catalog is intentionally limited to authored records; additional requested project ideas remain unpublished until their content is reviewed.

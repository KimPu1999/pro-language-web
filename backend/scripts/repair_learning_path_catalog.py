"""Link the published roadmap records to real published courses.

This is an additive data repair for the existing ``career_roadmaps`` catalog.
It never copies courses, removes resources, changes enrollment/progress, or
changes publication status. Run it after the localization migration:

    PYTHONPATH=. .venv/bin/python scripts/repair_learning_path_catalog.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import CareerRoadmap, Course, ProjectTemplate, RoadmapStage, RoadmapStep, RoadmapStepResource


COURSE_MAP: dict[str, tuple[str, ...]] = {
    "ai-engineer": ("python", "data-analysis", "machine-learning", "python-for-ai"),
    "backend-developer": ("python", "fastapi", "node-js", "express-js", "postgresql"),
    "cybersecurity": ("networking-fundamentals", "operating-systems", "cybersecurity-fundamentals", "web-security", "secure-coding", "owasp-top-10"),
    "devops-engineer": ("linux", "git", "docker", "ci-cd", "aws", "microsoft-azure"),
    "frontend-developer": ("html", "css", "javascript", "typescript", "react", "next-js", "tailwind-css"),
    "full-stack-developer": ("html", "css", "javascript", "react", "node-js", "postgresql"),
    "mobile-developer": ("dart", "flutter", "react-native"),
    "python-developer": ("python", "python-for-ai", "fastapi", "django"),
}

PROJECT_MAP: dict[str, tuple[str, ...]] = {
    "backend-developer": ("python-fastapi-rest-api", "nodejs-authentication-api"),
    "frontend-developer": ("html-css-landing-page", "personal-portfolio-website", "react-task-manager"),
    "full-stack-developer": ("e-commerce-application", "real-time-chat-application", "saas-dashboard"),
    "python-developer": ("python-cli-calculator", "python-fastapi-rest-api"),
}


def repair() -> tuple[int, int, int, list[str]]:
    linked = 0
    linked_projects = 0
    created_stages = 0
    missing: list[str] = []
    with SessionLocal.begin() as db:
        courses = {course.slug: course for course in db.scalars(select(Course).where(Course.published.is_(True))).all()}
        roadmaps = {path.slug: path for path in db.scalars(select(CareerRoadmap).where(CareerRoadmap.slug.in_(COURSE_MAP))).all()}

        for slug, course_slugs in COURSE_MAP.items():
            roadmap = roadmaps.get(slug)
            if roadmap is None:
                missing.append(f"path:{slug}")
                continue

            stages = db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id == roadmap.id).order_by(RoadmapStage.position)).all()
            if not stages:
                stage = RoadmapStage(roadmap_id=roadmap.id, title="Foundations", description_en="Build the foundations for this learning path.", level="beginner", position=0)
                db.add(stage)
                db.flush()
                stages = [stage]
                created_stages += 1

            first_stage = stages[0]
            first_step = db.scalar(select(RoadmapStep).where(RoadmapStep.stage_id == first_stage.id).order_by(RoadmapStep.position))
            if first_step is None:
                first_step = RoadmapStep(stage_id=first_stage.id, title="Start with the fundamentals", instructions_en="Complete the linked course before continuing.", position=0)
                db.add(first_step)
                db.flush()

            existing_course_ids = {
                resource.resource_id
                for resource in db.scalars(
                    select(RoadmapStepResource)
                    .join(RoadmapStep, RoadmapStepResource.step_id == RoadmapStep.id)
                    .join(RoadmapStage, RoadmapStep.stage_id == RoadmapStage.id)
                    .where(RoadmapStage.roadmap_id == roadmap.id, RoadmapStepResource.resource_type == "course")
                ).all()
            }
            next_position = max((stage.position for stage in stages), default=-1) + 1

            for index, course_slug in enumerate(course_slugs):
                course = courses.get(course_slug)
                if course is None:
                    missing.append(f"{slug}:course:{course_slug}")
                    continue
                if course.id in existing_course_ids:
                    continue

                if index == 0 and not db.scalar(select(RoadmapStepResource.id).where(RoadmapStepResource.step_id == first_step.id, RoadmapStepResource.resource_type == "course")):
                    target_step = first_step
                else:
                    stage = RoadmapStage(roadmap_id=roadmap.id, title=f"Stage {next_position + 1}: {course.title}", description_en=f"Build practical skills with the published {course.title} course.", level="intermediate" if next_position < 3 else "advanced", position=next_position)
                    db.add(stage)
                    db.flush()
                    stages.append(stage)
                    target_step = RoadmapStep(stage_id=stage.id, title=course.title, instructions_en=f"Complete the published {course.title} course before continuing.", position=0)
                    db.add(target_step)
                    db.flush()
                    next_position += 1
                    created_stages += 1

                db.add(RoadmapStepResource(step_id=target_step.id, resource_type="course", resource_id=course.id))
                existing_course_ids.add(course.id)
                linked += 1

            target_step = db.scalar(select(RoadmapStep).where(RoadmapStep.stage_id == stages[-1].id).order_by(RoadmapStep.position.desc()))
            if target_step is not None:
                for project_slug in PROJECT_MAP.get(slug, ()):
                    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == project_slug, ProjectTemplate.published.is_(True)))
                    if project is None:
                        missing.append(f"{slug}:project:{project_slug}")
                        continue
                    exists_link = db.scalar(select(RoadmapStepResource.id).where(RoadmapStepResource.step_id == target_step.id, RoadmapStepResource.resource_type == "project", RoadmapStepResource.resource_id == project.id))
                    if not exists_link:
                        db.add(RoadmapStepResource(step_id=target_step.id, resource_type="project", resource_id=project.id))
                        linked_projects += 1

    return linked, linked_projects, created_stages, missing


if __name__ == "__main__":
    linked_count, project_count, stage_count, missing_slugs = repair()
    print(f"linked_courses={linked_count} linked_projects={project_count} created_stages={stage_count}")
    if missing_slugs:
        print("missing=" + ",".join(missing_slugs))

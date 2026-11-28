"""Seed explicit catalog display titles and technology badges for existing courses."""
from alembic import op
import sqlalchemy as sa

revision = "0068_card_display_defaults"
down_revision = "0067_course_card_appearance"
branch_labels = None
depends_on = None

DISPLAY = {
    "c-programming": ("C Programming", "C"), "cpp-programming": ("C++", "C++"),
    "java": ("Java", "Java"), "advanced-java": ("Advanced Java", "Java"),
    "python": ("Python", "Python"), "javascript": ("JavaScript", "JavaScript"),
    "typescript": ("TypeScript", "TypeScript"), "react": ("React", "React"),
    "next-js": ("Next.js", "Next.js"), "php": ("PHP", "PHP"), "laravel": ("Laravel", "Laravel"),
    "node-js": ("Node.js", "Node.js"), "html": ("HTML", "HTML"), "css": ("CSS", "CSS"),
    "sql": ("SQL", "SQL"), "postgresql": ("PostgreSQL", "PostgreSQL"),
    "mongodb": ("MongoDB", "MongoDB"), "aws": ("AWS Cloud Computing", "AWS"),
    "algorithms": ("Algorithms", "Algorithms"), "operating-systems": ("Operating Systems", "Operating Systems"),
    "docker": ("Docker", "Docker"), "git": ("Git & GitHub", "Git"), "github": ("GitHub", "GitHub"),
}

def upgrade():
    connection = op.get_bind()
    for slug, (title, technology) in DISPLAY.items():
        connection.execute(sa.text("UPDATE courses SET display_title=:title, technology_name=:technology, card_short_description=COALESCE(NULLIF(card_short_description, ''), short_description), card_image_alt=:alt WHERE slug=:slug"), {"slug": slug, "title": title, "technology": technology, "alt": f"{title} technology logo"})

def downgrade():
    # Preserve administrator edits; this migration only seeds previously empty/default values.
    pass

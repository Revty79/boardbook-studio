from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Character, Generation, Project, StoryPage


def build_dashboard_summary(db: Session) -> dict[str, int]:
    return {
        "project_count": int(db.scalar(select(func.count(Project.id))) or 0),
        "character_count": int(db.scalar(select(func.count(Character.id))) or 0),
        "page_count": int(db.scalar(select(func.count(StoryPage.id))) or 0),
        "generation_count": int(db.scalar(select(func.count(Generation.id))) or 0),
    }

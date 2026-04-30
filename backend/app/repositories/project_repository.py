from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Character, Generation, Project, StoryPage


class ProjectRepository:
    def list(self, db: Session) -> list[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        return list(db.scalars(stmt).all())

    def get(self, db: Session, project_id: int) -> Project | None:
        return db.get(Project, project_id)

    def create(self, db: Session, *, title: str, description: str | None) -> Project:
        project = Project(title=title, description=description)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update(self, db: Session, project: Project, *, title: str | None, description: str | None) -> Project:
        if title is not None:
            project.title = title
        if description is not None:
            project.description = description
        db.commit()
        db.refresh(project)
        return project

    def stats(self, db: Session, project_id: int) -> dict[str, int]:
        character_count = db.scalar(select(func.count(Character.id)).where(Character.project_id == project_id)) or 0
        page_count = db.scalar(select(func.count(StoryPage.id)).where(StoryPage.project_id == project_id)) or 0
        generation_count = (
            db.scalar(
                select(func.count(Generation.id))
                .join(StoryPage, Generation.page_id == StoryPage.id)
                .where(StoryPage.project_id == project_id)
            )
            or 0
        )
        return {
            "character_count": int(character_count),
            "page_count": int(page_count),
            "generation_count": int(generation_count),
        }

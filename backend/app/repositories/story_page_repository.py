from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import StoryPage


class StoryPageRepository:
    def list_for_project(self, db: Session, project_id: int) -> list[StoryPage]:
        stmt = select(StoryPage).where(StoryPage.project_id == project_id).order_by(StoryPage.page_number.asc())
        return list(db.scalars(stmt).all())

    def get(self, db: Session, project_id: int, page_id: int) -> StoryPage | None:
        stmt = select(StoryPage).where(StoryPage.project_id == project_id, StoryPage.id == page_id)
        return db.scalar(stmt)

    def get_by_id(self, db: Session, page_id: int) -> StoryPage | None:
        return db.get(StoryPage, page_id)

    def create(self, db: Session, *, project_id: int, title: str, page_number: int, text_content: str) -> StoryPage:
        page = StoryPage(project_id=project_id, title=title, page_number=page_number, text_content=text_content)
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    def update(
        self,
        db: Session,
        *,
        page: StoryPage,
        title: str | None,
        page_number: int | None,
        text_content: str | None,
    ) -> StoryPage:
        if title is not None:
            page.title = title
        if page_number is not None:
            page.page_number = page_number
        if text_content is not None:
            page.text_content = text_content
        db.commit()
        db.refresh(page)
        return page

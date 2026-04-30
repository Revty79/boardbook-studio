from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Generation, RefinementMessage, StoryPage


class GenerationRepository:
    def list_for_page(self, db: Session, page_id: int) -> list[Generation]:
        stmt = select(Generation).where(Generation.page_id == page_id).order_by(Generation.created_at.desc())
        return list(db.scalars(stmt).all())

    def get(self, db: Session, generation_id: int) -> Generation | None:
        return db.get(Generation, generation_id)

    def create(
        self,
        db: Session,
        *,
        page_id: int,
        parent_generation_id: int | None,
        prompt: str,
        negative_prompt: str,
        seed: int | None,
        provider: str,
        image_path: str,
        generation_type: str,
    ) -> Generation:
        generation = Generation(
            page_id=page_id,
            parent_generation_id=parent_generation_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            provider=provider,
            image_path=image_path,
            generation_type=generation_type,
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)
        return generation

    def add_refinement_message(
        self,
        db: Session,
        *,
        generation_id: int,
        role: str,
        content: str,
    ) -> RefinementMessage:
        message = RefinementMessage(generation_id=generation_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def approve(self, db: Session, *, generation: Generation) -> Generation:
        generation.approved_at = datetime.now(timezone.utc)
        page: StoryPage | None = db.get(StoryPage, generation.page_id)
        if page is not None:
            page.approved_generation_id = generation.id
        db.commit()
        db.refresh(generation)
        return generation

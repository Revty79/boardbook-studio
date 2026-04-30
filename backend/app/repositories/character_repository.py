from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Character, CharacterReference


class CharacterRepository:
    def list_for_project(self, db: Session, project_id: int) -> list[Character]:
        stmt = select(Character).where(Character.project_id == project_id).order_by(Character.created_at.desc())
        return list(db.scalars(stmt).all())

    def get(self, db: Session, project_id: int, character_id: int) -> Character | None:
        stmt = select(Character).where(Character.project_id == project_id, Character.id == character_id)
        return db.scalar(stmt)

    def create(
        self,
        db: Session,
        *,
        project_id: int,
        name: str,
        description: str | None,
        personality: str | None,
        locked_traits: list[str],
    ) -> Character:
        character = Character(
            project_id=project_id,
            name=name,
            description=description,
            personality=personality,
            locked_traits=locked_traits,
        )
        db.add(character)
        db.commit()
        db.refresh(character)
        return character

    def update(
        self,
        db: Session,
        *,
        character: Character,
        name: str | None,
        description: str | None,
        personality: str | None,
        locked_traits: list[str] | None,
    ) -> Character:
        if name is not None:
            character.name = name
        if description is not None:
            character.description = description
        if personality is not None:
            character.personality = personality
        if locked_traits is not None:
            character.locked_traits = locked_traits
        db.commit()
        db.refresh(character)
        return character

    def add_reference(
        self,
        db: Session,
        *,
        character_id: int,
        image_path: str,
        note: str | None,
    ) -> CharacterReference:
        ref = CharacterReference(character_id=character_id, image_path=image_path, note=note)
        db.add(ref)
        db.commit()
        db.refresh(ref)
        return ref

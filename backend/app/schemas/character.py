from datetime import datetime

from pydantic import Field

from app.schemas.common import SchemaBase


class CharacterReferenceCreate(SchemaBase):
    image_path: str
    note: str | None = None


class CharacterReferenceRead(SchemaBase):
    id: int
    character_id: int
    image_path: str
    note: str | None
    created_at: datetime


class CharacterCreate(SchemaBase):
    name: str
    description: str | None = None
    personality: str | None = None
    locked_traits: list[str] = Field(default_factory=list)


class CharacterUpdate(SchemaBase):
    name: str | None = None
    description: str | None = None
    personality: str | None = None
    locked_traits: list[str] | None = None


class CharacterRead(SchemaBase):
    id: int
    project_id: int
    name: str
    description: str | None
    personality: str | None
    locked_traits: list[str]
    created_at: datetime
    updated_at: datetime
    references: list[CharacterReferenceRead]

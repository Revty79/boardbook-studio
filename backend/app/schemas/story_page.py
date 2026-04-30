from datetime import datetime

from app.schemas.common import SchemaBase


class StoryPageCreate(SchemaBase):
    title: str = "Untitled Page"
    page_number: int = 1
    text_content: str = ""


class StoryPageUpdate(SchemaBase):
    title: str | None = None
    page_number: int | None = None
    text_content: str | None = None


class StoryPageRead(SchemaBase):
    id: int
    project_id: int
    title: str
    page_number: int
    text_content: str
    approved_generation_id: int | None
    created_at: datetime
    updated_at: datetime

from datetime import datetime

from app.schemas.common import SchemaBase


class ProjectCreate(SchemaBase):
    title: str
    description: str | None = None


class ProjectUpdate(SchemaBase):
    title: str | None = None
    description: str | None = None


class ProjectRead(SchemaBase):
    id: int
    title: str
    description: str | None
    created_at: datetime


class ProjectStats(SchemaBase):
    character_count: int
    page_count: int
    generation_count: int


class ProjectDetail(ProjectRead):
    stats: ProjectStats

from app.schemas.common import SchemaBase


class DashboardSummary(SchemaBase):
    project_count: int
    character_count: int
    page_count: int
    generation_count: int

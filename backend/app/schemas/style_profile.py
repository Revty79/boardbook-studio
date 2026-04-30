from datetime import datetime

from app.schemas.common import SchemaBase


class StyleProfileUpsert(SchemaBase):
    visual_style: str
    color_palette: str
    lighting: str
    composition: str
    negative_prompt_rules: str


class StyleProfileRead(SchemaBase):
    id: int
    project_id: int
    visual_style: str
    color_palette: str
    lighting: str
    composition: str
    negative_prompt_rules: str
    created_at: datetime
    updated_at: datetime

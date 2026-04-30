from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import SchemaBase

GenerationType = Literal["initial", "refine", "variation", "inpaint", "mock"]


class RefinementMessageCreate(SchemaBase):
    content: str


class RefinementMessageRead(SchemaBase):
    id: int
    generation_id: int
    role: str
    content: str
    created_at: datetime


class GenerationRead(SchemaBase):
    id: int
    page_id: int
    parent_generation_id: int | None
    prompt: str
    negative_prompt: str
    seed: int | None
    provider: str
    image_path: str
    generation_type: str
    created_at: datetime
    approved_at: datetime | None
    refinement_messages: list[RefinementMessageRead] = Field(default_factory=list)


class PromptBuildInput(SchemaBase):
    page_id: int


class PromptBuildOutput(SchemaBase):
    prompt: str
    negative_prompt: str
    seed: int | None


class GenerateImageRequest(SchemaBase):
    page_id: int


class RefineGenerationRequest(SchemaBase):
    page_id: int
    parent_generation_id: int
    instruction: str


class ApproveGenerationRequest(SchemaBase):
    generation_id: int

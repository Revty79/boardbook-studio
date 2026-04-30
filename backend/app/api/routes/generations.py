from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_generation_service
from app.db.session import get_db
from app.repositories import GenerationRepository
from app.schemas import (
    ApproveGenerationRequest,
    GenerateImageRequest,
    GenerationRead,
    PromptBuildInput,
    PromptBuildOutput,
    RefineGenerationRequest,
)
from app.services import GenerationService

router = APIRouter()
generation_repo = GenerationRepository()


@router.post("/generations/build-prompt", response_model=PromptBuildOutput)
def build_prompt(
    payload: PromptBuildInput,
    db: Session = Depends(get_db),
    service: GenerationService = Depends(get_generation_service),
) -> PromptBuildOutput:
    result = service.build_prompt(db, page_id=payload.page_id)
    return PromptBuildOutput.model_validate(result)


@router.post("/generations/generate", response_model=GenerationRead)
def generate_image(
    payload: GenerateImageRequest,
    db: Session = Depends(get_db),
    service: GenerationService = Depends(get_generation_service),
) -> GenerationRead:
    generation = service.generate_initial(db, page_id=payload.page_id)
    return GenerationRead.model_validate(generation)


@router.post("/generations/refine", response_model=GenerationRead)
def refine_image(
    payload: RefineGenerationRequest,
    db: Session = Depends(get_db),
    service: GenerationService = Depends(get_generation_service),
) -> GenerationRead:
    generation = service.refine(
        db,
        page_id=payload.page_id,
        parent_generation_id=payload.parent_generation_id,
        instruction=payload.instruction,
    )
    return GenerationRead.model_validate(generation)


@router.post("/generations/approve", response_model=GenerationRead)
def approve_generation(
    payload: ApproveGenerationRequest,
    db: Session = Depends(get_db),
    service: GenerationService = Depends(get_generation_service),
) -> GenerationRead:
    generation = service.approve(db, generation_id=payload.generation_id)
    return GenerationRead.model_validate(generation)


@router.get("/pages/{page_id}/generations", response_model=list[GenerationRead])
def list_page_generations(page_id: int, db: Session = Depends(get_db)) -> list[GenerationRead]:
    generations = generation_repo.list_for_page(db, page_id)
    return [GenerationRead.model_validate(generation) for generation in generations]

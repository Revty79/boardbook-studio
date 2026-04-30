from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.providers import get_image_provider, get_llm_provider
from app.repositories import CharacterRepository, GenerationRepository, StoryPageRepository, StyleProfileRepository
from app.services.prompt_builder import build_prompt_payload


class GenerationService:
    def __init__(self) -> None:
        self.page_repo = StoryPageRepository()
        self.character_repo = CharacterRepository()
        self.style_repo = StyleProfileRepository()
        self.generation_repo = GenerationRepository()
        self.llm_provider = get_llm_provider()
        self.image_provider = get_image_provider()

    def build_prompt(self, db: Session, *, page_id: int) -> dict:
        page = self.page_repo.get_by_id(db, page_id)
        if page is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story page not found")

        characters = self.character_repo.list_for_project(db, page.project_id)
        style = self.style_repo.get_for_project(db, page.project_id)

        payload = build_prompt_payload(page=page, characters=characters, style_profile=style)
        result = self.llm_provider.build_initial_prompt(payload)
        return {
            "prompt": result.prompt,
            "negative_prompt": result.negative_prompt,
            "seed": result.seed,
        }

    def generate_initial(self, db: Session, *, page_id: int):
        page = self.page_repo.get_by_id(db, page_id)
        if page is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story page not found")

        characters = self.character_repo.list_for_project(db, page.project_id)
        style = self.style_repo.get_for_project(db, page.project_id)
        payload = build_prompt_payload(page=page, characters=characters, style_profile=style)

        prompt_result = self.llm_provider.build_initial_prompt(payload)
        image_result = self.image_provider.generate_image(
            prompt=prompt_result.prompt,
            negative_prompt=prompt_result.negative_prompt,
            seed=prompt_result.seed,
        )

        return self.generation_repo.create(
            db,
            page_id=page_id,
            parent_generation_id=None,
            prompt=prompt_result.prompt,
            negative_prompt=prompt_result.negative_prompt,
            seed=image_result.seed,
            provider=image_result.provider,
            image_path=image_result.image_path,
            generation_type="initial",
        )

    def refine(self, db: Session, *, page_id: int, parent_generation_id: int, instruction: str):
        page = self.page_repo.get_by_id(db, page_id)
        if page is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story page not found")

        parent_generation = self.generation_repo.get(db, parent_generation_id)
        if parent_generation is None or parent_generation.page_id != page_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent generation not found")

        characters = self.character_repo.list_for_project(db, page.project_id)
        style = self.style_repo.get_for_project(db, page.project_id)
        payload = build_prompt_payload(page=page, characters=characters, style_profile=style)

        prompt_result = self.llm_provider.refine_prompt(
            payload=payload,
            parent_prompt=parent_generation.prompt,
            parent_negative_prompt=parent_generation.negative_prompt,
            instruction=instruction,
        )
        image_result = self.image_provider.generate_image(
            prompt=prompt_result.prompt,
            negative_prompt=prompt_result.negative_prompt,
            seed=prompt_result.seed,
        )

        generation = self.generation_repo.create(
            db,
            page_id=page_id,
            parent_generation_id=parent_generation_id,
            prompt=prompt_result.prompt,
            negative_prompt=prompt_result.negative_prompt,
            seed=image_result.seed,
            provider=image_result.provider,
            image_path=image_result.image_path,
            generation_type="refine",
        )
        self.generation_repo.add_refinement_message(
            db,
            generation_id=generation.id,
            role="user",
            content=instruction,
        )

        return generation

    def approve(self, db: Session, *, generation_id: int):
        generation = self.generation_repo.get(db, generation_id)
        if generation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")
        return self.generation_repo.approve(db, generation=generation)

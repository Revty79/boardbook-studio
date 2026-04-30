from fastapi import Depends

from app.services import GenerationService


def get_generation_service() -> GenerationService:
    return GenerationService()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import ProjectRepository, StyleProfileRepository
from app.schemas import StyleProfileRead, StyleProfileUpsert

router = APIRouter()
project_repo = ProjectRepository()
style_repo = StyleProfileRepository()


@router.get("/{project_id}/style-profile", response_model=StyleProfileRead)
def get_style_profile(project_id: int, db: Session = Depends(get_db)) -> StyleProfileRead:
    if project_repo.get(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    profile = style_repo.get_for_project(db, project_id)
    if profile is None:
        profile = style_repo.upsert(
            db,
            project_id=project_id,
            visual_style="Soft storybook watercolor",
            color_palette="Warm pastels",
            lighting="Gentle morning light",
            composition="Simple characters with easy-to-read silhouettes",
            negative_prompt_rules="No photorealism. No scary faces. No horror themes.",
        )
    return StyleProfileRead.model_validate(profile)


@router.put("/{project_id}/style-profile", response_model=StyleProfileRead)
def upsert_style_profile(
    project_id: int,
    payload: StyleProfileUpsert,
    db: Session = Depends(get_db),
) -> StyleProfileRead:
    if project_repo.get(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    profile = style_repo.upsert(
        db,
        project_id=project_id,
        visual_style=payload.visual_style,
        color_palette=payload.color_palette,
        lighting=payload.lighting,
        composition=payload.composition,
        negative_prompt_rules=payload.negative_prompt_rules,
    )
    return StyleProfileRead.model_validate(profile)

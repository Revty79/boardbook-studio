from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import CharacterRepository, ProjectRepository
from app.schemas import (
    CharacterCreate,
    CharacterRead,
    CharacterReferenceCreate,
    CharacterReferenceRead,
    CharacterUpdate,
)
from app.utils.files import save_upload_file

router = APIRouter()
project_repo = ProjectRepository()
character_repo = CharacterRepository()


def _assert_project_exists(db: Session, project_id: int) -> None:
    if project_repo.get(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.get("/{project_id}/characters", response_model=list[CharacterRead])
def list_characters(project_id: int, db: Session = Depends(get_db)) -> list[CharacterRead]:
    _assert_project_exists(db, project_id)
    characters = character_repo.list_for_project(db, project_id)
    return [CharacterRead.model_validate(character) for character in characters]


@router.post("/{project_id}/characters", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
def create_character(project_id: int, payload: CharacterCreate, db: Session = Depends(get_db)) -> CharacterRead:
    _assert_project_exists(db, project_id)
    character = character_repo.create(
        db,
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        personality=payload.personality,
        locked_traits=payload.locked_traits,
    )
    return CharacterRead.model_validate(character)


@router.get("/{project_id}/characters/{character_id}", response_model=CharacterRead)
def get_character(project_id: int, character_id: int, db: Session = Depends(get_db)) -> CharacterRead:
    character = character_repo.get(db, project_id, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return CharacterRead.model_validate(character)


@router.patch("/{project_id}/characters/{character_id}", response_model=CharacterRead)
def update_character(
    project_id: int,
    character_id: int,
    payload: CharacterUpdate,
    db: Session = Depends(get_db),
) -> CharacterRead:
    character = character_repo.get(db, project_id, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    updated = character_repo.update(
        db,
        character=character,
        name=payload.name,
        description=payload.description,
        personality=payload.personality,
        locked_traits=payload.locked_traits,
    )
    return CharacterRead.model_validate(updated)


@router.post(
    "/{project_id}/characters/{character_id}/references",
    response_model=CharacterReferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def add_character_reference(
    project_id: int,
    character_id: int,
    payload: CharacterReferenceCreate,
    db: Session = Depends(get_db),
) -> CharacterReferenceRead:
    character = character_repo.get(db, project_id, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    reference = character_repo.add_reference(
        db,
        character_id=character.id,
        image_path=payload.image_path,
        note=payload.note,
    )
    return CharacterReferenceRead.model_validate(reference)


@router.post(
    "/{project_id}/characters/{character_id}/references/upload",
    response_model=CharacterReferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_character_reference(
    project_id: int,
    character_id: int,
    file: UploadFile = File(...),
    note: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> CharacterReferenceRead:
    character = character_repo.get(db, project_id, character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    path = save_upload_file(file, folder=f"references/character_{character_id}")
    reference = character_repo.add_reference(
        db,
        character_id=character.id,
        image_path=path,
        note=note,
    )
    return CharacterReferenceRead.model_validate(reference)

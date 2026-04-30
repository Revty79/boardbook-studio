from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import ProjectRepository, StoryPageRepository
from app.schemas import StoryPageCreate, StoryPageRead, StoryPageUpdate

router = APIRouter()
project_repo = ProjectRepository()
page_repo = StoryPageRepository()


@router.get("/{project_id}/pages", response_model=list[StoryPageRead])
def list_pages(project_id: int, db: Session = Depends(get_db)) -> list[StoryPageRead]:
    if project_repo.get(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    pages = page_repo.list_for_project(db, project_id)
    return [StoryPageRead.model_validate(page) for page in pages]


@router.post("/{project_id}/pages", response_model=StoryPageRead, status_code=status.HTTP_201_CREATED)
def create_page(project_id: int, payload: StoryPageCreate, db: Session = Depends(get_db)) -> StoryPageRead:
    if project_repo.get(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    page = page_repo.create(
        db,
        project_id=project_id,
        title=payload.title,
        page_number=payload.page_number,
        text_content=payload.text_content,
    )
    return StoryPageRead.model_validate(page)


@router.get("/{project_id}/pages/{page_id}", response_model=StoryPageRead)
def get_page(project_id: int, page_id: int, db: Session = Depends(get_db)) -> StoryPageRead:
    page = page_repo.get(db, project_id, page_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story page not found")
    return StoryPageRead.model_validate(page)


@router.patch("/{project_id}/pages/{page_id}", response_model=StoryPageRead)
def update_page(
    project_id: int,
    page_id: int,
    payload: StoryPageUpdate,
    db: Session = Depends(get_db),
) -> StoryPageRead:
    page = page_repo.get(db, project_id, page_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story page not found")

    updated = page_repo.update(
        db,
        page=page,
        title=payload.title,
        page_number=payload.page_number,
        text_content=payload.text_content,
    )
    return StoryPageRead.model_validate(updated)

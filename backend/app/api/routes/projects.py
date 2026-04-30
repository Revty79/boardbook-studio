from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import ProjectRepository
from app.schemas import ProjectCreate, ProjectDetail, ProjectRead, ProjectStats, ProjectUpdate

router = APIRouter()
repo = ProjectRepository()


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    projects = repo.list(db)
    return [ProjectRead.model_validate(project) for project in projects]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    project = repo.create(db, title=payload.title, description=payload.description)
    return ProjectRead.model_validate(project)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectDetail:
    project = repo.get(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    stats = repo.stats(db, project_id)
    return ProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        created_at=project.created_at,
        stats=ProjectStats.model_validate(stats),
    )


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)) -> ProjectRead:
    project = repo.get(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    updated = repo.update(db, project=project, title=payload.title, description=payload.description)
    return ProjectRead.model_validate(updated)

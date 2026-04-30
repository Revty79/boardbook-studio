from fastapi import APIRouter

from app.api.routes import characters, dashboard, generations, projects, story_pages, style_profiles

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(characters.router, prefix="/projects", tags=["characters"])
api_router.include_router(style_profiles.router, prefix="/projects", tags=["style-profiles"])
api_router.include_router(story_pages.router, prefix="/projects", tags=["story-pages"])
api_router.include_router(generations.router, tags=["generations"])

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.seed import seed_demo_data

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)

    with SessionLocal() as db:
        seed_demo_data(db)


app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}

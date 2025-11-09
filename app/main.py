import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.auth.router import router as auth_router
from app.api.v1.posts.router import router as post_router
from app.api.v1.upload.router import router as upload_router

# 👇 ¡IMPORTAR modelos antes de create_all!
from app.core.db import Base, engine, get_db

# Solo en desarrollo: crear tablas si no existen

MEDIA_DIR = "app/media"


def create_app() -> FastAPI:
    app = FastAPI(title="Mini blo")
    Base.metadata.create_all(bind=engine)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(upload_router)

    os.makedirs(MEDIA_DIR, exist_ok=True)  # CREAMOS LA CARPETA SI No eXISTE
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()


from fastapi import  FastAPI

# 👇 ¡IMPORTAR modelos antes de create_all!
from app.core.db import Base,engine,get_db
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.upload.router import router as upload_router


# Solo en desarrollo: crear tablas si no existen


def create_app()-> FastAPI:
    app=FastAPI(title="Mini blo")
    Base.metadata.create_all(bind=engine)
    app.include_router(auth_router,prefix='/api/v1')
    app.include_router(post_router)
    app.include_router(upload_router)
    return app



app=create_app()


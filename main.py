from turtle import title
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.db import Base, engine, get_db


# 👇 ¡IMPORTAR modelos antes de create_all!
from app.models.models import AuthorORM, PostORM, TagORM, post_tags
from app.schemas.schemas import PostCreate, PostPublic  

# Solo en desarrollo: crear tablas si no existen
Base.metadata.create_all(bind=engine)

app=FastAPI(title='Personal Blog')

@app.get("/")
def home():
    return {"message":"Primer blog TEST"}


# @app.post("/post/")
# def home():

@app.post("/posts", response_model=PostPublic,response_description="Post Creado con exito",status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate,db:Session=Depends(get_db)):
    author_obj=None
    
    if post.author:
        author_obj= db.execute(select(AuthorORM).where(AuthorORM.email == post.author.email)).scalar_one_or_none()
        
        if not author_obj:
            author_obj=AuthorORM(name=post.author.name,email=post.author.email)
            db.add(author_obj)
            db.flush()
    
    new_post=PostORM(title=post.title,content=post.content, author=author_obj)
    
    for tag in post.tags:
        tag_obj=db.execute(select(TagORM).where(TagORM.name==tag.name)).scalar_one_or_none()
        if not tag_obj:
            tag_obj= TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()
        new_post.tags.append(tag_obj)
        
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail='El titulo ya existe, prueba con otro')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Error al crear el post")
    
    
        